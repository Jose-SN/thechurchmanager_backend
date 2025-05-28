from .models import Checkout

class CheckoutService:
    def get_checkout(self, checkout_id=None, submitted_by=None, user_id=None):
        if checkout_id:
            return Checkout.objects(id=checkout_id).first()
        elif submitted_by:
            return Checkout.objects(submitted_by=submitted_by)
        elif user_id:
            return Checkout.objects(user_id=user_id)
        else:
            return Checkout.objects()

    def save_checkout(self, data):
        checkout = Checkout(**data)
        checkout.save()
        return checkout

    def update_checkout(self, checkout_id, data):
        checkout = Checkout.objects(id=checkout_id).first()
        if checkout:
            checkout.update(**data)
            return Checkout.objects(id=checkout_id).first()
        else:
            return None

    def delete_checkout(self, checkout_id):
        checkout = Checkout.objects(id=checkout_id).first()
        if checkout:
            checkout.delete()
            return True
        else:
            return False
