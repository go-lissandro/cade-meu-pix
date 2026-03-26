import httpx
from app.core.config import settings


class WhatsAppClient:
    def __init__(self):
        self.base_url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

    def send_text(self, phone: str, message: str) -> dict:
        """Envia mensagem de texto simples via Meta WABA API."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
            )
        if response.status_code != 200:
            raise RuntimeError(
                f"WhatsApp API error {response.status_code}: {response.text}"
            )
        return response.json()