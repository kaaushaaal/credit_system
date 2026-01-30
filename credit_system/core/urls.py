from django.urls import path
from .views import (
    RegisterCustomerAPIView,
    CheckEligibilityAPIView,
    CreateLoanAPIView,
    ViewLoanAPIView,
    ViewLoansByCustomerAPIView,
)

urlpatterns = [
    path("register", RegisterCustomerAPIView.as_view()),
    path("check-eligibility", CheckEligibilityAPIView.as_view()),
    path("create-loan", CreateLoanAPIView.as_view()),
    path("view-loan/<int:loan_id>", ViewLoanAPIView.as_view()),
    path("view-loans/<int:customer_id>", ViewLoansByCustomerAPIView.as_view()),
]
