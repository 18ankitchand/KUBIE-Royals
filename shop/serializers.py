from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    originalPrice = serializers.DecimalField(
        source="original_price",
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    discountPercent = serializers.IntegerField(
        source="discount_percent",
        required=False,
        min_value=0,
        max_value=99,
    )

    # Preserve the old frontend API contract.
    category = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    categoryId = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    imageKey = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()

    inStock = serializers.BooleanField(
        source="in_stock",
        required=False,
    )

    createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True,
    )

    updatedAt = serializers.DateTimeField(
        source="updated_at",
        read_only=True,
    )

    finalPrice = serializers.SerializerMethodField()
    savings = serializers.SerializerMethodField()

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "category",
            "categoryId",
            "description",
            "originalPrice",
            "discountPercent",
            "finalPrice",
            "savings",
            "imageKey",
            "imageUrl",
            "fabric",
            "inStock",
            "featured",
            "createdAt",
            "updatedAt",
        ]

        read_only_fields = [
            "id",
            "finalPrice",
            "savings",
            "imageKey",
            "imageUrl",
            "createdAt",
            "updatedAt",
        ]

    def validate_originalPrice(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Original price must be greater than zero."
            )

        if value > Decimal("99999999"):
            raise serializers.ValidationError(
                "Original price is too large."
            )

        return value

    def _price(self, obj):
        return (
            obj.original_price
            * (Decimal("100") - obj.discount_percent)
            / Decimal("100")
        ).quantize(
            Decimal(".01"),
            rounding=ROUND_HALF_UP,
        )

    def get_finalPrice(self, obj):
        return float(self._price(obj))

    def get_savings(self, obj):
        return float(
            obj.original_price - self._price(obj)
        )

    def get_imageKey(self, obj):
        if not obj.image_key:
            return None

        return obj.image_key.name

    def get_imageUrl(self, obj):
        if not obj.image_key:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.image_key.url
            )

        return obj.image_key.url