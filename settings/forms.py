from django import forms
from .models import ProductGroup, PRODUCTS_CHOICES


class ProductGroupForm(forms.ModelForm):
    products = forms.MultipleChoiceField(
        choices=PRODUCTS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = ProductGroup
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.products:
            initial_products = self.instance.products.split(',')
            self.fields['products'].initial = initial_products
            self.initial['products'] = initial_products

    def clean_products(self):
        products = self.cleaned_data.get("products")
        if products:
            return ",".join(products)
        return ""
