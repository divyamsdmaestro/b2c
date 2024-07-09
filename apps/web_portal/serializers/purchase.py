from apps.common.serializers import AppReadOnlyModelSerializer
from ...payments.models import Order, Payment

class PaymentListSerializer(AppReadOnlyModelSerializer):

    class Meta:
        model = Payment
        fields = ["id", "razorpay_order_id", "status"]

class TransactionHistoryListSerializer(AppReadOnlyModelSerializer):
    """ Serializer to Handle Transaction History """
    payment = PaymentListSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Order
        fields = ["id", "cart_data", "total_price_after_discount", "payment", "created"]