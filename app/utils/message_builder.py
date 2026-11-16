from html import escape

from app.models.charge import Charge


def build_whatsapp_message(charge: Charge) -> str:
    valor = f"R$ {charge.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    vencimento = charge.due_date.strftime("%d/%m/%Y")
    return (
        f"Olá, *{charge.client.name}*! 👋\n\n"
        f"Você possui uma cobrança em aberto:\n\n"
        f"📋 *Descrição:* {charge.description}\n"
        f"💰 *Valor:* {valor}\n"
        f"📅 *Vencimento:* {vencimento}\n\n"
        f"Em caso de dúvidas, entre em contato conosco."
    )


def build_email_html(charge: Charge) -> str:
    valor = f"R$ {charge.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    vencimento = charge.due_date.strftime("%d/%m/%Y")
    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
      <h2>Lembrete de cobrança</h2>
      <p>Olá, <strong>{escape(charge.client.name)}</strong>!</p>
      <p>Você possui uma cobrança em aberto:</p>
      <table style="border-collapse:collapse;width:100%">
        <tr><td style="padding:8px;border:1px solid #ddd"><strong>Descrição</strong></td>
            <td style="padding:8px;border:1px solid #ddd">{escape(charge.description)}</td></tr>
        <tr><td style="padding:8px;border:1px solid #ddd"><strong>Valor</strong></td>
            <td style="padding:8px;border:1px solid #ddd">{valor}</td></tr>
        <tr><td style="padding:8px;border:1px solid #ddd"><strong>Vencimento</strong></td>
            <td style="padding:8px;border:1px solid #ddd">{vencimento}</td></tr>
      </table>
    </body></html>
    """