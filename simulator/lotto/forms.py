from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import LottoGame


class RandomLottoForm(forms.Form):
    quantity = forms.IntegerField(
        label="Number of coupons",
        min_value=1,
        max_value=1000000,
        initial=100000,
        help_text="Enter a quantity greater than 0 and smaller or equal to 1 000 000",
    )

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        if quantity is not None and (quantity < 1 or quantity > 1000000):
            raise forms.ValidationError("Quantity must be greater than 0 and smaller than 1 000 001")

        return quantity


class NewLottoGameForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput,
        label="Date of the lottery:",
        initial=timezone.now(),
        help_text="Enter a date which you would like to simulate",
    )

    class Meta:
        model = LottoGame
        fields = ("date",)


class LottoGameUpdateForm(NewLottoGameForm):
    n1 = forms.IntegerField(min_value=1, max_value=49, required=False, label="Number 1")
    n2 = forms.IntegerField(min_value=1, max_value=49, required=False, label="Number 2")
    n3 = forms.IntegerField(min_value=1, max_value=49, required=False, label="Number 3")
    n4 = forms.IntegerField(min_value=1, max_value=49, required=False, label="Number 4")
    n5 = forms.IntegerField(min_value=1, max_value=49, required=False, label="Number 5")
    n6 = forms.IntegerField(min_value=1, max_value=49, required=False, label="Number 6")

    class Meta:
        model = LottoGame
        fields = ("date", "n1", "n2", "n3", "n4", "n5", "n6")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.numbers:
            for i in range(6):
                field_name = f"n{i + 1}"
                self.fields[field_name] = forms.IntegerField(
                    min_value=1,
                    max_value=49,
                    required=False,
                    label=f"Number {i + 1}",
                    initial=self.instance.numbers[i],
                )

    def clean(self):
        cleaned_data = super().clean()
        n1 = cleaned_data.get("n1")
        n2 = cleaned_data.get("n2")
        n3 = cleaned_data.get("n3")
        n4 = cleaned_data.get("n4")
        n5 = cleaned_data.get("n5")
        n6 = cleaned_data.get("n6")

        numbers = [n1, n2, n3, n4, n5, n6]

        if any(numbers) and not all(numbers):
            raise ValidationError("All 6 numbers must be given")

        if all(numbers):
            if len(set(numbers)) != 6:
                raise ValidationError("All 6 numbers must be unique")

            self.cleaned_data["numbers"] = numbers

        return self.cleaned_data
