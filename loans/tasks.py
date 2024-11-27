from celery import shared_task
import pandas as pd
from .models import Customer, Loan

@shared_task
def ingest_data():
    # Read data from Excel files
    customer_df = pd.read_excel('customer_data.xlsx')
    loan_df = pd.read_excel('loan_data.xlsx')

    # Standardize column names
    customer_df.columns = customer_df.columns.str.strip().str.lower().str.replace(' ', '_')
    loan_df.columns = loan_df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Parse date columns in the loan dataset
    loan_df['date_of_approval'] = pd.to_datetime(loan_df['date_of_approval'], errors='coerce')
    loan_df['end_date'] = pd.to_datetime(loan_df['end_date'], errors='coerce')

    # Bulk insert for customers
    customer_objects = [
        Customer(
            # customer_id=row['customer_id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone_number=row['phone_number'],
            monthly_salary=row['monthly_salary'],
            approved_limit=row['approved_limit'],
            age=row['age'],
        )
        for _, row in customer_df.iterrows()
    ]
    Customer.objects.bulk_create(customer_objects)

    # Bulk insert for loans
    loan_objects = [
        Loan(
            # loan_id=row['loan_id'],
            customer_id=row['customer_id'],
            loan_amount=row['loan_amount'],
            tenure=row['tenure'],
            interest_rate=row['interest_rate'],
            monthly_installment=row['monthly_payment'],
            emi_paid_on_time=row['emis_paid_on_time'],
            start_date=row['date_of_approval'],
            end_date=row['end_date'],
            repayments_left=row['tenure'] * 12,
        )
        for _, row in loan_df.iterrows()
    ]
    Loan.objects.bulk_create(loan_objects)
