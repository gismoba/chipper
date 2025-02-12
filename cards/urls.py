from django.urls import path

from . import views

app_name = "cards"


urlpatterns = [
    path(
        "",
        views.NFCCardListView.as_view(extra_context={"active": "dashboard"}),
        name="user_dashboard",
    ),
    path(
        "landingPage/<uidb64>/",
        views.NFCCardView.as_view(),
        name="landing_page",
    ),
    path(
        "card-update/<uidb64>/",
        views.NFCCardDetailView.as_view(extra_context={"active": "dashboard"}),
        name="card_detail",
    ),
    path(
        "card-update/<uidb64>/<int:pk>/update-password/",
        views.NFCCardUpdateView.as_view(extra_context={"active": "dashboard"}),
        name="update_card_password",
    ),
    path(
        "card-update/<uidb64>/<int:pk>/update-title/",
        views.NFCCardUpdateTitle.as_view(extra_context={"active": "dashboard"}),
        name="update_card_title",
    ),
    path("cards-link/<uidb64>/", views.link_new_card, name="link_new_card"),
    path("cards-add/", views.add_new_card, name="add_new_card"),
    path("check-password/<uidb64>/", views.check_password, name="check_password"),
    path("card-update/update-business-card/<uidb64>/", views.update_business_card, name="update_business_card"),
    path("card-update/update-gallery/<uidb64>/", views.update_gallery, name="update_gallery"),
    path("card-update/remove-gallery-image/<uidb64>/<path:image_url>/", views.remove_gallery_image, name="remove_gallery_image"),
    path("card-update/remove-product-image/<uidb64>/<path:image_url>/", views.remove_product_image, name="remove_product_image"),
    path("card-update/update-redirect-url/<uidb64>/", views.update_redirect_url, name="update_redirect_url"),
    path("card-update/update-video-message/<uidb64>/", views.update_video_message, name="update_video_message"),
    path("card-update/update-product-viewer/<uidb64>/", views.update_product_viewer, name="update_product_viewer"),
    path("card-update/update-pdf-viewer/<uidb64>/", views.update_pdf_viewer, name="update_pdf_viewer"),
    path("card-update/update-letter/<uidb64>/", views.update_letter, name="update_letter"),
]
