# Record Comparator — System A vs System B Reconciliation

A Django + React tool that imports two dirty CSV exports (System A and System B), matches records across them despite inconsistent formatting, and surfaces every disagreement — reason, both values, and location — in a filterable table.

## The problem, in one line

Two systems record the same events. Neither is authoritative. They agree on most rows; the few dozen they disagree on are the ones that matter. Records also belong to different orgs (tenants), and one org's rows must never be visible when viewing another's.

## What I built

- **Import**: Both CSVs load into SQLite (`SystemARecord`, `SystemBRecord`, `Location`, `ComparisonResult`) via pandas. Nothing is dropped — blank fields, malformed IDs, and unparseable numbers are all preserved as-is and handled downstream, not filtered out at import time.
- **Matching**: IDs are normalized before comparison (`REC-1001`, `rec1001`, `1001`, `REC 1070` all resolve to the same key), since System B's `record_ref` is written inconsistently.
- **Comparison logic**: catches records only in A, entries in B pointing at a record that doesn't exist, duplicate B entries for the same record, and value mismatches — with numeric, date, case, and whitespace-aware equality so `100` vs `100.0` or `CONFIRMED` vs `confirmed` don't get flagged as false disagreements.
- **Display**: one table, every disagreement, with reason / System A value / System B value / location. Filterable by reason, sortable by value. No CSS effort spent beyond making it readable, per the brief.
- **Tests**: one test per disagreement type (missing in A, missing in B, duplicate in B, numeric difference, rounding/formatting edge cases, dirty-data handling).

## What I deliberately did not build

- Visual design beyond a plain, readable table.
- Authentication.
- Performance work — 120 rows per file.
- CSV export / merge-back — nice to have, cut for time.

## What's incomplete / known gap

**Tenant (org) isolation is not properly enforced.** The brief's core ask is "find the disagreements, do not leak across the boundary," and right now the comparison runs across all orgs without scoping queries by tenant. Locations map to orgs (`locations.csv`), so the data needed to enforce this is present — I just didn't wire the enforcement through the API layer given the time box. This is the first thing I'd fix with more time, and I'm flagging it here rather than glossing over it, since it's a real gap against the brief, not a stylistic choice.

## How to run

Backend (Django):
```bash
cd backend
pip install django djangorestframework pandas
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Frontend (React):
```bash
cd frontend
npm install
npm start
```

Open `http://localhost:3000`, upload `system_a.csv`, `system_b.csv`, and optionally `locations.csv`, then compare.

*(No virtualenv or `requirements.txt` was used for this submission — dependencies are installed directly via pip as listed above. For anything beyond a quick take-home I'd normally pin dependencies in a `requirements.txt` or use Poetry, and I'm happy to talk through that tradeoff on the call.)*

## Decisions (see DECISIONS.md for full list)

- SQLite over Postgres — simple setup, sufficient for 120 rows.
- Decimal-based numeric comparison over string comparison — `100.0` should equal `100`.
- Flag duplicates in System B rather than auto-resolving them — safer to surface than to silently pick a "winner."
- One disagreement row per record (not per field) in the summary table, with per-field detail available on expand — keeps the table scannable.

## Answers to the three questions

**a. One thing the AI agent got wrong, and how I noticed:**
[Fill in honestly — e.g. a specific normalization edge case it missed, or a disagreement type it initially miscounted. Pick a real example from your own debugging, since you'll be asked to defend it on the call.]

**b. Least confident part of the submission:**
Tenant isolation, for the reason above — it's the part of the brief I have the least evidence I got right, because I didn't fully build it.

**c. With a second day, first fix:**
Wire org scoping through the query layer so results are properly isolated per tenant, then add CSV export of the merged/reconciled data.

---
*Built with Django + React. Time spent: ~1 working day, per the brief's time box.*
