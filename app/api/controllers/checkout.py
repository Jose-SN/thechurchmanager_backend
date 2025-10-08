from fastapi import HTTPException

class CheckoutController:
    def __init__(self, service):
        self.service = service

    def get_checkout(self, checkout_id=None, submitted_by=None, user_id=None):
        result = self.service.get_checkout(checkout_id, submitted_by, user_id)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Checkout not found")

    def create_checkout(self, data):
        return self.service.save_checkout(data)

    def update_checkout(self, checkout_id, data):
        updated = self.service.update_checkout(checkout_id, data)
        if updated:
            return updated
        else:
            raise HTTPException(status_code=404, detail="Checkout not found")

    def delete_checkout(self, checkout_id):
        success = self.service.delete_checkout(checkout_id)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Checkout not found")
