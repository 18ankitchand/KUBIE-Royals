from django.contrib import admin
from .models import Product, Category, ShopSetting, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "original_price",
        "discount_percent",
        "in_stock",
        "featured",
    )

    list_filter = (
        "category",
        "in_stock",
        "featured",
    )

    search_fields = (
        "name",
        "description",
        "fabric",
    )


@admin.register(ShopSetting)
class ShopSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "updated_at")


# customer info
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
    "id",
    "name",
    "phone",
    "total",
    "status",
    "payment_status",
    "created_at",
)
    search_fields = ("id","name", "phone")
    list_filter = ("status",)