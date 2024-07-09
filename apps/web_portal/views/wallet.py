from rest_framework import serializers
from apps.common.views.api import AppAPIView
from apps.access.models import User
from apps.payments.models.order import Order,Payment
from apps.purchase.models.cart import EcashAddToCart
from ...common.serializers import  AppReadOnlyModelSerializer

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["current_reward_points","total_reward_points","used_reward_points"]

class PaymentListSerializer(AppReadOnlyModelSerializer):

    class Meta:
        model = Payment
        fields = ["id", "razorpay_order_id", "status"]
        
class TransactionSerializer(serializers.ModelSerializer):
    payment = PaymentListSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Order
        fields = ["id", "cart_data", "payment","created"]
        
class WalletListAPIView(AppAPIView):
    def get(self, request, *args, **kwargs):
        user_details = self.get_user()
        wallet_serializer = WalletSerializer(user_details)
        wallet_data = wallet_serializer.data
        ecash_enabled_transactions = Order.objects.filter(created_by=user_details,cart_data__ecash_applied=True) # Filter orders where ecash was enabled
        transaction_serializer = TransactionSerializer(ecash_enabled_transactions,many=True)
        transaction_data = transaction_serializer.data
        data = {
            'wallet_details': wallet_data,
            'transaction_history': transaction_data
        }
        return self.send_response(data=data)


#Ecash is enabled/not    
class ECashEnabledorDisabledAPIView(AppAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        
        ecash_enabled = EcashAddToCart.objects.get_or_none(created_by=user, ecash=True)
        
        if ecash_enabled:
            ecash_enabled.delete()
            return self.send_response(data={"ecash": "ECASH_REMOVED"})
        else:
            created, _ = EcashAddToCart.objects.get_or_create(ecash=True, created_by=user)
            if created:
                return self.send_response(data={"ecash": "ECASH_APPLIED"})
            else:
                return self.send_response(data={"error": "Error occurred while applying ECASH"})   