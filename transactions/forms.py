from decimal import Decimal

from django import forms

from .models import LegacyPayable, Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "date",
            "description",
            "flow_type",
            "amount_excl_vat",
            "account",
            "category",
            "project",
            "material_item",
            "qty",
            "rate",
            "party_name",
            "party_type",
            "invoice_number",
            "tax_percent",
            "payment_status",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "flow_type": forms.Select(attrs={"class": "form-select"}),
            "amount_excl_vat": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "account": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "material_item": forms.TextInput(attrs={"class": "form-control"}),
            "qty": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "rate": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "party_name": forms.TextInput(attrs={"class": "form-control"}),
            "party_type": forms.Select(attrs={"class": "form-select"}),
            "invoice_number": forms.TextInput(attrs={"class": "form-control"}),
            "tax_percent": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "payment_status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_status"].required = True
        self.fields["amount_excl_vat"].required = True
        self.fields["party_type"].required = False
        self.fields["party_type"].empty_label = "—"
        self.fields["project"].required = False
        self.fields["project"].empty_label = "—"

    def clean(self):
        cleaned = super().clean()
        amt = cleaned.get("amount_excl_vat")
        if amt is None:
            self.add_error("amount_excl_vat", "Amount (excl. VAT) is required.")
        elif amt <= Decimal("0"):
            self.add_error("amount_excl_vat", "Amount must be greater than zero.")

        tp = cleaned.get("tax_percent")
        if tp is not None:
            if tp < Decimal("0") or tp > Decimal("100"):
                self.add_error("tax_percent", "Tax % must be between 0 and 100.")

        if not cleaned.get("payment_status"):
            self.add_error("payment_status", "Payment status is required.")

        return cleaned


class LegacyPayableForm(forms.ModelForm):
    class Meta:
        model = LegacyPayable
        fields = [
            "supplier_name",
            "total_payable",
            "total_paid",
            "date_last_paid",
            "projects_name",
            "status_note",
        ]
        widgets = {
            "supplier_name": forms.TextInput(attrs={"class": "form-control"}),
            "total_payable": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "total_paid": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "date_last_paid": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "projects_name": forms.TextInput(attrs={"class": "form-control"}),
            "status_note": forms.TextInput(attrs={"class": "form-control"}),
        }
