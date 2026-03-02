import logging
from datetime import date
from googleapiclient.discovery import build
from models.lead import Lead
from utils.retry import api_retry

logger = logging.getLogger("quote_automation")


class GoogleDocsClient:
    """Handles Google Docs operations: copy template and fill placeholders"""

    def __init__(self, credentials):
        self.drive_service = build("drive", "v3", credentials=credentials)
        self.docs_service = build("docs", "v1", credentials=credentials)

    @api_retry
    def copy_template(self, template_id: str, lead_name: str) -> str:
        """Copies the template and returns the new document ID"""
        new_name = f"הצעת מחיר - {lead_name}"
        logger.debug(f"Copying template '{template_id}' to '{new_name}'")

        result = self.drive_service.files().copy(
            fileId=template_id,
            body={"name": new_name}
        ).execute()

        doc_id = result.get("id")
        logger.debug(f"Template copied successfully. New doc ID: {doc_id}")
        return doc_id

    @api_retry
    def fill_placeholders(self, doc_id: str, lead: Lead, ai_paragraph: str):
        """Replaces all three placeholders in the copied document"""
        today = date.today().strftime("%d/%m/%Y")  # Israeli date format

        logger.debug(f"Filling placeholders in doc {doc_id}")

        requests = [
            self._replace_request("{{שם הלקוח}}", lead.name),
            self._replace_request("{{תאריך ההצעה}}", today),
            self._replace_request("{{פרט כאן את האתגר שעלה בשיחה}}", ai_paragraph),
        ]

        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()

        logger.debug(f"Placeholders filled successfully for doc {doc_id}")

    def get_doc_link(self, doc_id: str) -> str:
        """Generates the sharable Google Doc link"""
        return f"https://docs.google.com/document/d/{doc_id}/edit"

    def _replace_request(self, find: str, replace: str) -> dict:
        """Creates a batchUpdate request for replaceAllText"""
        return {
            "replaceAllText": {
                "containsText": {"text": find, "matchCase": True},
                "replaceText": replace,
            }
        }
