import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
from models.lead import Lead
from utils.retry import api_retry

logger = logging.getLogger("quote_automation")

# HTML email template for leads - RTL support
HTML_TEMPLATE = """<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; direction: rtl; color: #222; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; }}
        .content {{ margin-bottom: 20px; }}
        .signature {{ margin-top: 30px; font-weight: bold; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <p>היי {name},</p>
        </div>
        <div class="content">
            <p>תודה רבה על השיחה שלנו! היה לי תענוג להכיר.</p>
            <p>מצורפת הצעת המחיר המסודרת שסיכמנו עליה בקובץ PDF.</p>
            <p>
                ניתן גם לצפות בה ישירות דרך הקישור:<br>
                <a href="{doc_link}" target="_blank">לחץ כאן לצפייה בהצעת המחיר</a>
            </p>
        </div>
        <div class="signature">
            <p>אני זמין כאן לכל שאלה,</p>
            <p>רוי קרן</p>
        </div>
    </div>
</body>
</html>
"""

# Notification template for Roy
ROY_NOTIFICATION_TEMPLATE = """הצעת מחיר נשלחה בהצלחה!

פרטי הליד:
- שם: {name}
- אימייל: {email}
- שירותים: {services}

קישור למסמך: {doc_link}

---
זה הודעה אוטומטית מ-Quote Automation System
"""


class GmailClient:
    """Handles Gmail operations: send emails to leads and notifications"""

    def __init__(self, credentials, sender_email: str):
        self.service = build("gmail", "v1", credentials=credentials)
        self.sender = sender_email

    @api_retry
    def send_quote_to_lead(self, lead: Lead, pdf_bytes: bytes, doc_link: str):
        """Sends HTML email with PDF attachment to the lead"""
        logger.debug(f"Composing email for lead: {lead.email}")

        msg = MIMEMultipart("mixed")
        msg["To"] = lead.email
        msg["From"] = self.sender
        msg["Subject"] = f"הצעת המחיר שלך מרוי קרן - {lead.name}"

        # Attach HTML body
        html_body = HTML_TEMPLATE.format(name=lead.name, doc_link=doc_link)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Attach PDF
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_part.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"הצעת מחיר - {lead.name}.pdf"
        )
        msg.attach(pdf_part)

        self._send_message(msg)
        logger.info(f"Email sent to lead: {lead.email}")

    @api_retry
    def send_roy_notification(self, lead: Lead, doc_link: str, roy_email: str):
        """Sends a summary notification to Roy after each quote is dispatched"""
        logger.debug(f"Composing notification for Roy")

        services_str = ", ".join([s.name for s in lead.service_details])
        body = ROY_NOTIFICATION_TEMPLATE.format(
            name=lead.name,
            email=lead.email,
            services=services_str,
            doc_link=doc_link,
        )

        msg = MIMEText(body, "plain", "utf-8")
        msg["To"] = roy_email
        msg["From"] = self.sender
        msg["Subject"] = f"[אוטומציה] הצעת מחיר נשלחה - {lead.name}"

        self._send_message(msg)
        logger.info(f"Notification sent to Roy: {roy_email}")

    def _send_message(self, msg: MIMEMultipart):
        """Encodes and sends a MIME message via Gmail API"""
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        self.service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()
