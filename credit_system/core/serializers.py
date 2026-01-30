from rest_framework import serializers


class RegisterCustomerRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    age = serializers.IntegerField()
    monthly_income = serializers.IntegerField()
    phone_number = serializers.IntegerField()


class RegisterCustomerResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    name = serializers.CharField()
    age = serializers.IntegerField()
    monthly_income = serializers.IntegerField()
    approved_limit = serializers.IntegerField()
    phone_number = serializers.IntegerField()

class CheckEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class CheckEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()

class CreateLoanRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()

class ViewLoanSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    monthly_installment = serializers.FloatField()
    tenure = serializers.IntegerField()


class ViewLoansSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    monthly_installment = serializers.FloatField()
    tenure = serializers.IntegerField()
