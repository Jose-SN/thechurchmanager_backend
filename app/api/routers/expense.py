from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.expense import ExpenseController
from app.api.services.expense import ExpenseService
from app.api.dependencies import get_db

expense_router = APIRouter(tags=["Expense"])


def get_expense_service(db=Depends(get_db)):
    return ExpenseService(db)


def get_expense_controller(expense_service=Depends(get_expense_service)):
    return ExpenseController(expense_service)


@expense_router.get("/get")
async def get_expenses(
    expense_controller: ExpenseController = Depends(get_expense_controller),
    id: Optional[int] = Query(None, description="Expense ID"),
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    team_id: Optional[str] = Query(None, description="Team ID"),
    expense_date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    title: Optional[str] = Query(None, description="Search by title"),
):
    """Get expenses with optional filters."""
    filters = {}
    if id is not None:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    if team_id:
        filters["team_id"] = team_id
    if expense_date:
        filters["expense_date"] = expense_date
    if category:
        filters["category"] = category
    if title:
        filters["title"] = title
    return await expense_controller.fetch_expense_controller(filters)


@expense_router.post("/bulk-save")
async def save_bulk_expense(
    request: Request,
    expense_controller: ExpenseController = Depends(get_expense_controller)
):
    """
    Create multiple expenses at once.
    Request body: { "expenses": [{ "title": "...", "amount": 20, ... }, ...] }
    Or pass array directly: [{ "title": "...", "amount": 20, ... }, ...]
    """
    return await expense_controller.save_bulk_expense_controller(request)


@expense_router.get("/{expense_id}")
async def get_expense_by_id(
    expense_id: int,
    expense_controller: ExpenseController = Depends(get_expense_controller)
):
    """Get a single expense by ID"""
    return await expense_controller.get_expense_by_id_controller(expense_id)


@expense_router.post("/save")
async def save_expense(
    request: Request,
    expense_controller: ExpenseController = Depends(get_expense_controller)
):
    """
    Create a new expense.
    Request body: { "title": "Bottles", "amount": 20, "category": "Food", "expense_date": "2026-02-27", "organization_id": "...", "team_id": "...", "description": "" }
    """
    return await expense_controller.save_expense_controller(request)


@expense_router.put("/update/{expense_id}")
async def update_expense(
    expense_id: int,
    request: Request,
    expense_controller: ExpenseController = Depends(get_expense_controller)
):
    """Update an existing expense. Request body must include organization_id."""
    return await expense_controller.update_expense_controller(expense_id, request)


@expense_router.delete("/delete/{expense_id}")
async def delete_expense(
    expense_id: int,
    expense_controller: ExpenseController = Depends(get_expense_controller),
    organization_id: str = Query(..., description="Organization ID for authorization")
):
    """Delete an expense. Requires organization_id query parameter."""
    return await expense_controller.delete_expense_controller(expense_id, organization_id)
