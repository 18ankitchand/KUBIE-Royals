from django.db import models
from django.core.validators import (MinValueValidator, MaxValueValidator,RegexValidator, MinLengthValidator)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shop_categories"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=140)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )

    description = models.TextField(blank=True, default="")

    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    discount_percent = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    image_key = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    fabric = models.CharField(
        max_length=120,
        blank=True,
        null=True
    )

    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shop_products"
        ordering = ["-featured", "-created_at"]

    def __str__(self):
        return self.name


class ShopSetting(models.Model):
    key = models.TextField(primary_key=True)
    value = models.TextField(default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shop_settings"

    def __str__(self):
        return self.key





name_validator = RegexValidator(
    regex=r'^[A-Za-z ]+$',
    message="Name can contain only letters and spaces."
)

phone_validator = RegexValidator(
    regex=r'^(97|98)\d{8}$',
    message="Enter a valid 10-digit Nepal mobile number."
)


class Order(models.Model):
    name = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(2),
            name_validator
        ]
    )

    phone = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    address = models.TextField(
        validators=[MinLengthValidator(5)]
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    transaction_uuid = models.CharField(
        max_length=100,
        blank=True
    )

    payment_status = models.CharField(
        max_length=20,
        default="UNPAID"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.name}"