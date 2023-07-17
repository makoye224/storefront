from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from tags.models import TaggedItem
from . import models

# Register your models here.


class InventoryFilter(admin.SimpleListFilter):
    title = "Inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("<10", "Low")]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}
    actions = ["clear_inventory"]
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]
    list_editable = ["unit_price"]
    list_select_related = ["collection"]
    list_filter = ["collection", "last_update", InventoryFilter]
    search_fields = ["product"]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "LOW"
        return "OK"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, querset):
        updated_count = querset.update(inventory=0)
        self.message_user(
            request,
            f"{updated_count} products were successfully updated",
        )


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer", "payment_status"]
    inlines = [OrderItemInline]
    autocomplete_fields = ["customer"]


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders_set"]
    list_editable = ["membership"]
    ordering = ["last_name", "first_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="first_name")
    def orders_set(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, customer.orders_set)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_set=Count("order"))


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("product"))
