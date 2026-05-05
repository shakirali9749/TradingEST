from django import forms

from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "name",
            "salary_type",
            "monthly_salary",
            "daily_rate",
            "days_worked",
            "salary_paid_this_month",
            "advance_taken",
            "advance_adjusted",
            "previous_pending_salary",
            "note",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "salary_type": forms.Select(attrs={"class": "form-select"}),
            "monthly_salary": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "daily_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "days_worked": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "salary_paid_this_month": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "advance_taken": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "advance_adjusted": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "previous_pending_salary": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
