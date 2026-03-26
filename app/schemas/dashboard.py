from decimal import Decimal
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_pending: int
    total_paid: int
    total_overdue: int
    total_partially_paid: int
    amount_to_receive: Decimal
    amount_received: Decimal
    charges_today: int