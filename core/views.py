from cards.models import NFCCard, PurchasingCode
from django.contrib.admin import site
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _


def handler500(request):
    """To show our 500.html template instead of django default one"""
    return render(request, "500.html", status=500)


@login_required
def custom_admin_index(request, extra_context=None):
    url_count = NFCCard.objects.filter(batch__archive=False).count()
    code_count = PurchasingCode.objects.filter(batch__archive=False).count()
    extra_context = {
        'title': 'Home',
        'url_count': url_count,
        'code_count': code_count
    }

    context = {
        **site.each_context(request),
        **extra_context,
    }
    return TemplateResponse(request, 'admin/custom_index.html', context)
