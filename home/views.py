from django.shortcuts import render, redirect
from home.forms import (
    LoginForm,
    RegistrationForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
    UserPasswordChangeForm,
)
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth import views as auth_views
import json
from .models import Customer, Artist, Package, Booking
from .forms import BookingForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib import messages
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
import random
from django.db.models import Count, Sum, Q


# @login_required
# @login_required(login_url="/accounts/login/")
# def add_booking(request):
#     if request.method == "POST":
#         try:
#             with transaction.atomic():
#                 # Get customer info
#                 phone_number = request.POST.get("phone_number")
#                 customer_name = request.POST.get("customer_name")
#                 customer, _ = Customer.objects.get_or_create(
#                     phone_number=phone_number, defaults={"name": customer_name}
#                 )

#                 # Get general booking info
#                 number_of_appointments = int(
#                     request.POST.get("number_of_appointments", 1)
#                 )
#                 total_advance_payment = Decimal(request.POST.get("advance_payment", 0))
#                 payment_method = request.POST.get("payment_method")
#                 discount_percentage = Decimal(
#                     request.POST.get("discount_percentage", 0)
#                 )

#                 # Calculate advance payment per appointment
#                 advance_payment_per_appointment = (
#                     total_advance_payment / number_of_appointments
#                 )

#                 bookings = []
#                 for i in range(1, number_of_appointments + 1):
#                     appointment_datetime_str = request.POST.get(
#                         f"appointment_datetime_{i}"
#                     )

#                     # Parse the datetime string
#                     naive_datetime = datetime.strptime(
#                         appointment_datetime_str, "%Y-%m-%dT%H:%M"
#                     )

#                     # Create a timezone-aware datetime in the local timezone
#                     local_tz = ZoneInfo("Asia/Karachi")
#                     appointment_datetime = naive_datetime.replace(tzinfo=local_tz)

#                     artist_id = request.POST.get(f"artist_{i}")
#                     package_id = request.POST.get(f"package_{i}")

#                     artist = Artist.objects.get(id=artist_id)
#                     package = Package.objects.get(id=package_id)

#                     # Calculate amounts
#                     package_price = package.price
#                     discount_amount = package_price * (
#                         discount_percentage / Decimal("100")
#                     )
#                     net_amount = package_price - discount_amount
#                     balance_amount = net_amount - advance_payment_per_appointment

#                     booking = Booking(
#                         customer=customer,
#                         appointment_datetime=appointment_datetime,
#                         artist=artist,
#                         package=package,
#                         advance_payment=advance_payment_per_appointment,
#                         payment_method=payment_method,
#                         balance_amount=balance_amount,
#                         total_payment=net_amount,
#                         discount_percentage=discount_percentage,
#                     )
#                     bookings.append(booking)

#                 # Bulk create all bookings
#                 Booking.objects.bulk_create(bookings)

#             messages.success(
#                 request, f"{number_of_appointments} booking(s) created successfully."
#             )
#             return redirect("add_booking")
#         except Exception as e:
#             messages.error(request, f"An error occurred: {str(e)}")

#     artists = Artist.objects.all()
#     context = {
#         "artists": artists,
#     }
#     return render(request, "pages/add_booking.html", context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
from django.contrib.auth.decorators import login_required
from .models import Customer, Artist, Package, Booking


@login_required(login_url="/accounts/login/")
def add_booking(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Get customer info
                phone_number = request.POST.get("phone_number")
                customer_name = request.POST.get("customer_name")
                customer, _ = Customer.objects.get_or_create(
                    phone_number=phone_number, defaults={"name": customer_name}
                )
                # Get notes
                notes = request.POST.get("notes", "")

                # Get general booking info
                number_of_appointments = int(
                    request.POST.get("number_of_appointments", 1)
                )
                total_advance_payment = Decimal(request.POST.get("advance_payment", 0))
                payment_method = request.POST.get("payment_method")
                discount_price = Decimal(request.POST.get("discount_price", 0))


                # Calculate total package price
                total_package_price = sum(
                    Package.objects.get(id=request.POST.get(f"package_{i}")).price
                    for i in range(1, number_of_appointments + 1)
                )

                # Calculate advance payments for each booking
                advance_payments = []
                discounts = []

                for i in range(1, number_of_appointments + 1):
                    package_price = Package.objects.get(
                        id=request.POST.get(f"package_{i}")
                    ).price
                    percentage = package_price / total_package_price
                    advance_payment = total_advance_payment * percentage
                    advance_payments.append(advance_payment)
                    discount = discount_price * percentage
                    discounts.append(discount)


                bookings = []
                local_tz = ZoneInfo("Asia/Karachi")
                
                morning_charge_applied = False
                for i, (advance_payment, discount) in enumerate(zip(advance_payments, discounts), start=1):
                    appointment_datetime_str = request.POST.get(
                        f"appointment_datetime_{i}"
                    )
                    naive_datetime = datetime.strptime(
                        appointment_datetime_str, "%Y-%m-%dT%H:%M"
                    )
                    appointment_datetime = naive_datetime.replace(tzinfo=local_tz)

                    artist_id = request.POST.get(f"artist_{i}")
                    package_id = request.POST.get(f"package_{i}")
                    ready_time_str = request.POST.get(f"ready_time_{i}")
                    ready_time = datetime.strptime(ready_time_str, "%H:%M").time()

                    artist = Artist.objects.get(id=artist_id)
                    package = Package.objects.get(id=package_id)

                    # Calculate amounts
                    package_price = package.price

                    # Add 3000 if appointment time is before 1:30 PM and it hasn't been applied yet
                    if (
                        not morning_charge_applied
                        and ready_time < datetime.strptime("13:30", "%H:%M").time()
                    ):
                        package_price += Decimal("3000")
                        morning_charge_applied = True

                    # discount_amount = package_price * (
                    #     discount_percentage / Decimal("100")
                    # )
                    net_amount = package_price - discount
                    balance_amount = net_amount - advance_payment

                    booking = Booking(
                        customer=customer,
                        appointment_datetime=appointment_datetime,
                        artist=artist,
                        package=package,
                        advance_payment=advance_payment,
                        payment_method=payment_method,
                        balance_amount=balance_amount,
                        total_payment=net_amount,
                        discount_percentage=discount,
                        ready_time=ready_time,
                        notes=notes  # Add notes to the booking
                    )
                    bookings.append(booking)

                # Bulk create all bookings
                Booking.objects.bulk_create(bookings)

            messages.success(
                request, f"{number_of_appointments} booking(s) created successfully."
            )
            return redirect("add_booking")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    artists = Artist.objects.all()
    context = {
        "artists": artists,
    }
    return render(request, "pages/add_booking.html", context)


@login_required(login_url="/accounts/login/")
def get_customer_info(request):
    phone_number = request.GET.get("phone_number")
    try:
        customer = Customer.objects.get(phone_number=phone_number)
        return JsonResponse({"name": customer.name})
    except Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=404)


@login_required
@require_POST
@csrf_exempt
def save_new_customer(request):
    data = json.loads(request.body)
    name = data.get("name")
    phone_number = data.get("phone_number")

    if not name or not phone_number:
        return JsonResponse(
            {"success": False, "error": "Name and phone number are required"},
            status=400,
        )

    customer, created = Customer.objects.get_or_create(
        phone_number=phone_number, defaults={"name": name}
    )

    return JsonResponse(
        {"success": True, "name": customer.name, "phone_number": customer.phone_number}
    )

@login_required
@require_POST
@csrf_exempt
def update_customer_name(request):
    data = json.loads(request.body)
    phone_number = data.get("phone_number")
    new_name = data.get("name")

    if not phone_number or not new_name:
        return JsonResponse(
            {"success": False, "error": "Phone number and name are required"},
            status=400,
        )

    try:
        customer = Customer.objects.get(phone_number=phone_number)
        customer.name = new_name
        customer.save()
        return JsonResponse({"success": True, "message": "Customer name updated successfully"})
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "error": "Customer not found"}, status=404)

@login_required(login_url="/accounts/login/")
def get_artist_packages(request):
    artist_id = request.GET.get("artist_id")
    packages = Package.objects.filter(artist_id=artist_id).values("id", "name", "price")
    return JsonResponse(list(packages), safe=False)


@login_required
def bookings_view(request):
    artists = Artist.objects.all()
    context = {
        "artists": artists,
    }
    return render(request, "pages/bookings.html", context)


@login_required
def appointments_view(request):
    artists = Artist.objects.all()
    context = {
        "artists": artists,
    }
    return render(request, "pages/appointments.html", context)


@login_required
def get_appointments(request):
    bookings = Booking.objects.all().select_related("customer", "artist", "package")

    # Create a mapping of artist IDs to color classes
    artists = set(booking.artist for booking in bookings)
    color_classes = [
        "event-danger",
        "event-success",
        "event-primary",
        "event-info",
        "event-warning",
        "event-dark",
    ]
    artist_colors = {
        artist.id: color_classes[i % len(color_classes)]
        for i, artist in enumerate(artists)
    }

    events = []
    for booking in bookings:
        start_time = booking.appointment_datetime
        end_time = start_time + timedelta(hours=1)
        events.append(
            {
                "id": booking.id,
                "title": f"{booking.customer.name} - {booking.package.name}",
                "start": booking.appointment_datetime.isoformat(),
                "end": (booking.appointment_datetime + timedelta(hours=1)).isoformat(),
                "className": artist_colors[booking.artist.id],
                "extendedProps": {
                    "customer": booking.customer.name,
                    "artist": booking.artist.name,
                    "artist_id": booking.artist.id,
                    "package": booking.package.name,
                    "total_payment": str(booking.total_payment),
                    "start_time": booking.appointment_datetime.strftime("%H:%M:%S"),
                    "end_time": (booking.appointment_datetime + timedelta(hours=1)).strftime("%H:%M:%S"),
                    "date": booking.appointment_datetime.strftime("%Y-%m-%d"),
                    "ready_time": booking.ready_time.strftime("%H:%M:%S") if booking.ready_time else None,
                    "notes": booking.notes
                },
            }
        )

    return JsonResponse(events, safe=False)


@login_required
def get_bookings(request):
    bookings = Booking.objects.all().select_related("customer", "artist", "package")

    # Create a mapping of artist IDs to color classes
    artists = set(booking.artist for booking in bookings)
    color_classes = [
        "event-danger",
        "event-success",
        "event-primary",
        "event-info",
        "event-warning",
        "event-dark",
    ]
    artist_colors = {
        artist.id: color_classes[i % len(color_classes)]
        for i, artist in enumerate(artists)
    }

    events = []
    for booking in bookings:
        # Truncate microseconds
        start_time = booking.created_at.replace(microsecond=0)
        end_time = start_time + timedelta(hours=1)

        events.append(
            {
                "id": booking.id,
                "title": f"{booking.customer.name} - {booking.package.name}",
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "className": artist_colors[booking.artist.id],
                "extendedProps": {
                    "customer": booking.customer.name,
                    "artist": booking.artist.name,
                    "artist_id": booking.artist.id,
                    "package": booking.package.name,
                    "total_payment": str(booking.total_payment),
                    "start_time": booking.appointment_datetime.strftime("%H:%M:%S"),
                    "end_time": (booking.appointment_datetime + timedelta(hours=1)).strftime("%H:%M:%S"),
                    "date": booking.appointment_datetime.strftime("%Y-%m-%d"),
                    "ready_time": booking.ready_time.strftime("%H:%M:%S") if booking.ready_time else None,
                    "notes": booking.notes,
                },
            }
        )
    return JsonResponse(events, safe=False)


@login_required
def get_booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    data = {
        "id": booking.id,
        "customer_name": booking.customer.name,
        "phone_number": booking.customer.phone_number,
        "appointment_datetime": timezone.localtime(
            booking.appointment_datetime
        ).isoformat(),
        "ready_time": booking.ready_time,
        "number_of_appointments": booking.number_of_appointments,
        "artist_id": booking.artist.id,
        "artist_name": booking.artist.name,
        "package_id": booking.package.id,
        "package_name": booking.package.name,
        "package_price": str(booking.package.price),
        "advance_payment": str(booking.advance_payment),
        "payment_method": booking.payment_method,
        "discount_percentage": str(booking.discount_percentage),
        "total_payment": str(booking.total_payment),
        "balance_amount": str(booking.balance_amount),
        "notes": str(booking.notes),
    }
    return JsonResponse(data)


@login_required
@require_POST
def update_booking(request):
    booking_id = request.POST.get("id")
    try:
        booking = Booking.objects.get(id=booking_id)

        # Update booking fields
        booking.appointment_datetime = request.POST.get("appointment_datetime")
        booking.number_of_appointments = request.POST.get("number_of_appointments")
        booking.artist_id = request.POST.get("artist")
        booking.package_id = request.POST.get("package")
        booking.advance_payment = request.POST.get("advance_payment")
        booking.payment_method = request.POST.get("payment_method")
        booking.discount_percentage = request.POST.get("discount_percentage")
        booking.total_payment = request.POST.get("total_payment")
        booking.balance_amount = request.POST.get("balance_amount")
        booking.notes = request.POST.get("edit_notes")

        # Update customer if phone number changed
        phone_number = request.POST.get("phone_number")
        if phone_number != booking.customer.phone_number:
            try:
                customer = Customer.objects.get(phone_number=phone_number)
            except Customer.DoesNotExist:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Customer not found for the given phone number",
                    }
                )
            booking.customer = customer

        booking.save()
        return JsonResponse({"status": "success"})
    except ObjectDoesNotExist:
        return JsonResponse({"status": "error", "message": "Booking not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


@login_required
@require_POST
def update_booking_time(request):
    booking_id = request.POST.get("id")
    start_time = request.POST.get("start")

    try:
        booking = Booking.objects.get(id=booking_id)
        booking.appointment_datetime = parse_datetime(start_time)
        booking.save()
        return JsonResponse({"status": "success"})
    except Booking.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Booking not found"}, status=404
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@require_POST
def delete_booking(request):
    booking_id = request.POST.get("id")

    booking = Booking.objects.get(id=booking_id)
    booking.delete()

    return JsonResponse({"status": "success"})


@login_required
def randomize_booking_dates(request):
    # Get the current year
    current_year = timezone.now().year

    # Get all bookings
    bookings = Booking.objects.all()

    # Update each booking with a random date from this year
    for booking in bookings:
        # Generate a random date for this year
        random_date = datetime(current_year, 1, 1) + timedelta(
            days=random.randint(0, 364)
        )

        # Keep the original time, just update the date
        new_datetime = datetime.combine(
            random_date.date(), booking.appointment_datetime.time()
        )

        # Update the booking
        booking.appointment_datetime = new_datetime
        booking.save()

    # Return a response
    return HttpResponse(
        f"Updated {bookings.count()} bookings with random dates from {current_year}"
    )


@login_required
def populate_database(request):
    # Check if data already exists
    if Artist.objects.exists() or Package.objects.exists():
        return HttpResponse("Database already populated. No action taken.")

    # Add Artists
    amna = Artist.objects.create(name="AMNA RAFIQ JAVERI")
    kanwal = Artist.objects.create(name="KANWAL")

    # Packages and Add-ons data
    amna_packages = [
        ("Party Makeup", 18000),
        ("Mayun/ Baat Pakki/ Dua-e-Khair", 25000),
        ("Engagement/ Mehndi/ Nikkah", 35000),
        ("Barat/ Walima", 50000),
        ("Barat + Walima", 95000),  # Discounted price
        ("Mehndi + Barat + Walima", 127000),  # Discounted price
        ("5 Party Makeups By Amna", 85000),  # Discounted price
    ]

    kanwal_packages = [
        ("Soft Party Makeup", 10000),
        ("Heavy Party Makeup", 12500),
        ("Mayun/ Baat Pakki/ Dua-e-Khair", 18500),
        ("Engagement/ Mehndi/ Nikkah", 25000),
        ("Barat/ Walima", 32500),
        ("Barat + Walima", 60000),  # Discounted price
        ("Mehndi + Barat + Walima", 82000),  # Discounted price
    ]

    add_ons_data = [
        ("Dupatta Setting On Head", 2000),
        ("Dupatta Setting On Shoulders", 1000),
        ("Fake Nails Application", 1000),
        ("Nail Paint On Hands", 250),
        ("Hair Extensions Application", 1000),
        ("Reusable Hair Extensions", 3000),
    ]

    # Add packages for Amna
    for name, price in amna_packages:
        Package.objects.create(artist=amna, name=name, price=Decimal(price))

    # Add packages for Kanwal
    for name, price in kanwal_packages:
        Package.objects.create(artist=kanwal, name=name, price=Decimal(price))

    # Add add-ons for both artists
    for artist in [amna, kanwal]:
        for name, price in add_ons_data:
            Package.objects.create(artist=artist, name=name, price=Decimal(price))

    return HttpResponse(
        "Database populated successfully with artists and packages (including add-ons)."
    )


@login_required(login_url="/accounts/login/")
def dashboard(request):
    # Get the start of the current month
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Total bookings this month
    total_bookings = Booking.objects.filter(
        appointment_datetime__gte=start_of_month
    ).count()

    # Total revenue this month
    # total_revenue = (
    #     Booking.objects.filter(appointment_datetime__gte=start_of_month).aggregate(
    #         total=Sum("total_payment")
    #     )["total"]
    #     or 0
    # )

    # New customers this month
    new_customers = (
        Customer.objects.filter(booking__appointment_datetime__gte=start_of_month)
        .distinct()
        .count()
    )

    # Most popular package
    popular_package = (
        Package.objects.annotate(
            booking_count=Count(
                "booking", filter=Q(booking__appointment_datetime__gte=start_of_month)
            )
        )
        .order_by("-booking_count")
        .first()
    )

    # Recent bookings
    recent_bookings = Booking.objects.select_related("customer", "package").order_by(
        "-appointment_datetime"
    )[:10]

    # Top artists
    top_artists = Artist.objects.annotate(
        booking_count=Count(
            "booking", filter=Q(booking__appointment_datetime__gte=start_of_month)
        )
    ).order_by("-booking_count")[:5]

    context = {
        "total_bookings": total_bookings,
        "new_customers": new_customers,
        "popular_package": popular_package.name if popular_package else "N/A",
        "recent_bookings": recent_bookings,
        "top_artists": top_artists,
    }

    return render(request, "pages/dashboard/analytics.html", context)


# For sqlite
# from django.db.models.functions import TruncYear, TruncMonth, TruncDay

# @login_required(login_url="/accounts/login/")
# def finances(request):
#     view_type = request.GET.get("view", "monthly")  # Default to monthly view

#     if view_type == "yearly":
#         bookings = (
#             Booking.objects.annotate(date=TruncYear("appointment_datetime"))
#             .values("date")
#             .annotate(
#                 total_amount=Sum("total_payment"),
#                 net_amount=Sum("total_payment") - Sum("advance_payment"),
#             )
#             .order_by("-date")
#         )
#     elif view_type == "daily":
#         bookings = (
#             Booking.objects.annotate(date=TruncDay("appointment_datetime"))
#             .values("date")
#             .annotate(
#                 total_amount=Sum("total_payment"),
#                 net_amount=Sum("total_payment") - Sum("advance_payment"),
#             )
#             .order_by("-date")
#         )
#     else:  # Monthly view
#         bookings = (
#             Booking.objects.annotate(date=TruncMonth("appointment_datetime"))
#             .values("date")
#             .annotate(
#                 total_amount=Sum("total_payment"),
#                 net_amount=Sum("total_payment") - Sum("advance_payment"),
#             )
#             .order_by("-date")
#         )

#     context = {
#         "bookings": bookings,
#         "view_type": view_type,
#     }
#     return render(request, "pages/finances.html", context)


from collections import defaultdict
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def is_not_manager(user):
    return not user.groups.filter(name="manager").exists()


def permission_denied(request):
    return render(request, "403.html")


@login_required
@user_passes_test(is_not_manager, login_url="permission_denied")
def finances(request):
    view_type = request.GET.get("view", "monthly")

    # Fetch all bookings
    all_bookings = Booking.objects.all().values(
        "appointment_datetime", "total_payment", "advance_payment"
    )

    # Group and calculate in Python
    grouped_bookings = defaultdict(
        lambda: {"total_amount": 0, "net_amount": 0, "advance_amount": 0}
    )

    for booking in all_bookings:
        date = timezone.localtime(booking["appointment_datetime"])
        if view_type == "yearly":
            key = date.strftime("%Y")
        elif view_type == "daily":
            key = date.strftime("%Y-%m-%d")
        else:  # monthly
            key = date.strftime("%Y-%m")
            view_type = "monthly"

        grouped_bookings[key]["total_amount"] += booking["total_payment"]
        grouped_bookings[key]["net_amount"] += (
            booking["total_payment"] - booking["advance_payment"]
        )
        grouped_bookings[key]["advance_amount"] += booking["advance_payment"]

    # Convert to list and sort
    bookings = [
        {
            "date": datetime.strptime(
                key,
                (
                    "%Y"
                    if view_type == "yearly"
                    else "%Y-%m" if view_type == "monthly" else "%Y-%m-%d"
                ),
            ),
            "total_amount": values["total_amount"],
            "net_amount": values["net_amount"],
            "advance_amount": values["advance_amount"],
        }
        for key, values in grouped_bookings.items()
    ]
    bookings.sort(key=lambda x: x["date"], reverse=True)

    context = {
        "bookings": bookings,
        "view_type": view_type,
    }

    return render(request, "pages/finances.html", context)


@login_required(login_url="/accounts/login/")
def customer_search(request):
    query = request.GET.get("q")
    date_filter = request.GET.get("date")
    bookings = []
    customer = None

    if query:
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(phone_number__icontains=query)
        )
        if customers.exists():
            customer = customers.first()
            bookings = Booking.objects.filter(customer=customer)

            if date_filter:
                try:
                    filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                    bookings = bookings.filter(appointment_datetime__date=filter_date)
                except ValueError:
                    # Handle invalid date format
                    pass

            bookings = bookings.order_by("-appointment_datetime")

    if bookings:
        totals = bookings.aggregate(
            total_payment_sum=Sum('total_payment'),
            advance_payment_sum=Sum('advance_payment'),
            balance_amount_sum=Sum('balance_amount')
        )
    else:
        totals = {
            'total_payment_sum': 0,
            'advance_payment_sum': 0,
            'balance_amount_sum': 0
        }

    context = {
        "query": query,
        "date_filter": date_filter,
        "customer": customer,
        "bookings": bookings,
        'totals': totals,
    }
    return render(request, "pages/customer_search.html", context)

@login_required(login_url="/accounts/login/")
def appointments_list_view(request):
    return render(request, "pages/list_appointments.html")

from django.db.models import F, Case, When, TimeField
@login_required(login_url="/accounts/login/")
def get_appointments_list(request):
    date_filter = request.GET.get("date")
    
    try:
        filter_date = timezone.datetime.strptime(date_filter, "%Y-%m-%d").date()
        
        # Create start and end of day in the server's time zone
        start_of_day = timezone.make_aware(timezone.datetime.combine(filter_date, timezone.datetime.min.time()))
        end_of_day = timezone.make_aware(timezone.datetime.combine(filter_date, timezone.datetime.max.time()))
        
        bookings = Booking.objects.filter(
            appointment_datetime__range=(start_of_day, end_of_day)
        ).annotate(
            ready_time_order=Case(
                When(ready_time__isnull=False, then=F('ready_time')),
                default=F('appointment_datetime'),
                output_field=TimeField()
            )
        ).order_by('ready_time_order')
        
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    appointments = []
    for booking in bookings:
        appointments.append({
            "customer_name": booking.customer.name,
            "customer_phone": booking.customer.phone_number,
            "appointment_date": booking.appointment_datetime.strftime("%Y-%m-%d"),
            "appointment_time": booking.appointment_datetime.strftime("%H:%M"),
            "ready_time": booking.ready_time.strftime("%H:%M") if booking.ready_time else "",
            "package": booking.package.name,
            "artist": booking.artist.name,
            "total_payment": float(booking.total_payment),
            "advance_payment": float(booking.advance_payment),
            "balance": float(booking.balance_amount),
            "notes": booking.notes,
        })

    return JsonResponse(appointments, safe=False)

# Authentication


######## Start Login #########
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            print("Account created successfully!")
            return redirect("/accounts/login/")
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {"form": form}
    return render(request, "accounts/register-v2.html", context)


class UserLoginView(auth_views.LoginView):
    template_name = "accounts/login-v2.html"
    form_class = LoginForm
    success_url = "/dashboard"


class UserPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password-change-v2.html"
    form_class = UserPasswordChangeForm


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/forgot-password-v2.html"
    form_class = UserPasswordResetForm


######## End Login #########


######## Common #########
class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/reset-password-v1.html"
    form_class = UserSetPasswordForm


def user_logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


######## End Common #########


def check_mail(request):
    return render(request, "accounts/check-mail-v2.html")


def reset_password(request):
    return render(request, "accounts/reset-password-v2.html")


def code_verification(request):
    return render(request, "accounts/code-verification-v2.html")


# Maintenance
def error_404(request):
    return render(request, "accounts/error-404.html")


def coming_soon(request):
    return render(request, "accounts/coming-soon-v2.html")


def under_construction(request):
    return render(request, "accounts/under-construction.html")


def landing(request):
    return render(request, "accounts/landing.html")


# i18n
def i18n_view(request):
    context = {"parent": "apps", "segment": "i18n"}
    return render(request, "pages/navigation/i18n.html", context)
