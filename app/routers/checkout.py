from fastapi import APIRouter, Depends
from .schemas import CheckoutSchema
from .service import CheckoutService
from .event import CheckoutController

router = APIRouter()
service = CheckoutService()
controller = CheckoutController(service)

@router.get("/get")
def get_checkout(checkout_id: str = None, submitted_by: str = None, user_id: str = None):
    return controller.get_checkout(checkout_id, submitted_by, user_id)

@router.post("/save")
def save_checkout(data: CheckoutSchema):
    return controller.create_checkout(data.dict())

@router.put("/update/{checkout_id}")
def update_checkout(checkout_id: str, data: CheckoutSchema):
    return controller.update_checkout(checkout_id, data.dict())

@router.delete("/delete/{checkout_id}")
def delete_checkout(checkout_id: str):
    return controller.delete_checkout(checkout_id)
