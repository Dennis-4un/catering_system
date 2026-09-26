# Public Gathering Catering and Food-Service Management System

Phases 0-6 — the complete build: foundation through REST API, security
hardening, and PDF reporting.

## What's in this build

**Phase 0 — Foundation:** Flask app factory, all 31+ tables, auth/RBAC,
audit logging, seed script with demo data for every phase.

**Phase 1 — Customers & Event Booking** (`app/booking/`): event inquiries,
venue management, availability-checked confirmation.

**Phase 2 — Menus & Quotations** (`app/catering/`): menu/package browsing
and customization, quotation generation, approval → auto-created Contract,
PDF export.

**Phase 3 — Payments & Inventory** (`app/finance/`): payments, invoices,
inventory with low-stock flags, suppliers with performance summaries,
purchase orders. Confirming an event requires a completed payment.

**Phase 4 — Kitchen Production & Operations** (`app/operations/`): recipes,
production plans that auto-deduct real inventory, staff assignment,
checklists, deliveries.

**Phase 5 — Feedback & Reports** (`app/feedback/`): wastage, complaints,
reviews, all 5 notification types (booking/payment/schedule/staff/status),
admin audit log viewer, real dashboard KPIs, search/filter/pagination on
events/quotations/payments/purchases/inventory.

**Phase 6 — REST API, Security, PDF Reports** (`app/api/`):
- **REST API** (`/api/v1/`) — bearer-token authenticated (not session
  cookies), covering auth, menus, events (list/detail/create), quotations,
  payments, inventory, and dashboard stats. Every endpoint mirrors its
  browser-route counterpart's exact business rules and RBAC.
- **PDF exports** for invoices (`/finance/events/<id>/invoice/pdf`) and
  kitchen recipes (`/operations/recipes/<id>/pdf`), alongside the existing
  quotation PDF from Phase 2.
- **Security hardening**: see "Security" section below.

## Quick start

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY at minimum

export FLASK_APP=run.py         # set FLASK_APP=run.py on Windows
export FLASK_CONFIG=development

flask db upgrade                 # creates dev.db (SQLite) from migrations
python seed.py                   # creates roles, admin, demo data for every phase

flask run
```

Visit `http://127.0.0.1:5000`. `seed.py` prints credentials for every role.

### Using the REST API

```bash
# 1. Get a bearer token
curl -X POST http://127.0.0.1:5000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@catering-system.com","password":"ChangeMe123!"}'
# -> {"token": "...", "user": {...}}

# 2. Use it
curl http://127.0.0.1:5000/api/v1/events \
  -H "Authorization: Bearer <token>"
```

Endpoints:
| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/v1/auth/token` | — | body: `{email, password}` |
| POST | `/api/v1/auth/revoke` | token | invalidates the current token |
| GET | `/api/v1/menus` | — | public |
| GET | `/api/v1/events` | token | `?status=&page=&per_page=` |
| GET | `/api/v1/events/<id>` | token | owner or staff |
| POST | `/api/v1/events` | token (customer) | body: `{event_type, event_date, guest_count, venue_id?}` |
| GET | `/api/v1/quotations/<id>` | token | owner or staff |
| POST | `/api/v1/events/<id>/payments` | token (finance_officer) | requires an existing Contract |
| GET | `/api/v1/inventory` | token (inventory_manager) | `?q=` |
| GET | `/api/v1/dashboard/stats` | token | role-scoped KPIs |

Regenerating a token (calling `/auth/token` again) immediately invalidates
the previous one — only one live token per user at a time.

### Using PostgreSQL instead of SQLite

Set `DATABASE_URL` in `.env` to a Postgres connection string — no code
changes needed. Leave it genuinely blank (not present-but-empty) to use
SQLite.

## Running tests

```bash
pytest tests/ -v
```

**139 tests, all passing.** Covers auth/RBAC/audit (Phase 0), booking +
venue availability (Phase 1), menus/quotations/contracts/PDF (Phase 2),
payments/inventory/purchases (Phase 3), production/staffing/logistics
(Phase 4), feedback/notifications/dashboards/search (Phase 5), the full
REST API with input-validation edge cases (Phase 6), invoice/recipe PDF
exports, a CSRF-token regression suite, and dedicated security-hardening
tests (CSRF-exemption correctness, RBAC-rejects-wrong-role, SQL-injection-
shaped input, malformed JSON).

## Security (Section 27)

- **CSRF**: enabled globally via Flask-WTF for every browser-facing
  blueprint (auth, booking, catering, finance, operations, feedback),
  including plain HTML forms (each carries a manually-added token — see
  "Lessons" below). The `/api/` blueprint is the one deliberate exemption:
  it authenticates via `Authorization: Bearer <token>`, never the session
  cookie, so it isn't CSRF-exploitable in the first place (CSRF relies on
  a browser automatically attaching *ambient* credentials to a forged
  request — a custom header can't be forged that way). `tests/test_security_hardening.py`
  proves this exemption is narrow: browser routes remain fully protected,
  and the API rejects bad credentials with 401, never a CSRF 400.
- **RBAC**: `role_required()` (browser) and `api_role_required()` (API)
  share the same semantics — admin always passes, everyone else must match
  an explicit allow-list. `test_security_hardening.py` iterates every
  non-permitted role against a sample endpoint and confirms each is
  rejected, not just that the right role is accepted.
- **Input validation**: WTForms on every browser form; hand-written
  validation on every API JSON body (type checks, range checks, foreign-
  key existence checks) returning structured `{"errors": {...}}` on 400 —
  same rigor as the forms, different transport.
- **Audit logging**: every state-changing action across all six phases
  calls the shared `log_action()` helper, including new Phase 6 actions
  (API token issue/revoke, API-created events/payments, PDF downloads).
  Viewable at `/feedback/audit-logs` (admin only).
- **Ownership checks** on every event/quotation/payment/complaint/review
  route, in both the browser and the API.
- Passwords hashed with Werkzeug; secrets from environment variables only.

## Project structure

```
catering_system/
├── app/
│   ├── auth/                 # register/login/logout, RBAC decorator, forms
│   ├── booking/               # Phase 1 — events, venues
│   ├── catering/                # Phase 2 — menus, packages, quotations, PDF
│   ├── finance/                   # Phase 3 — payments, inventory, suppliers, invoice PDF
│   ├── operations/                  # Phase 4 — recipes, production, staffing, recipe PDF
│   ├── feedback/                      # Phase 5 — wastage, complaints, reviews, notifications, audit log
│   ├── api/                            # Phase 6 — REST API (bearer-token auth)
│   ├── main/                            # landing page + KPI dashboard
│   ├── models/                            # all tables, one file per domain
│   ├── templates/
│   ├── static/                             # CSS design system (rose/mauve, Playfair Display + Poppins) + vendored Bootstrap/Icons/Fonts (offline)
│   └── utils/audit.py                       # shared audit-log helper
├── migrations/                               # Flask-Migrate / Alembic
├── tests/
├── uploads/
├── config.py
├── requirements.txt
├── run.py
└── seed.py
```

## Team ownership

| Member | Owns |
|---|---|
| Sameer (Team Leader) | `app/auth/`, `app/booking/`, `app/main/`, coordination |
| Tashfeen Farid | `app/catering/` |
| Mubashir Ahmed | `app/finance/` |
| Denis Vector | `app/operations/` |
| Ahmed Raza | `app/feedback/`, `app/api/`, test suite, security hardening |

## Lessons from this build (worth knowing for the demo/viva)

- **Blank `.env` values vs. missing keys**: `os.environ.get(...) or default`
  is used throughout `config.py` instead of `.get(key, default)`, because
  a present-but-empty `.env` value (`DATABASE_URL=`) is not the same as an
  absent key, and the latter is all `.get`'s default parameter catches.
- **CSRF on plain forms**: every plain `<form>` needs a manually-added
  `csrf_token` input or Flask-WTF's global protection 400s it — caught via
  `tests/test_csrf_presence.py`, which forces CSRF on in a dedicated test
  fixture specifically because the main test config disables it for
  convenience and would otherwise mask this class of bug.
- **Staff visibility vs. staff authority are different permission
  questions**: a bug where Finance/Kitchen/Operations/Inventory staff
  could see zero events (and got 403 opening one directly) traced back to
  a single tuple, `STAFF_BOOKING_ROLES`, being reused for both "who can
  view the events list" and "who can confirm an event" — two different
  questions that happened to share a variable. Fixed by splitting them;
  regression-tested in `test_staff_visibility_fix.py`, including a test
  that Finance Officer's *broadened visibility* did NOT also broaden their
  *action* authority.
- **CSRF exemption for the API is a design decision, not a shortcut**:
  documented in `app/api/__init__.py` and proven correct (not just
  assumed) by `test_security_hardening.py`.
- **Venue availability** only blocks confirmation against already-
  *confirmed* events, not other pending inquiries for the same slot.
- Email validation rejects `.local`/reserved TLDs by design — use normal
  domains for test/seed accounts.
