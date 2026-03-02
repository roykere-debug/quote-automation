import io
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from utils.retry import api_retry

logger = logging.getLogger("quote_automation")


class GoogleDriveClient:
    """Handles Google Drive operations: export documents as PDF"""

    def __init__(self, credentials):
        self.service = build("drive", "v3", credentials=credentials)

    @api_retry
    def export_as_pdf(self, doc_id: str) -> bytes:
        """Downloads the Google Doc as PDF and returns raw bytes"""
        logger.debug(f"Exporting doc {doc_id} as PDF")

        request = self.service.files().export_media(
            fileId=doc_id,
            mimeType="application/pdf"
        )

        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False

        while not done:
            _, done = downloader.next_chunk()

        pdf_bytes = buffer.getvalue()
        logger.debug(f"PDF exported successfully. Size: {len(pdf_bytes)} bytes")
        return pdf_bytes
