from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True, primary_key=True)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class Artist(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Package(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="packages"
    )

    def __str__(self):
        return f"{self.name} by {self.artist.name}"


class Booking(models.Model):
    PAYMENT_METHODS = [
        ("bank", "Bank Transfer"),
        ("cash", "Cash"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField()
    number_of_appointments = models.PositiveIntegerField(default=1)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=4, choices=PAYMENT_METHODS)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=0)
    total_payment = models.DecimalField(max_digits=10, decimal_places=0)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for {self.customer} on {self.appointment_datetime}"
