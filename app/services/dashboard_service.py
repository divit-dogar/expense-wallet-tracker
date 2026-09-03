from datetime import datetime, timedelta, timezone

from app.repositories.dashboard import DashboardRepository


class DashboardService:

    def __init__(self, db):
        self.repository = DashboardRepository(db)

    async def get_dashboard(
        self,
        user_id: int,
    ):

        now = datetime.now(timezone.utc)

        # Start of today
        start_of_day = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        # Start of current week
        start_of_week = start_of_day - timedelta(
            days=start_of_day.weekday()
        )

        # Start of current month
        start_of_month = start_of_day.replace(
            day=1
        )

        # Total wallet balance
        total_wallet_balance = (
            await self.repository.get_total_wallet_balance(
                user_id
            )
        )

        # Daily expenses
        daily_expenses = (
            await self.repository.get_expense_total(
                user_id,
                start_of_day,
                now,
            )
        )

        # Weekly expenses
        weekly_expenses = (
            await self.repository.get_expense_total(
                user_id,
                start_of_week,
                now,
            )
        )

        # Monthly expenses
        monthly_expenses = (
            await self.repository.get_expense_total(
                user_id,
                start_of_month,
                now,
            )
        )

        # Wallet-wise expenses
        wallet_rows = (
            await self.repository.get_wallet_wise_expenses(
                user_id,
                start_of_month,
                now,
            )
        )

        wallet_wise_expenses = [
            {
                "wallet_id": row[0],
                "wallet_name": row[1],
                "total": float(row[2]),
            }
            for row in wallet_rows
        ]

        # Category-wise expenses
        category_rows = (
            await self.repository.get_category_wise_expenses(
                user_id,
                start_of_month,
                now,
            )
        )

        category_wise_expenses = [
            {
                "category_id": row[0],
                "category_name": row[1],
                "total": float(row[2]),
            }
            for row in category_rows
        ]

        # Recent expenses
        recent_expenses = (
            await self.repository.get_recent_expenses(
                user_id
            )
        )

        recent_expenses_data = [
            {
                "uuid": expense.uuid,
                "amount": float(expense.amount),
                "description": expense.description,
                "expense_date": expense.expense_date,
            }
            for expense in recent_expenses
        ]

        return {
            "total_wallet_balance": total_wallet_balance,
            "daily_expenses": daily_expenses,
            "weekly_expenses": weekly_expenses,
            "monthly_expenses": monthly_expenses,
            "wallet_wise_expenses": wallet_wise_expenses,
            "category_wise_expenses": category_wise_expenses,
            "recent_expenses": recent_expenses_data,
        }
    