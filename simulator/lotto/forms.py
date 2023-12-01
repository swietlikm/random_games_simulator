from django import forms


class RandomLottoForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100000,
        initial=10000,
        help_text="Enter a quantity greater than 0 and smaller or equal to 100 000",
    )

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        if quantity is not None and (quantity < 1 or quantity > 100000):
            raise forms.ValidationError("Quantity must be greater than 0 and smaller than 100001")

        return quantity
