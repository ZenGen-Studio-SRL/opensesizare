# OpenSesizare

Open-source platform that lets citizens submit petitions and complaints
to small municipalities online, and helps the town hall register them,
track legal response deadlines and publish anonymised statistics.

## Why

Many small municipalities in Romania still receive citizen complaints on
paper, by phone or during office hours, with no central record. The legal
response deadline (30 days) is often missed. Existing digital solutions
are proprietary, costly, and send citizen data to third parties.

## Planned features

- Public submission form (no account needed)
- Multi-tenant: one installation, many municipalities, isolated data
- Registry numbers, PDF export, deadline reminders
- Anonymised reports and statistics
- GDPR by design: data retention, deletion and export on request
- Accessible (WCAG) and multilingual
- Self-hosting with Docker

## Status

Early stage. The first skeleton is in place:

- [x] Data model: municipalities (tenants) and petitions
- [x] Public form without account, with a simple anti-bot honeypot
- [x] Status page via an unguessable tracking link (no personal data shown)
- [x] Registry numbers per municipality and year, 30-day legal deadline, overdue flag
- [x] Admin back-office with data isolation per municipality
- [x] Docker + PostgreSQL setup, automated tests
- [ ] PDF export, deadline reminders, reports
- [ ] GDPR retention and deletion
- [ ] Accessibility review and translations

## Run locally

Development (SQLite):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then add a municipality at `/admin/` and open the public form at `/p/<slug>/`.

With Docker (PostgreSQL):

```bash
cp .env.example .env   # then edit the values
docker compose up --build
```

Run the tests:

```bash
python manage.py test
```

## License

AGPL-3.0

Maintained by ZENGEN STUDIO SRL, Petroșani, Romania.
