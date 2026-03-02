import os
import time
import logging
import schedule
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from utils.logger import setup_logger
from services import (
    AirtableClient,
    GeminiClient,
    GoogleDocsClient,
    GoogleDriveClient,
    GmailClient,
)

# Setup logging first thing
logger = setup_logger()

# Load environment variables
load_dotenv()

# Google OAuth Scopes
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.send",
]


def get_google_credentials():
    """Handles OAuth2 token refresh/creation. Runs browser flow only on first run."""
    creds = None
    token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

    # Check if token file exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        logger.debug(f"Loaded credentials from {token_file}")

    # Refresh or create new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing Google credentials...")
            creds.refresh(Request())
        else:
            logger.info("Starting OAuth2 flow for Google authorization...")
            if not os.path.exists(creds_file):
                logger.error(f"Credentials file not found: {creds_file}")
                logger.error("Download credentials.json from Google Cloud Console and place it in this directory")
                raise FileNotFoundError(f"{creds_file} not found")

            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next time
        with open(token_file, "w") as f:
            f.write(creds.to_json())
        logger.info(f"Credentials saved to {token_file}")

    return creds


def process_lead(lead, airtable, gemini, docs, drive, gmail):
    """Full pipeline for a single lead. Each step is logged and errors are caught."""
    logger.info(f"▶ Processing lead: {lead.name} ({lead.record_id})")

    try:
        # 1. Fetch service details (supports multiple)
        logger.debug(f"  Fetching services: {lead.services}")
        lead.service_details = airtable.get_services_for_lead(lead.services)

        if not lead.service_details:
            logger.error(f"  ✗ No services found for lead {lead.name}: {lead.services}")
            return

        logger.debug(f"  ✓ Found {len(lead.service_details)} service(s)")

        # 2. Generate AI paragraph
        logger.info(f"  Calling Gemini API...")
        ai_paragraph = gemini.generate_paragraph(lead, lead.service_details)
        logger.debug(f"  ✓ Generated paragraph ({len(ai_paragraph)} chars)")

        # 3. Copy & fill Google Doc
        logger.info(f"  Copying Google Doc template...")
        template_id = os.getenv("GOOGLE_DOC_TEMPLATE_ID")
        doc_id = docs.copy_template(template_id, lead.name)
        logger.debug(f"  ✓ Template copied: {doc_id}")

        logger.info(f"  Filling document placeholders...")
        docs.fill_placeholders(doc_id, lead, ai_paragraph)
        doc_link = docs.get_doc_link(doc_id)
        lead.doc_link = doc_link
        logger.debug(f"  ✓ Placeholders filled")

        # 4. Export as PDF
        logger.info(f"  Exporting document to PDF...")
        pdf_bytes = drive.export_as_pdf(doc_id)
        logger.debug(f"  ✓ PDF exported ({len(pdf_bytes)} bytes)")

        # 5. Send email to lead
        logger.info(f"  Sending email to lead: {lead.email}")
        gmail.send_quote_to_lead(lead, pdf_bytes, doc_link)
        logger.debug(f"  ✓ Email sent")

        # 6. Update Airtable (status + doc link)
        logger.info(f"  Updating Airtable status...")
        airtable.mark_quote_sent(lead.record_id, doc_link)
        logger.debug(f"  ✓ Airtable updated")

        # 7. Notify Roy
        logger.info(f"  Sending notification to Roy...")
        roy_email = os.getenv("ROY_NOTIFICATION_EMAIL")
        gmail.send_roy_notification(lead, doc_link, roy_email)
        logger.debug(f"  ✓ Roy notified")

        logger.info(f"✓ Quote sent successfully for: {lead.name}")

    except Exception as e:
        logger.exception(f"✗ Failed to process lead {lead.name}: {e}")
        # Does NOT update Airtable on failure -> lead stays as "לשלוח הצעה"
        # so it will be retried on the next poll cycle


def run_poll_cycle(airtable, gemini, docs, drive, gmail):
    """Single polling cycle: fetch leads and process them"""
    logger.info("=" * 60)
    logger.info("POLL CYCLE STARTED")
    logger.info("=" * 60)

    try:
        leads = airtable.get_leads_to_quote()
        logger.info(f"Found {len(leads)} lead(s) to process")

        if len(leads) == 0:
            logger.info("No leads to process. Waiting for next cycle...")
        else:
            for i, lead in enumerate(leads, 1):
                logger.info(f"\n[{i}/{len(leads)}]")
                process_lead(lead, airtable, gemini, docs, drive, gmail)

    except Exception as e:
        logger.exception(f"Poll cycle failed: {e}")

    logger.info("=" * 60)
    logger.info("POLL CYCLE ENDED")
    logger.info("=" * 60)


def validate_env():
    """Validate that all required environment variables are set"""
    required = [
        "AIRTABLE_API_KEY",
        "AIRTABLE_BASE_ID",
        "AIRTABLE_LEADS_TABLE_ID",
        "AIRTABLE_SERVICES_TABLE_ID",
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "GOOGLE_DOC_TEMPLATE_ID",
        "GMAIL_SENDER",
        "ROY_NOTIFICATION_EMAIL",
    ]

    missing = [var for var in required if not os.getenv(var)]

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file and ensure all required variables are set")
        raise ValueError("Missing environment variables")

    logger.info("✓ All environment variables are set")


def main():
    """Main entry point - initialize clients and start polling"""
    logger.info("=" * 60)
    logger.info("Quote Automation System - Starting")
    logger.info("=" * 60)

    try:
        # Validate environment
        validate_env()

        # Get Google credentials
        logger.info("Initializing Google credentials...")
        creds = get_google_credentials()
        logger.info("✓ Google credentials loaded")

        # Initialize all clients
        logger.info("Initializing service clients...")
        airtable = AirtableClient(
            os.getenv("AIRTABLE_API_KEY"),
            os.getenv("AIRTABLE_BASE_ID"),
            os.getenv("AIRTABLE_LEADS_TABLE_ID"),
            os.getenv("AIRTABLE_SERVICES_TABLE_ID"),
        )
        gemini = GeminiClient(os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_MODEL"))
        docs = GoogleDocsClient(creds)
        drive = GoogleDriveClient(creds)
        gmail = GmailClient(creds, os.getenv("GMAIL_SENDER"))
        logger.info("✓ All service clients initialized")

        # Run once immediately on start
        logger.info("Running initial poll cycle...")
        run_poll_cycle(airtable, gemini, docs, drive, gmail)

        # Schedule recurring polls
        interval = int(os.getenv("POLL_INTERVAL_SECONDS", 60))
        logger.info(f"Scheduling poll every {interval} seconds")
        schedule.every(interval).seconds.do(
            run_poll_cycle, airtable, gemini, docs, drive, gmail
        )

        logger.info("✓ Quote Automation System is running")
        logger.info(f"Next check in {interval} seconds. Press Ctrl+C to stop.\n")

        # Main polling loop
        while True:
            schedule.run_pending()
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("\n\nShutdown requested by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
