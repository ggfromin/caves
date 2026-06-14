from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, City, MarketplaceItem, Purchase, Comment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'balance', 'has_server_access', 'created_at', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('created_at', 'is_staff', 'is_active', 'has_server_access')
    list_editable = ('has_server_access',)
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'avatar', 'bio', 'balance', 'has_server_access', 'city'),
        }),
    )
    readonly_fields = ('created_at',)

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'phone'),
        }),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'population', 'mayor', 'is_capital', 'founded_date')
    search_fields = ('name',)
    list_filter = ('is_capital', 'founded_date')
    list_editable = ('population', 'is_capital')

@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'seller', 'item_type', 'is_available', 'created_at')
    list_filter = ('item_type', 'is_available', 'created_at')
    search_fields = ('title', 'seller__username')
    list_editable = ('price', 'is_available')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('item', 'buyer', 'price_paid', 'purchased_at')
    list_filter = ('purchased_at',)
    readonly_fields = ('item', 'buyer', 'price_paid', 'purchased_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('item', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__username')