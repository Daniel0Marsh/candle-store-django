from django.contrib import admin
from .models import Candle, WaxMelt, StorePricingSettings

@admin.register(StorePricingSettings)
class StorePricingSettingsAdmin(admin.ModelAdmin):
    list_display = ('delivery_fee', 'free_delivery_over', 'updated_at')
    fieldsets = (
        (None, {
            'fields': (
                'delivery_fee',
                'free_delivery_over',
            )
        }),
    )

# Register the Candle model in the admin
@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'stock_quantity', 'scent', 'color', 'size', 'featured', 'best_seller', 'discount_price')
    list_filter = ('featured', 'best_seller', 'scent', 'color', 'size')
    search_fields = ('title', 'description')
    ordering = ('-price',)
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
                'price',
                'discount_price',
                'stock_quantity',
                'scent',
                'color',
                'size',
                'featured',
                'best_seller',
                'image'
            )
        }),
    )

# Register the WaxMelt model in the admin
@admin.register(WaxMelt)
class WaxMeltAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'stock_quantity', 'scent', 'color', 'size', 'featured', 'best_seller', 'discount_price')
    list_filter = ('featured', 'best_seller', 'scent', 'color', 'size')
    search_fields = ('title', 'description')
    ordering = ('-price',)
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
                'price',
                'discount_price',
                'stock_quantity',
                'scent',
                'color',
                'size',
                'featured',
                'best_seller',
                'image'
            )
        }),
    )
