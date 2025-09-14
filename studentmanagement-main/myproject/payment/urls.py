# payment/urls.py

from django.urls import path
from .views import PaymentSelectView, RazorpayCallbackView, AdminCashApprovalView

urlpatterns = [
    path("select/", PaymentSelectView.as_view(), name="payment-select"),
    path("razorpay/callback/", RazorpayCallbackView.as_view(), name="razorpay-callback"),
    path("payments-admin/", AdminCashApprovalView.as_view(), name="payment-admin"),
    path("payments-admin/<int:pk>/", AdminCashApprovalView.as_view(), name="payment-admin-action"),
]



