import logging
from typing import List
import google.generativeai as genai
from models.lead import Lead, Service
from utils.retry import api_retry

logger = logging.getLogger("quote_automation")


class GeminiClient:
    """Generates personalized paragraphs using Google Gemini"""

    def __init__(self, api_key: str, model: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model

    @api_retry
    def generate_paragraph(self, lead: Lead, services: List[Service]) -> str:
        """
        Generates a personalized paragraph for the quote.
        Improvement over n8n: when there are multiple services,
        all service details are included in the prompt, not just the first one.
        """
        services_text = "\n".join([
            f"- שירות: {s.name} | כולל: {s.whats_included} | מחיר: {s.price}"
            for s in services
        ])

        prompt = f"""אתה מנהל מכירות מומחה של רוי קרן.

שלב 1 - קרא את הנתונים הבאים:
שם הלקוח: {lead.name}
סיכום מהשיחה: {lead.summary}
שירותים מבוקשים:
{services_text}

שלב 2 - הבקשה:
נסח פסקה אישית במקצועיות רבה של 'שותף להצלחה' (RTL), שתשובץ בתוך מסמך הצעת מחיר.
תסביר בפסקה איך השירותים שלנו יפתרו את האתגר של הלקוח לפי סיכום השיחה,
תוך ציון אלגנטי של השירותים, מה כלול, והמחירים.

חוקים:
1. בלי כותרות או הקדמות.
2. בלי Markdown (בלי כוכביות, בלי סולמות).
החזר אך ורק את הפסקה ברצף אחד שמוכנה להעתקה למסמך."""

        logger.debug(f"Calling Gemini ({self.model_name}) for lead: {lead.name}")
        response = self.model.generate_content(prompt)
        return response.text.strip()
