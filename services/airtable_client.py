import logging
import os
from typing import List
from pyairtable import Api
from pyairtable.formulas import match, OR
from models.lead import Lead, Service
from utils.retry import api_retry

logger = logging.getLogger("quote_automation")


class AirtableClient:
    """Handles all Airtable operations"""

    def __init__(self, api_key: str, base_id: str, leads_table_id: str, services_table_id: str):
        self.api = Api(api_key)
        self.base_id = base_id
        self.leads_table_id = leads_table_id
        self.services_table_id = services_table_id
        self.leads_table = self.api.table(base_id, leads_table_id)
        self.services_table = self.api.table(base_id, services_table_id)

    @api_retry
    def get_leads_to_quote(self) -> List[Lead]:
        """Fetches all leads where שלב הבא = לשלוח הצעה"""
        trigger_field = os.getenv("FIELD_NEXT_STEP", "שלב הבא")
        trigger_value = os.getenv("FIELD_TRIGGER_VALUE", "לשלוח הצעה")

        # Use pyairtable's match helper for safe formula building
        formula = match({trigger_field: trigger_value})
        records = self.leads_table.all(formula=formula)

        leads = []
        for record in records:
            try:
                lead = self._parse_lead(record)
                leads.append(lead)
            except Exception as e:
                logger.error(f"Failed to parse lead record {record.get('id')}: {e}")
                continue

        return leads

    @api_retry
    def get_services_for_lead(self, service_names: List[str]) -> List[Service]:
        """
        Fetches ALL services for the given names using OR formula.
        Improvement over n8n: batch-fetches all services in one API call,
        instead of just taking the first one.
        """
        if not service_names:
            return []

        service_name_field = os.getenv("FIELD_SERVICE_NAME", "שם השירות")

        # Build OR formula: {שם השירות}='X' OR {שם השירות}='Y'
        conditions = [f"{{{service_name_field}}}='{name}'" for name in service_names]
        formula_str = f"OR({', '.join(conditions)})"

        records = self.services_table.all(formula=formula_str)

        services = []
        for record in records:
            try:
                service = self._parse_service(record)
                services.append(service)
            except Exception as e:
                logger.error(f"Failed to parse service record {record.get('id')}: {e}")
                continue

        return services

    @api_retry
    def mark_quote_sent(self, record_id: str, doc_link: str):
        """Updates שלב הבא to הצעה נשלחה and stores the Google Doc link"""
        done_field = os.getenv("FIELD_NEXT_STEP", "שלב הבא")
        done_value = os.getenv("FIELD_DONE_VALUE", "הצעה נשלחה")
        doc_link_field = os.getenv("FIELD_DOC_LINK", "קישור להצעה")

        self.leads_table.update(record_id, {
            done_field: done_value,
            doc_link_field: doc_link,
        })

    def _parse_lead(self, record: dict) -> Lead:
        """Converts an Airtable record dict into a Lead object"""
        fields = record.get("fields", {})

        name_field = os.getenv("FIELD_LEAD_NAME", "שם הליד")
        service_field = os.getenv("FIELD_SERVICE", "שירות מבוקש")
        email_field = os.getenv("FIELD_EMAIL", "אימייל")
        next_step_field = os.getenv("FIELD_NEXT_STEP", "שלב הבא")

        # Service field can be a list (Airtable multi-select) or a single string
        services_raw = fields.get(service_field, [])
        if isinstance(services_raw, str):
            services = [services_raw]
        else:
            services = services_raw if services_raw else []

        return Lead(
            record_id=record.get("id"),
            name=fields.get(name_field, ""),
            summary="",  # Not required anymore
            email=fields.get(email_field, ""),
            next_step=fields.get(next_step_field, ""),
            services=services,
        )

    def _parse_service(self, record: dict) -> Service:
        """Converts an Airtable record dict into a Service object"""
        fields = record.get("fields", {})

        name_field = os.getenv("FIELD_SERVICE_NAME", "שם השירות")
        included_field = os.getenv("FIELD_WHATS_INCLUDED", "מה כלול")
        price_field = os.getenv("FIELD_PRICE", "מחיר")

        return Service(
            name=fields.get(name_field, ""),
            whats_included=fields.get(included_field, ""),
            price=fields.get(price_field, ""),
        )
