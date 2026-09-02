from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WalletExpenseSummary(BaseModel):
    wallet_id: UUID
    wallet_name: str
    total: float


class CategoryExpenseSummary(BaseModel):
    category_id: UUID
    category_name: str
    total: float


class RecentExpense(BaseModel):
    uuid: UUID
    amount: float
    description: str | None
    expense_date: datetime


class DashboardResponse(BaseModel):
    total_wallet_balance: float
    daily_expenses: float
    weekly_expenses: float
    monthly_expenses: float
    wallet_wise_expenses: list[WalletExpenseSummary]
    category_wise_expenses: list[CategoryExpenseSummary]
    recent_expenses: list[RecentExpense]