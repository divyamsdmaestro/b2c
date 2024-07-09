import razorpay
from django.conf import settings


def get_razorpay_client():
    """Returns the razorpay client."""

    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def is_razorpay_payment_order_successful(order_id):
    """
    Returns if the razorpay payment order is successful or not. Payment order
    is basically the wrapper class which denote the amount to be paid.
    """

    order_response = get_razorpay_client().order.fetch(order_id=order_id)
    return order_response.get("status") in ["paid"]


def get_razorpay_payment_order(amount, currency, receipt):
    """
    The payment order is the first object to be created before even triggering
    the payment from the mobile app.

    Ref: https://razorpay.com/docs/payment-gateway/server-integration/python/#step-2-integrate-orders-api
    """

    return get_razorpay_client().order.create(
        data={
            "amount": int(amount * 100),  # should be 50000 if 500 is the actual amount
            "currency": currency,
            "receipt": receipt,
        }
    )


def verify_razorpay_payment_completion(**kwargs):
    """
    Validates a given razorpay completed payment and send back.
    Necessary data to save to the tracker.
    """

    client = get_razorpay_client()
    razorpay_order_id = kwargs.get("razorpay_order_id")
    razorpay_payment_id = kwargs.get("razorpay_payment_id")
    razorpay_signature = kwargs.get("razorpay_signature")

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }
    client.utility.verify_payment_signature(params_dict)

    return {
        "razorpay_completed_payment_id": razorpay_payment_id,
        "razorpay_completed_order_id": razorpay_order_id,
        "razorpay_completed_signature": razorpay_signature,
    }


def to_int(input_value, fallback_value=None):
    """Centralized function to handle int conversions."""

    try:
        return int(input_value)
    except:  # noqa
        return fallback_value


def divide(numerator, denominator, fallback_value=None):
    """Central function to divied. Handles exceptions."""

    try:
        return numerator / denominator
    except:  # noqa
        return fallback_value
