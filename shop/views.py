#esewa intigration
from decimal import Decimal, InvalidOperation
import os
import uuid
import hmac
import hashlib
import base64
import json

import requests


import os

#others
import uuid
from pathlib import Path
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count
from django.http import JsonResponse,FileResponse,Http404,HttpResponse
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, ShopSetting, Category, Order, OrderItem
from .serializers import ProductSerializer
DEFAULT_SETTINGS={'brandName':'KUBIE Royals','tagline':'Handpicked sarees, kurtis and festive wear — delivered across Nepal.','whatsapp':'9779708059550','phone':'+977 9779708059550','facebook':'https://facebook.com/kusum.chand.803639','tiktok':'https://tiktok.com/@kubie.couture?r=1&_t=ZS-99mDTA3yeF2','email':'hello@example.com','address':'Kanchanpur, Mahendranagar, Nepal','hours':'Sun–Fri, 10:00 – 19:00','currency':'NPR'}
def storefront(request):return render(request,'index.html')
def dashboard(request):return render(request,'admin/index.html')
def admin_user(request):return request.user.is_authenticated and request.user.is_staff
@ensure_csrf_cookie
@api_view(['GET'])
def session(request):return Response({'authenticated':admin_user(request),'defaultPassword':False})
@csrf_protect
@api_view(['POST'])
def login_api(request):
 password=request.data.get('password','')
 username=settings.SHOP_ADMIN_USERNAME if hasattr(settings,'SHOP_ADMIN_USERNAME') else __import__('os').environ.get('SHOP_ADMIN_USERNAME','shopadmin')
 user=authenticate(request,username=username,password=password)
 if user is None or not user.is_staff:return Response({'error':'Incorrect password.'},status=401)
 login(request,user);return Response({'authenticated':True})
@csrf_protect
@api_view(['POST'])
def logout_api(request):logout(request);return Response({'authenticated':False})
def denied():return Response({'error':'Admin sign-in required.'},status=401)
@api_view(['GET','PUT'])
def settings_api(request):
 if request.method=='PUT':
  if not admin_user(request):return denied()
  if not isinstance(request.data,dict):return Response({'error':'Invalid JSON body.'},status=400)
  updates={k:str(request.data[k] if request.data[k] is not None else '').strip()[:500] for k in DEFAULT_SETTINGS if k in request.data}
  if not updates:return Response({'error':'Nothing to update.'},status=400)
  for k,v in updates.items():ShopSetting.objects.update_or_create(key=k,defaults={'value':v})
 values=DEFAULT_SETTINGS.copy();values.update({x.key:x.value for x in ShopSetting.objects.all() if x.value and x.key in values})
 return Response({'settings':values})
@api_view(['GET','POST'])
def products_api(request):
 if request.method=='POST':
  if not admin_user(request):return denied()
  serializer=ProductSerializer(data=request.data)
  if not serializer.is_valid():return Response({'error':' '.join(str(x) for vals in serializer.errors.values() for x in vals),'errors':serializer.errors},status=422)
  obj=serializer.save();return Response({'product':ProductSerializer(obj).data},status=201)
 if request.method == 'GET':
  qs = Product.objects.select_related('category').all()

  category = request.query_params.get('category')
  term = request.query_params.get('search', '').strip()

  if category:
   qs = qs.filter(category__name__iexact=category)

  if term:
   qs = qs.filter(
    Q(name__icontains=term) |
    Q(description__icontains=term) |
    Q(category__name__icontains=term)
   )

  if request.query_params.get('offers') == 'true':
   qs = qs.filter(discount_percent__gt=0)

  if request.query_params.get('featured') == 'true':
   qs = qs.filter(featured=True)

  categories = list(
   Category.objects.values_list('name', flat=True)
  )

  counts = dict(
   Product.objects
   .exclude(category=None)
   .values('category__name')
   .annotate(total=Count('id'))
   .values_list('category__name', 'total')
  )

  qs = qs.order_by('-featured', '-created_at')

  return Response({
   'products': ProductSerializer(
    qs, many=True,
    context={'request': request}
   ).data,
   'categories': categories,
   'counts': counts,
   'total': qs.count()
  })



@api_view(['GET','PUT','PATCH','DELETE'])
def product_detail(request,pk):
 obj=Product.objects.filter(pk=pk).first()
 if not obj:return Response({'error':'Product not found.'},status=404)
 if request.method=='GET':return Response({'product':ProductSerializer(obj).data})
 if not admin_user(request):return denied()
 if request.method=='DELETE':obj.delete();return Response({'deleted':pk})
 serializer=ProductSerializer(obj,data=request.data,partial=True)
 if not serializer.is_valid():return Response({'error':' '.join(str(x) for vals in serializer.errors.values() for x in vals),'errors':serializer.errors},status=422)
 if not serializer.validated_data:return Response({'error':'Nothing to update.'},status=400)
 obj=serializer.save();return Response({'product':ProductSerializer(obj).data})
@api_view(['POST'])
def upload_api(request):
 if not admin_user(request):return denied()
 image=request.FILES.get('image')
 if not image:return Response({'error':'Choose an image file to upload.'},status=400)
 if image.size>8*1024*1024:return Response({'error':'Image must be smaller than 8 MB.'},status=413)
 # Verify actual content rather than trusting the browser-provided MIME type.
 try:
  from PIL import Image
  image.seek(0);im=Image.open(image);fmt=im.format;im.verify();image.seek(0)
 except Exception:return Response({'error':'Invalid image file.'},status=415)
 ext={'JPEG':'jpg','PNG':'png','WEBP':'webp','GIF':'gif','AVIF':'avif'}.get(fmt)
 if not ext:return Response({'error':'Unsupported image format.'},status=415)
 key=f'products/{uuid.uuid4()}.{ext}'
 target=settings.MEDIA_ROOT/key;target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('wb') as dest:
  for chunk in image.chunks():dest.write(chunk)
 return Response({'imageKey':key,'imageUrl':'/media/'+key},status=201)

#For cart

from .cart import Cart


@api_view(["POST"])
def cart_add(request, pk):
    product = Product.objects.filter(pk=pk, in_stock=True).first()

    if not product:
        return Response({"error": "Product not found."}, status=404)

    cart = Cart(request)
    cart.add(pk)

    return Response({
        "message": "Added to cart.",
        "cartCount": sum(cart.cart.values())
    })
@api_view(["POST"])
def cart_update(request, pk):
    cart = Cart(request)

    try:
        quantity = int(request.data.get("quantity", 1))
    except (TypeError, ValueError):
        return Response({"error": "Invalid quantity."}, status=400)

    cart.update(pk, quantity)

    return Response({
        "message": "Cart updated.",
        "cartCount": cart.count()
    })


@api_view(["POST"])
def cart_remove(request, pk):
    cart = Cart(request)
    cart.remove(pk)

    return Response({
        "message": "Product removed.",
        "cartCount": cart.count()
    })




@api_view(["GET"])
def cart_detail(request):
    cart = Cart(request)

    products = Product.objects.filter(
        id__in=cart.cart.keys()
    )

    items = []

    for product in products:
        quantity = cart.cart[str(product.id)]
        price = product.original_price * (
            100 - product.discount_percent
        ) / 100

        items.append({
            "id": product.id,
            "name": product.name,
            "quantity": quantity,
            "price": float(price),
            "total": float(price * quantity),
            "imageUrl": product.image_key.url
            if product.image_key else None,
        })

    return Response({"items": items})





#for Order
@api_view(["POST"])
def create_order(request):
    cart = Cart(request)

    if not cart.cart:
        return Response({"error": "Cart is empty."}, status=400)

    name = request.data.get("name", "").strip()
    phone = request.data.get("phone", "").strip()
    address = request.data.get("address", "").strip()

    if not name or not phone or not address:
        return Response({"error": "Please fill all delivery details."}, status=400)

    products = Product.objects.filter(
        id__in=cart.cart.keys(),
        in_stock=True
    )

    if products.count() != len(cart.cart):
       return Response(
            {"error": "Some cart items are unavailable. Please update your cart."},
            status=400
        )
    total = sum(
        p.original_price * (100 - p.discount_percent) / 100
        * cart.cart[str(p.id)]
        for p in products
    )

    order_id = request.session.get("checkout_order_id")
    order = Order.objects.filter(
        id=order_id,
        payment_status="UNPAID"
    ).first()

    if order:
        order.name = name
        order.phone = phone
        order.address = address
        order.total = total
        order.items.all().delete()
    else:
        order = Order(
            name=name,
            phone=phone,
            address=address,
            total=total
        )

    try:
        order.full_clean()
        order.save()

        for product in products:
            quantity = cart.cart[str(product.id)]
            price = product.original_price * (100 - product.discount_percent) / 100

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=price,
                quantity=quantity
            )

    except ValidationError as e:
        return Response(
            {"error": " ".join(e.messages)},
            status=400
        )
    request.session["checkout_order_id"] = order.id
    request.session.modified = True

    return Response({
        "message": "Order created.",
        "orderId": order.id,
        "total": float(order.total)
    })




#esewa
@api_view(["POST"])
def esewa_payment(request, pk):
    order = Order.objects.filter(pk=pk).first()

    if not order:
        return Response({"error": "Order not found."}, status=404)
    if request.session.get("checkout_order_id") != order.id:
        return Response(
            {"error": "You are not authorized to pay this order."},
            status=403
        )
    transaction_uuid = str(uuid.uuid4())
    order.transaction_uuid = transaction_uuid
    order.save(update_fields=["transaction_uuid"])
    total = str(order.total)

    product_code = os.getenv("ESEWA_PRODUCT_CODE")
    secret_key = os.getenv("ESEWA_SECRET_KEY")

    message = (
        f"total_amount={total},"
        f"transaction_uuid={transaction_uuid},"
        f"product_code={product_code}"
    )

    signature = base64.b64encode(
        hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    return Response({
        "amount": total,
        "total_amount": total,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "signature": signature,
        "signed_field_names":
            "total_amount,transaction_uuid,product_code"
    })



# Add eSewa verification
@api_view(["GET"])
def verify_esewa(request, pk):
    order = Order.objects.filter(pk=pk).first()

    if not order:
        return Response({"error": "Order not found."}, status=404)
    if request.session.get("checkout_order_id") != order.id:
        return Response(
            {"error": "You are not authorized to verify this order."},
            status=403
        )
    url = "https://rc.esewa.com.np/api/epay/transaction/status/"

    params = {
    "product_code": os.getenv("ESEWA_PRODUCT_CODE"),
    "total_amount": str(order.total),
    "transaction_uuid": order.transaction_uuid,
}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return Response(
            {"error": "Could not verify payment."},
            status=502
        )

    if data.get("status") == "COMPLETE":
        order.payment_status = "PAID"
        order.status = "Confirmed"
        order.save()

        Cart(request).clear()
        request.session.pop("checkout_order_id", None)

        return Response({
            "verified": True,
            "message": "Payment successful."
        })

    return Response({
        "verified": False,
        "status": data.get("status", "UNKNOWN")
    })


def esewa_success(request, pk):
    encoded_data = request.GET.get("data")


    order = Order.objects.filter(pk=pk).first()

    if not order:
        return HttpResponse("Order not found.")

    if order.payment_status == "PAID":
        return HttpResponse("Payment already verified.")

    if not encoded_data:
        return HttpResponse("Payment data not received.")

    try:
        # Decode eSewa response
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        payment_data = json.loads(decoded_data)

        # Check transaction belongs to this order
        if payment_data.get("transaction_uuid") != order.transaction_uuid:
            return HttpResponse("Transaction does not match this order.")

    
        # Check amount
        try:
            paid_amount = Decimal(str(payment_data.get("total_amount")))
        except (InvalidOperation, TypeError):
            return HttpResponse("Invalid payment amount.")

        if paid_amount != order.total:
            return HttpResponse("Payment amount does not match.")
        # Verify returned signature
        secret_key = os.getenv("ESEWA_SECRET_KEY")

        signed_fields = payment_data["signed_field_names"].split(",")

        message = ",".join(
            f"{field}={payment_data[field]}"
            for field in signed_fields
        )

        expected_signature = base64.b64encode(
            hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        if not hmac.compare_digest(
            expected_signature,
            payment_data["signature"]
        ):
            return HttpResponse("Invalid payment signature.")

        # Verify directly with eSewa

        verify_url = "https://rc.esewa.com.np/api/epay/transaction/status/"

        response = requests.get(
            verify_url,
            params={
                "product_code": os.getenv("ESEWA_PRODUCT_CODE"),
                "total_amount": str(order.total),
                "transaction_uuid": order.transaction_uuid,
            },
            timeout=10
        )

        response.raise_for_status()
        verification = response.json()

 
        # Payment is verified
        order.payment_status = "PAID"
        order.status = "Confirmed"
        order.save()

        Cart(request).clear()
        request.session.pop("checkout_order_id", None)

        return HttpResponse(
            f"""
            <h1>Payment Successful</h1>
            <p>Order #{order.id}</p>
            <p>Payment verified successfully.</p>
            <a href="/">Return to shop</a>
            """
        )

    except Exception as error:
        return HttpResponse("Payment verification error.")
