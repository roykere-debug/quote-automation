from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Service:
    """Service details from Airtable services table"""
    name: str            # שם השירות
    whats_included: str  # מה כלול
    price: str           # מחיר


@dataclass
class Lead:
    """Lead record from Airtable leads table"""
    record_id: str
    name: str            # שם הליד
    summary: str         # סיכום חכם
    email: str           # אימייל
    next_step: str       # שלב הבא
    services: List[str]  # שירות מבוקש - list to support multiple services
    service_details: List[Service] = field(default_factory=list)
    doc_link: Optional[str] = None
