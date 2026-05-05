from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "client_name", "contract_value_excl_vat", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "contract_value_excl_vat": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
