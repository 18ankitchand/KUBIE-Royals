import django.db.models.deletion
from django.db import migrations, models


def clear_old_categories(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    Product.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0003_alter_product_image_key_alter_product_table_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Categories",
                "db_table": "shop_categories",
                "ordering": ["name"],
            },
        ),

        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": [
                    "-featured",
                    "-created_at",
                ]
            },
        ),

        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(
                blank=True,
                default="",
            ),
        ),

        migrations.AlterField(
            model_name="product",
            name="fabric",
            field=models.CharField(
                blank=True,
                max_length=120,
                null=True,
            ),
        ),

        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(
                max_length=140,
            ),
        ),

        # Clear old text categories like "Dude"
        migrations.RunPython(
            clear_old_categories,
            migrations.RunPython.noop,
        ),

        migrations.AlterModelTable(
            name="product",
            table="shop_products",
        ),

        migrations.AlterModelTable(
            name="shopsetting",
            table="shop_settings",
        ),

        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="shop.category",
            ),
        ),
    ]