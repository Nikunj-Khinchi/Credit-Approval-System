from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    age = models.IntegerField()


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    emi_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    repayments_left = models.IntegerField()
