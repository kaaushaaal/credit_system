import os
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from core.models import Customer, Loan

class Command(BaseCommand):
    help = "Ingest customer and loan data from Excel files"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting data ingestion...")

        self.ingest_customers()
        self.ingest_loans()
        self.reset_customer_id_sequence()
        self.stdout.write(self.style.SUCCESS("Data ingestion completed."))

    def ingest_customers(self):
        customer_file = os.path.join(
        settings.BASE_DIR.parent,
        "data_files",
        "customer_data.xlsx"
     )
        df = pd.read_excel(customer_file)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        for _, row in df.iterrows():
            Customer.objects.get_or_create(
                id=int(row["customer_id"]),
                defaults={
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "age": int(row["age"]),
                    "phone_number": str(row["phone_number"]),
                    "monthly_salary": int(row["monthly_salary"]),
                    "approved_limit": int(row["approved_limit"]),
                    "current_debt": 0,   # ← correct default
                }
            )

    def ingest_loans(self):
        loan_file = os.path.abspath(
            os.path.join(settings.BASE_DIR, "..", "data_files", "loan_data.xlsx")
        )

        df = pd.read_excel(loan_file)

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        for _, row in df.iterrows():
            customer = Customer.objects.get(id=int(row["customer_id"]))

            Loan.objects.get_or_create(
                id=int(row["loan_id"]),
                defaults={
                    "customer": customer,
                    "loan_amount": float(row["loan_amount"]),
                    "interest_rate": float(row["interest_rate"]),
                    "tenure": int(row["tenure"]),
                    "monthly_installment": float(row["monthly_payment"]),
                    "emis_paid_on_time": int(row["emis_paid_on_time"]),
                    "start_date": pd.to_datetime(row["date_of_approval"]).date(),
                    "end_date": pd.to_datetime(row["end_date"]).date(),
                }
            )

        self.stdout.write("Loans ingested.")

        
    def reset_customer_id_sequence(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT setval(
                    pg_get_serial_sequence('core_customer', 'id'),
                    COALESCE((SELECT MAX(id) FROM core_customer), 1)
                );
            """)
