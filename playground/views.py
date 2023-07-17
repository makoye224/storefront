from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F
from django.http import HttpResponse
from store.models import Product, Customer, Collection, OrderItem


def say_hello(request):
    queryset = Product.objects.filter(
        id__in=OrderItem.objects.values("product_id").distinct()
    )

    return render(request, "hello.html", {"name": "Mosh", "products": list(queryset)})
