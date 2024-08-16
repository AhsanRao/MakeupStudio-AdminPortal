from django.urls import path
from . import views

from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard_index"),
    # Application
    # path('application/customer-list/', views.customer_list, name='customer_list'),
    # path('application/order-list/', views.order_list, name='order_list'),
    # path('application/order-details/', views.order_details, name='order_details'),
    # path('application/create-invoice/', views.create_invoice, name='create_invoice'),
    # path('application/product-list/', views.product_list, name='product_list'),
    # path('application/product-review/', views.product_review, name='product_review'),
    # path('application/calendar/', views.calendar, name='calendar'),
    # Authentication
    ######## Common #########
    path("accounts/logout/", views.user_logout_view, name="logout"),
    path(
        "accounts/password-reset-confirm-v1/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "accounts/password-reset-done-v1/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password-reset-done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/password-reset-complete-v1/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password-reset-complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "accounts/password-change-done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password-change-done.html"
        ),
        name="password_change_done",
    ),
    ######## End Common #########
    ######## login #########
    path("accounts/login/", views.UserLoginView.as_view(), name="login"),
    path("accounts/register/", views.register, name="register"),
    path(
        "accounts/password-reset/",
        views.UserPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "accounts/password-change/",
        views.UserPasswordChangeView.as_view(),
        name="password_change",
    ),
    ######## End login #########
    path("accounts/check-mail/", views.check_mail, name="check_mail"),
    path("accounts/reset-password/", views.reset_password, name="reset_password"),
    path(
        "accounts/code-verification/", views.code_verification, name="code_verification"
    ),
    # Maintenance
    path("pages/error-404/", views.error_404, name="error_404"),
    path("pages/coming-soon/", views.coming_soon, name="coming_soon"),
    path(
        "pages/under-contruction/", views.under_construction, name="under_construction"
    ),
    path("add-booking/", views.add_booking, name="add_booking"),
    path("get-customer-info/", views.get_customer_info, name="get_customer_info"),
    path("save-new-customer/", views.save_new_customer, name="save_new_customer"),
    path('update-customer-name/', views.update_customer_name, name='update_customer_name'),
    path("get-artist-packages/", views.get_artist_packages, name="get_artist_packages"),
    path("populate-database/", views.populate_database, name="populate_database"),
    path("appointments/", views.appointments_view, name="appointments"),
    path("bookings/", views.bookings_view, name="bookings"),
    path(
        "randomize-bookings/", views.randomize_booking_dates, name="randomize_bookings"
    ),
    path("get-bookings/", views.get_bookings, name="get_bookings"),
    path("get-appointments/", views.get_appointments, name="get_appointments"),
    path("update-booking/", views.update_booking, name="update_booking"),
    path("delete-booking/", views.delete_booking, name="delete_booking"),
    path(
        "get-booking-details/<int:booking_id>/",
        views.get_booking_details,
        name="get_booking_details",
    ),
    path("finances/", views.finances, name="finances"),
    path("customer-search/", views.customer_search, name="customer_search"),
    path("update-booking-time/", views.update_booking_time, name="update_booking_time"),

    path('appointments-list/', views.appointments_list_view, name='appointments-list'),
    path('get-appointments-list/', views.get_appointments_list, name='get_appointments-list'),
    
    path('permission-denied/', views.permission_denied, name='permission_denied'),

]
