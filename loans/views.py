from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.decorators import api_view
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


# Helper Function
def calculate_monthly_installment(principal, interest_rate, tenure):
    R = interest_rate / (12 * 100)
    N = tenure * 12
    EMI = principal * R * (1 + R) ** N / ((1 + R) ** N - 1)
    return round(EMI, 2)

class RegisterCustomer(APIView):
    def post(self, request):
        try:
            data = request.data
            data['approved_limit'] = int(round(36 * data['monthly_salary'] / 1e5) * 1e5)
            serializer = CustomerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CheckEligibility(APIView):
    def post(self, request):
        try:
            customer_id = request.data.get('customer_id')
            loan_amount = request.data.get('loan_amount')
            interest_rate = request.data.get('interest_rate')
            tenure = request.data.get('tenure')

            customer = Customer.objects.get(customer_id=customer_id)
            if customer.approved_limit < loan_amount:
                return Response({"error": "Insufficient approved limit"}, status=status.HTTP_400_BAD_REQUEST)

            # Query historical loan data from the database
            customer_loans = Loan.objects.filter(customer_id=customer_id)

            # Check if the customer is new (no historical loan data)
            if not customer_loans.exists():
                credit_score = 50  # Assign a default credit score for new users
            else:
                # Calculate credit score
                past_loans_paid_on_time = customer_loans.filter(emi_paid_on_time=True).count()
                no_of_loans_taken = customer_loans.count()
                loan_activity_current_year = customer_loans.filter(start_date__year=date.today().year).count()
                loan_approved_volume = customer_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
                current_loans_sum = customer_loans.filter(emi_paid_on_time=False).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0

                if current_loans_sum > customer.approved_limit:
                    credit_score = 0
                else:
                    credit_score = (past_loans_paid_on_time * 0.4 +
                                    no_of_loans_taken * 0.2 +
                                    loan_activity_current_year * 0.2 +
                                    loan_approved_volume * 0.2)

            # Approval Logic
            if credit_score > 50:
                approval = True
            elif 30 < credit_score <= 50:
                approval = True
                if interest_rate < 12:
                    interest_rate = 12
            elif 10 < credit_score <= 30:
                approval = True
                if interest_rate < 16:
                    interest_rate = 16
            else:
                approval = False

            # Check if sum of all current EMIs > 50% of monthly salary
            total_emis = customer_loans.filter(emi_paid_on_time=False).aggregate(Sum('monthly_installment'))['monthly_installment__sum'] or 0
            if total_emis > 0.5 * customer.monthly_salary:
                approval = False

            monthly_installment = calculate_monthly_installment(
                loan_amount, interest_rate, tenure
            )

            return Response(
                {
                    "approval": approval,
                    "corrected_interest_rate": interest_rate,
                    "monthly_installment": monthly_installment,
                },
                status=status.HTTP_200_OK,
            )
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
        
class CreateLoan(APIView):
    def post(self, request):
        try:
            eligibility_response = CheckEligibility().post(request).data
            if not eligibility_response["approval"]:
                return Response(
                    {"message": "Loan not approved", "details": eligibility_response},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            loan_data = {
                "customer": Customer.objects.get(customer_id=request.data["customer_id"]),
                "loan_amount": request.data["loan_amount"],
                "tenure": request.data["tenure"],
                "interest_rate": eligibility_response["corrected_interest_rate"],
                "monthly_installment": eligibility_response["monthly_installment"],
                "emi_paid_on_time": 0,
                "start_date": date.today(),
                "end_date": date.today() + relativedelta(months=request.data["tenure"]),
                "repayments_left": request.data["tenure"] * 12,
            }
            loan = Loan.objects.create(**loan_data)
            return Response(
                {"loan_id": loan.loan_id, "message": "Loan approved"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ViewLoans(APIView):
    """
    Retrieve all loans associated with a specific customer.
    """
    def get(self, request, customer_id):
        try:
            customer = get_object_or_404(Customer, customer_id=customer_id)
            loans = Loan.objects.filter(customer=customer)
            serializer = LoanSerializer(loans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ViewLoan(APIView):
    """
    Retrieve details of a specific loan.
    """
    def get(self, request, loan_id):
        try:
            loan = get_object_or_404(Loan, loan_id=loan_id)
            serializer = LoanSerializer(loan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
