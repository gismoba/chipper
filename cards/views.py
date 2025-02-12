from cards.models import NFCCard
from core.utils import get_form_errors, handle_uploaded_file
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, UpdateView
from hitcount.models import HitCount
from hitcount.views import HitCountDetailView

from .forms import (BusinessCardForm, GalleryForm, LetterForm, NFCCardForm,
                    NFCCardTitleForm, PDFViewerFom, ProductViewerForm,
                    RedirectUrlForm, VideoMessageForm)
from .models import NFCCard, PurchasingCode


class NFCCardView(HitCountDetailView):
    template_name = "cards/langing_page_detail.html"
    model = NFCCard
    context_object_name = "card"
    count_hit = True

    def get_object(self, queryset=None):
        uuid = self.kwargs.get("uidb64")
        return get_object_or_404(self.model, uuid=uuid)


class NFCCardDetailView(DetailView):
    template_name = "cards/card_detail.html"
    model = NFCCard
    context_object_name = "card"

    def get_object(self, queryset=None):
        uuid = self.kwargs.get("uidb64")
        return get_object_or_404(self.model, uuid=uuid)


def link_new_card(request, uidb64):
    if request.method == "POST":
        code = request.POST.get('code')
        try:
            code = PurchasingCode.objects.get(code=code, card__isnull=True)
        except PurchasingCode.DoesNotExist:
            msg = "Wrong Code or used before"
            messages.error(request, msg)
            return redirect("cards:link_new_card", uidb64=uidb64)
        try:
            card = NFCCard.objects.get(uuid=uidb64, user__isnull=True)
        except NFCCard.DoesNotExist:
            msg = "Wrong Card uuid or used before"
            messages.error(request, msg)
            return redirect("cards:link_new_card", uidb64=uidb64)
        card.user = request.user
        data = {}
        data['choosen_product'] = {'product': ''}
        card.data = data
        card.save()
        code.card = card
        code.save()
        msg = "Card Linked Successfully"
        messages.success(request, msg)
        return redirect("cards:user_dashboard")
    return render(request, 'cards/card_register.html', {})


@login_required
def add_new_card(request):
    if request.method == "POST":
        code = request.POST.get('code')
        uuid = request.POST.get('uuid')
        try:
            code = PurchasingCode.objects.get(code=code, card__isnull=True)
        except PurchasingCode.DoesNotExist:
            msg = "Wrong Code or used before"
            messages.error(request, msg)
            return redirect("cards:add_new_card")
        try:
            card = NFCCard.objects.get(uuid=uuid, user__isnull=True)
        except NFCCard.DoesNotExist:
            msg = "Wrong Card uuid or used before"
            messages.error(request, msg)
            return redirect("cards:add_new_card")            
        card.user = request.user
        data = {}
        data['choosen_product'] = {'product': ''}
        card.data = data
        card.save()
        code.card = card
        code.save()
        msg = "Card Linked Successfully"
        messages.success(request, msg)
        return redirect("cards:user_dashboard")
    return render(request, 'cards/forms/card_add.html', {})


def check_password(request, uidb64):
    if request.method == "POST":
        card = get_object_or_404(NFCCard, uuid=uidb64)
        password = request.POST.get('password')
        if card.password == password:
            request.session['password_correct'] = True
            return redirect(card.get_absolute_url())
        else:
            request.session['password_correct'] = False
            msg = "Wrong Password, Try Again"
            messages.error(request, msg)
            return redirect(card.get_absolute_url())
    else:
        return redirect(card.get_absolute_url())


class NFCCardUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = NFCCard
    template_name = 'base/forms/create_update.html'
    success_message = "Card successfully updated"
    form_class = NFCCardForm

    def get_queryset(self):
        user = self.request.user
        qs = self.model.objects.filter(user=user)
        return qs

    def get_success_url(self):
          uidb64=self.kwargs['uidb64']
          return reverse_lazy('cards:card_detail', kwargs={'uidb64': uidb64})


class NFCCardUpdateTitle(NFCCardUpdateView):
    form_class = NFCCardTitleForm


class NFCCardListView(LoginRequiredMixin, ListView):
    model = NFCCard
    template_name = 'user/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super(NFCCardListView, self).get_context_data(*args, **kwargs)
        user = self.request.user
        content_types = ContentType.objects.all()
        total_hits = 0
        for content_type in content_types:
            hits = HitCount.objects.filter(
                content_type=content_type,
                object_pk__in=NFCCard.objects.filter(user=user).values_list('id', flat=True)
            ).aggregate(total_hits=Sum('hits'))['total_hits']

            if hits:
                total_hits += hits

        context['total_hits'] = total_hits
        current_year = timezone.now().year
        monthly_hits = (
            HitCount.objects.filter(
                content_type__in=content_types,
                object_pk__in=NFCCard.objects.filter(user=user).values_list('id', flat=True),
                modified__year=current_year
            ).annotate(month=ExtractMonth('modified'))
            .values('month')
            .annotate(total_hits=Sum('hits'))
            .order_by('month')
        )
        hits_by_month = {i: 0 for i in range(1, 13)}
        for entry in monthly_hits:
            hits_by_month[entry['month']] = entry['total_hits']
        context['hits_by_month'] = hits_by_month
        return context


@login_required
def update_business_card(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    if request.method == "POST":
        form = BusinessCardForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            show = form.cleaned_data.get('show')
            logo = request.FILES.get('logo')

            existing_data = card.data or {}
            existing_logo_url = existing_data.get('business_card', {}).get('logo_url', '')
            logo_url = handle_uploaded_file(request, logo) if logo else existing_logo_url
            json_data = {
                'title': title,
                'desc': desc,
                'logo_url': logo_url,
                'show': show
            }
            data = existing_data
            data['business_card'] = json_data
            if show:
                data['choosen_product'] = {'product': 'business_card'}
                if "redirect_url" in data:
                    data['redirect_url']['show'] = not show
                if "gallery" in data:
                    data['gallery']['show'] = not show
                if "letter" in data:
                    data['letter']['show'] = not show
                if "pdf_viewer" in data:
                    data['pdf_viewer']['show'] = not show
                if "video_message" in data:
                    data['video_message']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:card_detail", uidb64)
        else:
            msg = get_form_errors(form)
            messages.error(request, msg[0])
            return redirect("cards:card_detail", uidb64)
    else:
        if card.data:
            initial_data = card.data.get('business_card', {})
            logo_url = initial_data.get('logo_url', '')
        else:
            initial_data = {}
            logo_url = None
        form = BusinessCardForm(initial=initial_data)
    
    return render(request, 'cards/forms/business_card.html', {'form': form, 'logo_url': logo_url, "active": "dashboard"})


@login_required
def update_gallery(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        gallery_data = None
        if form.is_valid():
            files = request.FILES.getlist('images')
            show = form.cleaned_data.get('show')
            existing_data = card.data or {}
            existing_images = existing_data.get('gallery', {}).get('images', [])
            image_urls = existing_images or []
            for file in files:
                file_url = handle_uploaded_file(request, file)
                image_urls.append(file_url)
            
            data = card.data or {}
            data['gallery'] = {'images': image_urls, 'show': show}
            if show:
                data['choosen_product'] = {'product': 'gallery'}
                if "business_card" in data:
                    data['business_card']['show'] = not show
                if "redirect_url" in data:
                    data['redirect_url']['show'] = not show
                if "letter" in data:
                    data['letter']['show'] = not show
                if "pdf_viewer" in data:
                    data['pdf_viewer']['show'] = not show
                if "video_message" in data:
                    data['video_message']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:card_detail", uidb64)
        else:
            msg = get_form_errors(form)
            messages.error(request, msg[0])
            return redirect("cards:card_detail", uidb64)
    else:
        if card.data:
            data = card.data.get('gallery', {}).get('images', [])
            initial_data = card.data.get("gallery", {})
        else:
            data = None
            initial_data = {}
        form = GalleryForm(initial=initial_data)

    return render(request, 'cards/forms/gallery.html', {'form': form, 'gallery_data': data, 'uuid': card.uuid, "active": "dashboard"})


@login_required
def remove_gallery_image(request, uidb64, image_url):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    data = card.data or {}

    gallery_images = data.get('gallery', {}).get('images', [])

    if image_url in gallery_images:
        gallery_images.remove(image_url)

    data['gallery']['images'] = gallery_images
    card.data = data
    card.save()
    return redirect('cards:update_gallery', uidb64)


@login_required
def remove_product_image(request, uidb64, image_url):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    data = card.data or {}

    product_images = data.get('product_viewer', {}).get('images', [])

    if image_url in product_images:
        product_images.remove(image_url)

    data['product_viewer']['images'] = product_images
    card.data = data
    card.save()
    return redirect('cards:update_product_viewer', uidb64)


@login_required
def update_redirect_url(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    if request.method == "POST":
        form = RedirectUrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get('url')
            show = form.cleaned_data.get('show')
            existing_data = card.data or {}
            json_data = {
                'url': url,
                'show': show
            }
            data = existing_data
            data['redirect_url'] = json_data
            if show:
                data['choosen_product'] = {'product': 'redirect_url'}
                if "gallery" in data:
                    data['gallery']['show'] = not show
                if "business_card" in data:
                    data['business_card']['show'] = not show
                if "letter" in data:
                    data['letter']['show'] = not show
                if "pdf_viewer" in data:
                    data['pdf_viewer']['show'] = not show
                if "video_message" in data:
                    data['video_message']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:card_detail", uidb64)
        else:
            msg = get_form_errors(form)
            messages.error(request, msg[0])
            return redirect("cards:card_detail", uidb64)
    else:
        if card.data:
            initial_data = card.data.get("redirect_url", {})
        else:
            initial_data = {}
        form = RedirectUrlForm(initial=initial_data)
    
    return render(request, 'cards/forms/redirect_url.html', {'form': form, "active": "dashboard"})


@login_required
def update_video_message(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    if request.method == "POST":
        form = VideoMessageForm(request.POST, request.FILES)
        if form.is_valid():
            show = form.cleaned_data.get('show')
            video = request.FILES.get('video')

            existing_data = card.data or {}
            existing_video_url = existing_data.get('video_message', {}).get('video_url', '')
            existing_video_name = existing_data.get('video_message', {}).get('video', '')
            video_url = handle_uploaded_file(request, video) if video else existing_video_url
            if video:
                video_name = video.name
            else:
                video_name = existing_video_name
            json_data = {
                'video': video_name,
                'video_url': video_url,
                'show': show
            }
            data = existing_data
            data['video_message'] = json_data
            if show:
                data['choosen_product'] = {'product': 'video_message'}
                if "redirect_url" in data:
                    data['redirect_url']['show'] = not show
                if "gallery" in data:
                    data['gallery']['show'] = not show
                if "business_card" in data:
                    data['business_card']['show'] = not show
                if "letter" in data:
                    data['letter']['show'] = not show
                if "pdf_viewer" in data:
                    data['pdf_viewer']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:card_detail", uidb64)
        else:
            msg = get_form_errors(form)
            messages.error(request, msg[0])
            return redirect("cards:card_detail", uidb64)
    else:
        if card.data:
            initial_data = card.data.get('video_message', {})
            video_name = initial_data.get('video', '')
        else:
            initial_data = {}
            video_name = None
        form = VideoMessageForm(initial=initial_data)
    
    return render(request, 'cards/forms/video_message.html', {'form': form, 'video_name': video_name, "active": "dashboard"})


@login_required
def update_product_viewer(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    
    if request.method == 'POST':
        form = ProductViewerForm(request.POST, request.FILES)
        product_images = None
        if form.is_valid():
            files = request.FILES.getlist('images')
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            show = form.cleaned_data.get('show')
            existing_data = card.data or {}
            existing_images = existing_data.get('product_viewer', {}).get('images', [])
            image_urls = existing_images or []
            for file in files:
                file_url = handle_uploaded_file(request, file)
                image_urls.append(file_url)
            
            data = existing_data
            json_data = {
                'images': image_urls,
                'title': title,
                'desc': desc,
                'show': show
            }
            data['product_viewer'] = json_data
            if show:
                data['choosen_product'] = {'product': 'product_viewer'}
                if "business_card" in data:
                    data['business_card']['show'] = not show
                if "gallery" in data:
                    data['gallery']['show'] = not show
                if "redirect_url" in data:
                    data['redirect_url']['show'] = not show
                if "letter" in data:
                    data['letter']['show'] = not show
                if "pdf_viewer" in data:
                    data['pdf_viewer']['show'] = not show
                if "video_message" in data:
                    data['video_message']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:card_detail", uidb64)
        else:
            msg = get_form_errors(form)
            messages.error(request, msg[0])
            return redirect("cards:card_detail", uidb64)
    else:
        if card.data:
            initial_data = card.data.get('product_viewer', {})
            product_images = card.data.get('product_viewer', {}).get('images', [])
        else:
            initial_data = {}
            product_images = None
        form = ProductViewerForm(initial=initial_data)

    return render(request, 'cards/forms/product_viewer.html', {'form': form, 'product_images': product_images, 'uuid': card.uuid, "active": "dashboard"})


@login_required
def update_pdf_viewer(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    if request.method == "POST":
        form = PDFViewerFom(request.POST, request.FILES)
        if form.is_valid():
            show = form.cleaned_data.get('show')
            file = request.FILES.get('file')

            existing_data = card.data or {}
            existing_file_url = existing_data.get('pdf_viewer', {}).get('file_url', '')
            existing_file_name = existing_data.get('pdf_viewer', {}).get('file', '')
            file_url = handle_uploaded_file(request, file) if file else existing_file_url
            if file:
                file_name = file.name
            else:
                file_name = existing_file_name
            json_data = {
                'file': file_name,
                'file_url': file_url,
                'show': show
            }
            data = existing_data
            data['pdf_viewer'] = json_data
            if show:
                data['choosen_product'] = {'product': 'pdf_viewer'}
                if "redirect_url" in data:
                    data['redirect_url']['show'] = not show
                if "gallery" in data:
                    data['gallery']['show'] = not show
                if "business_card" in data:
                    data['business_card']['show'] = not show
                if "letter" in data:
                    data['letter']['show'] = not show
                if "video_message" in data:
                    data['video_message']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:card_detail", uidb64)
        else:
            msg = get_form_errors(form)
            messages.error(request, msg[0])
            return redirect("cards:card_detail", uidb64)
    else:
        if card.data:
            initial_data = card.data.get('pdf_viewer', {})
            file_name = initial_data.get('file', '')
        else:
            initial_data = {}
            file_name = None
        form = PDFViewerFom(initial=initial_data)
    
    return render(request, 'cards/forms/pdf_viewer.html', {'form': form, 'file_name': file_name, "active": "dashboard"})



@login_required
def update_letter(request, uidb64):
    card = get_object_or_404(NFCCard, uuid=uidb64, user=request.user)
    if request.method == "POST":
        form = LetterForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            text = form.cleaned_data.get('text')
            show = form.cleaned_data.get('show')

            existing_data = card.data or {}
            json_data = {
                'title': title,
                'text': text,
                'show': show
            }
            data = existing_data
            data['letter'] = json_data
            if show:
                data['choosen_product'] = {'product': 'letter'}
                if "redirect_url" in data:
                    data['redirect_url']['show'] = not show
                if "gallery" in data:
                    data['gallery']['show'] = not show
                if "business_card" in data:
                    data['business_card']['show'] = not show
                if "pdf_viewer" in data:
                    data['pdf_viewer']['show'] = not show
            card.data = data
            card.save()
            msg = "Updated Successfully"
            messages.success(request, msg)
            return redirect("cards:card_detail", uidb64)
        else:
            msg = get_form_errors(form)
            messages.error(request, msg[0])
            return redirect("cards:card_detail", uidb64)
    else:
        if card.data:
            initial_data = card.data.get('letter', {})
        else:
            initial_data = {}
        form = LetterForm(initial=initial_data)
    
    return render(request, 'cards/forms/letter.html', {'form': form, "active": "dashboard"})