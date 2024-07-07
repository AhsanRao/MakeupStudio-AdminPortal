from django.contrib import admin
from .models import Customer, Artist, Package, Booking

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number')
    search_fields = ('name', 'phone_number')

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'artist')
    search_fields = ('name', 'artist__name')
    list_filter = ('artist',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'appointment_datetime', 'number_of_appointments', 'artist', 'package', 'advance_payment', 'payment_method', 'balance_amount', 'total_payment', 'discount_percentage', 'created_at', 'updated_at')
    search_fields = ('customer__name', 'artist__name', 'package__name')
    list_filter = ('artist', 'package', 'payment_method', 'created_at', 'updated_at')