from django import forms

from .models import Petition


class PetitionForm(forms.ModelForm):
    # Honeypot field: hidden from people, bots tend to fill it in.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Petition
        fields = ["first_name", "last_name", "phone", "address", "email", "subject", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Cererea nu a putut fi trimisă.")
        return cleaned
