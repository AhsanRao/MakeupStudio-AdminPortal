# Generated by Django 4.2.9 on 2024-06-25 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Artist",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("name", models.CharField(max_length=100)),
                (
                    "phone_number",
                    models.CharField(
                        max_length=15, primary_key=True, serialize=False, unique=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Package",
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
                ("name", models.CharField(max_length=100)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "artist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="packages",
                        to="home.artist",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Booking",
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
                ("appointment_datetime", models.DateTimeField()),
                ("number_of_appointments", models.PositiveIntegerField(default=1)),
                (
                    "advance_payment",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[("bank", "Bank Transfer"), ("cash", "Cash")],
                        max_length=4,
                    ),
                ),
                (
                    "balance_amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("total_payment", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "discount_percentage",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "artist",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="home.artist",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.customer"
                    ),
                ),
                (
                    "package",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="home.package",
                    ),
                ),
            ],
        ),
    ]
