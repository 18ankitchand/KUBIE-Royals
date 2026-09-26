from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):
 initial=True
 dependencies=[]
 operations=[migrations.CreateModel(name='Product',fields=[('id',models.BigAutoField(primary_key=True,serialize=False)),('name',models.TextField()),('category',models.TextField(db_index=True)),('description',models.TextField(default='')),('original_price',models.DecimalField(decimal_places=2,max_digits=12)),('discount_percent',models.IntegerField(default=0)),('image_key',models.TextField(blank=True,null=True)),('fabric',models.TextField(blank=True,null=True)),('in_stock',models.BooleanField(default=True)),('featured',models.BooleanField(default=False)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True))],options={'db_table':'shop_products'}),migrations.CreateModel(name='ShopSetting',fields=[('key',models.TextField(primary_key=True,serialize=False)),('value',models.TextField(default='')),('updated_at',models.DateTimeField(auto_now=True))],options={'db_table':'shop_settings'})]
