import math
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from .serializers import ViewLoanSerializer, ViewLoansSerializer

from .serializers import (
    CreateLoanRequestSerializer,
    CreateLoanResponseSerializer,
)

from .models import Loan
from .models import Customer

from .serializers import (
    CheckEligibilityRequestSerializer,
    CheckEligibilityResponseSerializer,
    RegisterCustomerRequestSerializer,
    RegisterCustomerResponseSerializer,
)

class RegisterCustomerAPIView(APIView):
    def post(self, request):
        serializer = RegisterCustomerRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        monthly_income = data["monthly_income"]

        # PDF rule: approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        approved_limit = round((36 * monthly_income) / 100000) * 100000

        customer = Customer.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            phone_number=str(data["phone_number"]),
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            current_debt=0,
        )

        response_data = {
            "customer_id": customer.id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": monthly_income,
            "approved_limit": approved_limit,
            "phone_number": customer.phone_number,
        }

        response_serializer = RegisterCustomerResponseSerializer(response_data)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
    
class CheckEligibilityAPIView(APIView):
    def post(self, request):
        serializer = CheckEligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer_id = data["customer_id"]
        loan_amount = data["loan_amount"]
        interest_rate = data["interest_rate"]
        tenure = data["tenure"]

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        loans = customer.loans.all()

        # Hard rule 1: total loan amount > approved limit
        total_loan_amount = sum(l.loan_amount for l in loans)
        if total_loan_amount > customer.approved_limit:
            credit_score = 0
        else:
            credit_score = 100

            # Past loans count
            credit_score -= len(loans) * 2

            # Loans not paid on time
            for loan in loans:
                if loan.emis_paid_on_time < loan.tenure:
                    credit_score -= 5

            # Loans in current year
            current_year = date.today().year
            for loan in loans:
                if loan.start_date.year == current_year:
                    credit_score -= 5

            credit_score = max(0, credit_score)

        # Hard rule 2: total EMIs > 50% salary
        total_monthly_emi = sum(l.monthly_installment for l in loans)
        if total_monthly_emi > 0.5 * customer.monthly_salary:
            return Response(
                {
                    "customer_id": customer_id,
                    "approval": False,
                    "interest_rate": interest_rate,
                    "corrected_interest_rate": interest_rate,
                    "tenure": tenure,
                    "monthly_installment": 0,
                }
            )

        # Determine approval & corrected interest
        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            corrected_interest_rate = max(interest_rate, 12)
            approval = True
        elif 10 < credit_score <= 30:
            corrected_interest_rate = max(interest_rate, 16)
            approval = True
        else:
            approval = False

        # Monthly installment (compound interest)
        r = corrected_interest_rate / (12 * 100)
        n = tenure
        monthly_installment = (
            loan_amount * r * math.pow(1 + r, n)
        ) / (math.pow(1 + r, n) - 1)

        response_data = {
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(monthly_installment, 2),
        }

        response_serializer = CheckEligibilityResponseSerializer(response_data)
        return Response(response_serializer.data)

def evaluate_loan_eligibility(customer, loan_amount, interest_rate, tenure):
    loans = customer.loans.all()

    # Hard rule: total loan amount > approved limit
    total_loan_amount = sum(l.loan_amount for l in loans)
    if total_loan_amount > customer.approved_limit:
        credit_score = 0
    else:
        credit_score = 100
        credit_score -= len(loans) * 2

        for loan in loans:
            if loan.emis_paid_on_time < loan.tenure:
                credit_score -= 5

        current_year = date.today().year
        for loan in loans:
            if loan.start_date.year == current_year:
                credit_score -= 5

        credit_score = max(0, credit_score)

    # Hard rule: EMI burden
    total_monthly_emi = sum(l.monthly_installment for l in loans)
    if total_monthly_emi > 0.5 * customer.monthly_salary:
        return False, interest_rate, 0

    approval = False
    corrected_interest_rate = interest_rate

    if credit_score > 50:
        approval = True
    elif 30 < credit_score <= 50:
        corrected_interest_rate = max(interest_rate, 12)
        approval = True
    elif 10 < credit_score <= 30:
        corrected_interest_rate = max(interest_rate, 16)
        approval = True
    else:
        approval = False

    if not approval:
        return False, corrected_interest_rate, 0

    r = corrected_interest_rate / (12 * 100)
    n = tenure
    emi = (loan_amount * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)

    return True, corrected_interest_rate, round(emi, 2)

class CreateLoanAPIView(APIView):
    def post(self, request):
        serializer = CreateLoanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            customer = Customer.objects.get(id=data["customer_id"])
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        approval, corrected_interest_rate, emi = evaluate_loan_eligibility(
            customer,
            data["loan_amount"],
            data["interest_rate"],
            data["tenure"],
        )

        loan = None
        if approval:
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=data["loan_amount"],
                interest_rate=corrected_interest_rate,
                tenure=data["tenure"],
                monthly_installment=emi,
                emis_paid_on_time=0,
                start_date=date.today(),
                end_date=date.today().replace(year=date.today().year + data["tenure"] // 12),
            )

        response_data = {
            "loan_id": loan.id if loan else None,
            "customer_id": customer.id,
            "approval": approval,
            "interest_rate": data["interest_rate"],
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": data["tenure"],
            "monthly_installment": emi,
        }

        response_serializer = CreateLoanResponseSerializer(response_data)
        return Response(response_serializer.data)

class ViewLoanAPIView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {"error": "Loan not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = {
            "loan_id": loan.id,
            "customer_id": loan.customer.id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure,
        }

        serializer = ViewLoanSerializer(data)
        return Response(serializer.data)

class ViewLoansByCustomerAPIView(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer_id=customer_id)

        if not loans.exists():
            return Response([], status=status.HTTP_200_OK)

        data = []
        for loan in loans:
            data.append({
                "loan_id": loan.id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "tenure": loan.tenure,
            })

        serializer = ViewLoansSerializer(data, many=True)
        return Response(serializer.data)
