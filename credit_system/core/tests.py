from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Customer, Loan
from datetime import date

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            phone_number="9999999999",
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0,
        )

    def test_register_customer(self):
        response = self.client.post(
            "/api/register",
            {
                "first_name": "New",
                "last_name": "Customer",
                "age": 28,
                "phone_number": "8888888888",
                "monthly_income": 40000,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("customer_id", response.data)

    def test_check_eligibility(self):
        response = self.client.post(
            "/api/check-eligibility",
            {
                "customer_id": self.customer.id,
                "loan_amount": 100000,
                "interest_rate": 10,
                "tenure": 12,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("approval", response.data)

    def test_create_loan(self):
        response = self.client.post(
            "/api/create-loan",
            {
                "customer_id": self.customer.id,
                "loan_amount": 100000,
                "interest_rate": 10,
                "tenure": 12,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("approval", response.data)

    def test_view_loan(self):
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=50000,
            interest_rate=10,
            tenure=12,
            monthly_installment=4400,
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today(),
        )

        response = self.client.get(f"/api/view-loan/{loan.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["loan_id"], loan.id)

    def test_view_loans_by_customer(self):
        response = self.client.get(f"/api/view-loans/{self.customer.id}")
        self.assertEqual(response.status_code, 200)


