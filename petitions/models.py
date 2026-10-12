"""Core data model: municipalities (tenants) and the petitions they receive."""
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class Municipality(models.Model):
    """A town hall. Every petition belongs to exactly one municipality."""

    name = models.CharField("denumire", max_length=200)
    slug = models.SlugField("identificator URL", unique=True)
    contact_email = models.EmailField("email de contact", blank=True)
    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="municipalities",
        verbose_name="personal cu acces",
    )
    is_active = models.BooleanField("activă", default=True)

    class Meta:
        verbose_name = "primărie"
        verbose_name_plural = "primării"
        ordering = ["name"]

    def __str__(self):
        return self.name


def generate_tracking_code():
    """Unguessable code the citizen uses to follow the petition without an account."""
    return secrets.token_urlsafe(16)


class Petition(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", "Primită"
        REGISTERED = "registered", "Înregistrată"
        IN_PROGRESS = "in_progress", "În lucru"
        ANSWERED = "answered", "Răspuns transmis"
        CLOSED = "closed", "Închisă"

    municipality = models.ForeignKey(
        Municipality, on_delete=models.PROTECT, related_name="petitions",
        verbose_name="primărie",
    )
    # Personal data required by law to register a petition (kept to the minimum).
    first_name = models.CharField("prenume", max_length=100)
    last_name = models.CharField("nume", max_length=100)
    phone = models.CharField("telefon", max_length=30)
    address = models.CharField("adresă", max_length=255)
    email = models.EmailField("email", blank=True)

    subject = models.CharField("subiect", max_length=200)
    description = models.TextField("descriere")

    status = models.CharField(
        "stadiu", max_length=20, choices=Status.choices, default=Status.RECEIVED,
    )
    registry_number = models.PositiveIntegerField("număr de înregistrare", null=True, blank=True)
    registry_year = models.PositiveIntegerField("an înregistrare", null=True, blank=True)
    tracking_code = models.CharField(
        max_length=32, unique=True, default=generate_tracking_code, editable=False,
    )

    created_at = models.DateTimeField("depusă la", default=timezone.now)
    due_date = models.DateField("termen legal de răspuns", null=True, blank=True)
    answered_at = models.DateTimeField("răspuns la", null=True, blank=True)

    class Meta:
        verbose_name = "sesizare"
        verbose_name_plural = "sesizări"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["municipality", "registry_year", "registry_number"],
                name="unique_registry_number_per_municipality_year",
            ),
        ]

    def __str__(self):
        return f"{self.registry_label} – {self.subject}"

    @property
    def registry_label(self):
        if self.registry_number:
            return f"{self.registry_number}/{self.registry_year}"
        return "neînregistrată"

    @property
    def is_overdue(self):
        return (
            self.due_date is not None
            and self.status not in (self.Status.ANSWERED, self.Status.CLOSED)
            and timezone.localdate() > self.due_date
        )

    def save(self, *args, **kwargs):
        if self.due_date is None:
            created = timezone.localdate(self.created_at)
            self.due_date = created + timedelta(days=settings.PETITION_RESPONSE_DAYS)
        super().save(*args, **kwargs)

    def register(self):
        """Assign the next registry number for this municipality and year."""
        if self.registry_number:
            return
        year = timezone.localdate().year
        with transaction.atomic():
            last = (
                Petition.objects.select_for_update()
                .filter(municipality=self.municipality, registry_year=year)
                .aggregate(models.Max("registry_number"))["registry_number__max"]
            )
            self.registry_year = year
            self.registry_number = (last or 0) + 1
            self.status = self.Status.REGISTERED
            self.save(update_fields=["registry_year", "registry_number", "status"])
