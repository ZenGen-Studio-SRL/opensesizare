from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .admin import PetitionAdmin
from .models import Municipality, Petition


def make_petition(municipality, **kwargs):
    data = dict(
        first_name="Ion", last_name="Popescu", phone="0700000000",
        address="Str. Exemplu 1", subject="Groapă în drum", description="Detalii",
    )
    data.update(kwargs)
    return Petition.objects.create(municipality=municipality, **data)


class PetitionModelTests(TestCase):
    def setUp(self):
        self.town = Municipality.objects.create(name="Primăria Test", slug="test")

    def test_due_date_is_30_days_after_submission(self):
        p = make_petition(self.town)
        self.assertEqual(p.due_date, timezone.localdate(p.created_at) + timedelta(days=30))

    def test_registry_numbers_are_sequential_per_municipality(self):
        other = Municipality.objects.create(name="Alta", slug="alta")
        a, b, c = make_petition(self.town), make_petition(self.town), make_petition(other)
        for p in (a, b, c):
            p.register()
        self.assertEqual((a.registry_number, b.registry_number, c.registry_number), (1, 2, 1))
        self.assertEqual(a.status, Petition.Status.REGISTERED)

    def test_tracking_codes_are_unique_and_long(self):
        a, b = make_petition(self.town), make_petition(self.town)
        self.assertNotEqual(a.tracking_code, b.tracking_code)
        self.assertGreaterEqual(len(a.tracking_code), 20)

    def test_overdue(self):
        p = make_petition(self.town, created_at=timezone.now() - timedelta(days=40))
        self.assertTrue(p.is_overdue)


class PublicViewsTests(TestCase):
    def setUp(self):
        self.town = Municipality.objects.create(name="Primăria Test", slug="test")

    def test_submit_without_account_and_follow_status(self):
        response = self.client.post(reverse("petitions:submit", args=["test"]), {
            "first_name": "Ana", "last_name": "Ionescu", "phone": "0711111111",
            "address": "Str. Florilor 2", "subject": "Iluminat stradal", "description": "Bec ars",
        })
        petition = Petition.objects.get()
        self.assertRedirects(response, reverse("petitions:status", args=[petition.tracking_code]))
        page = self.client.get(response["Location"])
        self.assertContains(page, "Iluminat stradal")
        self.assertNotContains(page, "0711111111")  # no personal data on the status page

    def test_honeypot_blocks_bots(self):
        self.client.post(reverse("petitions:submit", args=["test"]), {
            "first_name": "Bot", "last_name": "Bot", "phone": "1", "address": "x",
            "subject": "spam", "description": "spam", "website": "http://spam",
        })
        self.assertEqual(Petition.objects.count(), 0)


class DataIsolationTests(TestCase):
    def test_staff_only_see_their_municipality(self):
        town_a = Municipality.objects.create(name="A", slug="a")
        town_b = Municipality.objects.create(name="B", slug="b")
        clerk = User.objects.create_user("clerk", password="x", is_staff=True)
        town_a.staff.add(clerk)
        make_petition(town_a, subject="din A")
        make_petition(town_b, subject="din B")

        request = type("Req", (), {"user": clerk})()
        qs = PetitionAdmin(Petition, None).get_queryset(request)
        self.assertEqual([p.subject for p in qs], ["din A"])
