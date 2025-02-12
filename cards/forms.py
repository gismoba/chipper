from core.validators import FileSizeValidator
from django import forms
from django.core.validators import FileExtensionValidator
from settings.models import PRODUCTS_CHOICES, ProductGroup

from .models import NFCCard, PurchasingCode


class URLBulkCreateForm(forms.Form):
    count = forms.IntegerField(label="Quantity", min_value=1)


class CodeBulkCreateForm(forms.ModelForm):
    count = forms.IntegerField(label="Quantity", min_value=1)
    product = forms.ChoiceField(
        label="Product", widget=forms.Select(attrs={"class": "custom-select"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        group_choices = [
            (group.id, group.title) for group in ProductGroup.objects.all()
        ]
        static_choices = PRODUCTS_CHOICES

        self.fields["product"].choices = group_choices + static_choices

    class Meta:
        model = PurchasingCode
        fields = ["count", "duration"]
        widgets = {
            "duration": forms.Select(attrs={"class": "custom-select"}),
        }


class NFCCardForm(forms.ModelForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(), required=False, label="Old Password"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(), required=True, label="Password"
    )
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())

    class Meta:
        model = NFCCard
        fields = ["old_password", "password", "password2"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.password:
            self.fields["old_password"].required = True
        else:
            self.fields.pop("old_password")

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if self.instance and self.instance.password and old_password:
            if not self.instance.check_password(old_password):
                raise forms.ValidationError("Old password is incorrect")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class NFCCardTitleForm(forms.ModelForm):
    class Meta:
        model = NFCCard
        fields = ["title"]


class BusinessCardForm(forms.Form):
    title = forms.CharField(max_length=255)
    desc = forms.CharField(label="Description", max_length=255)
    logo = forms.ImageField(
        required=False, validators=[FileSizeValidator(max_size=5242880)]
    )
    show = forms.BooleanField(label="Select This Product", required=False)


class GalleryForm(forms.Form):
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["png", "jpg", "jpeg", "gif", "webp"]
            ),
            FileSizeValidator(max_size=5242880),
        ],
    )
    show = forms.BooleanField(label="Select This Product", required=False)


class RedirectUrlForm(forms.Form):
    url = forms.URLField(required=False)
    show = forms.BooleanField(label="Select This Product", required=False)


class VideoMessageForm(forms.Form):
    video = forms.FileField(
        label="Video Message",
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=["mp4"]),
            FileSizeValidator(max_size=52428800),
        ],
    )
    show = forms.BooleanField(label="Select This Product", required=False)


class ProductViewerForm(forms.Form):
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["png", "jpg", "jpeg", "gif", "webp"]
            ),
            FileSizeValidator(max_size=5242880),
        ],
    )
    title = forms.CharField(max_length=255)
    desc = forms.CharField(label="Description", widget=forms.Textarea)
    show = forms.BooleanField(label="Select This Product", required=False)


class PDFViewerFom(forms.Form):
    file = forms.FileField(
        label="PDF File",
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
            FileSizeValidator(max_size=20971520),
        ],
    )
    show = forms.BooleanField(label="Select This Product", required=False)


class LetterForm(forms.Form):
    title = forms.CharField(label="Title", max_length=255)
    text = forms.CharField(label="Your Letter", widget=forms.Textarea)
    show = forms.BooleanField(label="Select This Product", required=False)
