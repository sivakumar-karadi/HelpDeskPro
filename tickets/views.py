
from django.conf import settings
from django.core.mail import send_mail
from smtplib import SMTPException

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Ticket
from .forms import UserRegisterForm
from .profile_forms import UserProfileForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserRegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


@login_required
def home(request):
    all_tickets = Ticket.objects.filter(
        owner=request.user
    )

    tickets = all_tickets.order_by("-id")

    # Search filter
    search_query = request.GET.get("q", "").strip()

    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get("status", "")

    if status_filter in ["Open", "In Progress", "Resolved"]:
        tickets = tickets.filter(status=status_filter)
    else:
        status_filter = ""

    # Priority filter
    priority_filter = request.GET.get("priority", "")

    if priority_filter in ["Low", "Medium", "High"]:
        tickets = tickets.filter(priority=priority_filter)
    else:
        priority_filter = ""

    context = {
        "tickets": tickets,
        "search_query": search_query,
        "status_filter": status_filter,
        "priority_filter": priority_filter,

        # Dashboard statistics
        "total_tickets": all_tickets.count(),
        "open_tickets": all_tickets.filter(
            status="Open"
        ).count(),
        "in_progress_tickets": all_tickets.filter(
            status="In Progress"
        ).count(),
        "resolved_tickets": all_tickets.filter(
            status="Resolved"
        ).count(),
    }

    return render(
        request,
        "tickets/home.html",
        context,
    )


@login_required
def create_ticket(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        priority = request.POST.get("priority", "Medium")

        if priority not in ["Low", "Medium", "High"]:
            priority = "Medium"

        if title and description:
            ticket = Ticket.objects.create(
                owner=request.user,
                title=title,
                description=description,
                priority=priority,
                status="Open",
            )

            try:
                emails_sent = send_mail(
                    subject=(
                        f"New HelpDeskPro Ticket #{ticket.id}: "
                        f"{ticket.title}"
                    ),
                    message=(
                        "A new support ticket has been created.\n\n"
                        f"Ticket ID: {ticket.id}\n"
                        f"Title: {ticket.title}\n"
                        f"Description: {ticket.description}\n"
                        f"Priority: {ticket.priority}\n"
                        f"Status: {ticket.status}\n"
                        f"Created by: {request.user.username}\n"
                        f"User email: "
                        f"{request.user.email or 'Not provided'}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.SUPPORT_EMAIL],
                    fail_silently=False,
                )

                if emails_sent == 1:
                    print(
                        f"Email notification sent for ticket #{ticket.id}."
                    )
                else:
                    print(
                        f"No email was sent for ticket #{ticket.id}."
                    )

            except (SMTPException, OSError, ValueError) as error:
                print(
                    f"Ticket #{ticket.id} was saved, "
                    f"but email notification failed: {error}"
                )

            return redirect("home")

    return render(
        request,
        "tickets/create_ticket.html",
    )


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        id=ticket_id,
        owner=request.user,
    )

    return render(
        request,
        "tickets/ticket_detail.html",
        {"ticket": ticket},
    )


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        id=ticket_id,
        owner=request.user,
    )

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        priority = request.POST.get("priority", ticket.priority)

        if priority not in ["Low", "Medium", "High"]:
            priority = ticket.priority

        if title and description:
            ticket.title = title
            ticket.description = description
            ticket.priority = priority
            ticket.save()

            return redirect(
                "ticket_detail",
                ticket_id=ticket.id,
            )

    return render(
        request,
        "tickets/edit_ticket.html",
        {"ticket": ticket},
    )


@login_required
@require_POST
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        id=ticket_id,
        owner=request.user,
    )

    new_status = request.POST.get("status", "").strip()

    valid_statuses = [
        "Open",
        "In Progress",
        "Resolved",
    ]

    old_status = ticket.status

    if new_status not in valid_statuses:
        return redirect(
            "ticket_detail",
            ticket_id=ticket.id,
        )

    if new_status != old_status:
        ticket.status = new_status
        ticket.save(update_fields=["status"])

        recipient_email = ticket.owner.email.strip()

        if recipient_email:
            try:
                emails_sent = send_mail(
                    subject=(
                        f"HelpDeskPro Ticket #{ticket.id} "
                        "Status Updated"
                    ),
                    message=(
                        "Your HelpDeskPro ticket status has changed.\n\n"
                        f"Ticket ID: {ticket.id}\n"
                        f"Title: {ticket.title}\n"
                        f"Previous status: {old_status}\n"
                        f"New status: {new_status}\n"
                        f"Priority: {ticket.priority}\n\n"
                        "Thank you for using HelpDeskPro."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )

                if emails_sent == 1:
                    print(
                        f"Status email sent to {recipient_email} "
                        f"for ticket #{ticket.id}."
                    )
                else:
                    print(
                        f"No status email was sent for ticket #{ticket.id}."
                    )

            except (SMTPException, OSError, ValueError) as error:
                print(
                    f"Ticket #{ticket.id} status was updated, "
                    f"but email notification failed: {error}"
                )
        else:
            print(
                f"Ticket #{ticket.id} status was updated, "
                "but the owner has no email address."
            )

    return redirect(
        "ticket_detail",
        ticket_id=ticket.id,
    )


@login_required
@require_POST
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        id=ticket_id,
        owner=request.user,
    )

    ticket.delete()

    return redirect("home")


@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(
            instance=request.user,
        )

    return render(
        request,
        "tickets/profile.html",
        {"form": form},
    )


def logout_user(request):
    logout(request)
    return redirect("login")
