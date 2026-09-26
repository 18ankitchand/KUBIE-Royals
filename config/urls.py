from django.contrib import admin
from django.urls import path,re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from shop import views
urlpatterns=[
    path('',views.storefront),
    path('admin/',views.dashboard),
    path('django-admin/',admin.site.urls),
    path('api/session',views.session),
    path('api/login',views.login_api),
    path('api/logout',views.logout_api),
    path('api/settings',views.settings_api),
    path('api/products',views.products_api),
    path('api/products/<int:pk>',views.product_detail),
    path('api/upload',views.upload_api),

    path("api/cart/", views.cart_detail),
    path("api/cart/add/<int:pk>/", views.cart_add),


    path("api/cart/update/<int:pk>/", views.cart_update),
    path("api/cart/remove/<int:pk>/", views.cart_remove),

    path("api/orders/create/", views.create_order),
#esewa
    path("api/esewa/payment/<int:pk>/", views.esewa_payment),
    path("api/esewa/verify/<int:pk>/", views.verify_esewa),
    path(
        "payment/esewa/success/<int:pk>/",
        views.esewa_success
    ),
    ]
if settings.DEBUG: urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    
