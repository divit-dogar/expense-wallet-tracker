from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.wallets import router as wallet_router
from app.api.expense_categories import router as expense_category_router
from app.api.expenses import router as expenses_router
from app.api.dashboard import router as dashboard_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(expense_category_router)
app.include_router(expenses_router)
app.include_router(dashboard_router)