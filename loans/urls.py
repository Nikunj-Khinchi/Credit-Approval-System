from django.urls import path
from .views import RegisterCustomer, CheckEligibility, CreateLoan, health_check, ViewLoan, ViewLoans

urlpatterns = [
      path('health/', health_check, name='health_check'),
    path('register/', RegisterCustomer.as_view(), name='register'),
    path('check-eligibility/', CheckEligibility.as_view(), name='check_eligibility'),
    path('create-loan/', CreateLoan.as_view(), name='create_loan'),
    path('view-loans/<int:customer_id>/', ViewLoans.as_view(), name='view_loans'),
    path('view-loan/<int:loan_id>/', ViewLoan.as_view(), name='view_loan'),
]
