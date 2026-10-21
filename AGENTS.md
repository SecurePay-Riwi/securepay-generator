# AGENTS.md: securepay-generator

Context for AI assistants and new contributors. Keep it short; the full
documentation is at https://securepay-riwi.github.io/SecurePay/.

## What this repository is

Simulated wallet core: reads the seed from PostgreSQL and streams transactions with one labeled fraud pattern per antifraud rule (plus controls and defects), to files or to the decision engine over HTTP.

It is one of the SecurePay-Riwi repositories. The others are securepay-seed,
securepay-generator, securepay-csv and securepay-apis (simulated data sources)
and SecurePay (decision engine, consumers, infrastructure, documentation).

## Commands

Run everything from the repository root.

```bash
uv sync                 # install (Python 3.12, securepay-shared from PyPI)
uv run pytest           # tests; they need no database, internet or LocalStack
uv run python -m securepay_generator                 # needs the seed loaded
uv run python -m securepay_generator.fetch_rates     # refresh the rates file; needs internet
```

## Structure rules (mandatory)

Follow these rules for every change. If a change seems to need breaking one,
stop and ask instead of working around it.

1. All code lives in the single package `src/securepay_generator/`. Do not add top-level
   Python folders or a second package.
2. Each component is a subpackage of `securepay_generator`. A new component gets its own
   subpackage, with an entry point in `__main__.py` when it is run with
   `python -m`.
3. Tests live in `tests/`, mirroring the subpackages (`tests/<component>/`).
   Never put tests inside `src/`.
4. Imports are absolute and start with `securepay_generator` or `securepay_shared`.
   Never import code from another SecurePay repository and never copy
   `securepay_shared` code here: add what is missing to that package instead.
5. Repositories exchange data only through files or S3, never through imports.
   A path to another repository is a default that an environment variable can
   override (for example `../securepay-generator/generated`).
6. Generated data and downloads (`generated/`, `data/`) are never committed.
7. Dependencies are managed only with uv (`uv add`, `uv add --dev`); commit
   `pyproject.toml` and `uv.lock` together.
8. Every environment variable the code reads is listed in `.env.example`, and
   `.env.example` lists nothing the code does not read.
9. When a command, variable or folder changes, update README.md and this file
   in the same change.

## Conventions

- Commit messages and pull requests in English, conventional commits
  (`feat:`, `fix:`, `refactor:`, `docs:`, `build:`, `chore:`).
- Existing Spanish names and comments stay; translate them only when editing
  that code anyway. Database table and column names stay as they are.
- Reproducibility: `SEED=42` and `FECHA_REFERENCIA=2026-10-01` (from
  `securepay_shared.config`) must give the same data on Windows and Linux.

## Known traps

- With `SEED=42` and default settings the run must print `Listo: 1036 eventos`.
  If a change alters that number, it changes the data every other piece uses.
- Balances are kept in memory; the generator does not write to PostgreSQL.
- `src/securepay_generator/data/tasas_2026-10.json` is the one committed data
  file (rule 6 is about generated output): every run must use the same rates.
  Each amount is converted with the rate of its transaction date
  (`money.Tasas.del_dia`), never with the rate of the day a pattern starts.
- securepay-csv reads `generated/instance-*/events.jsonl`; keep that format.

## Where to read more

Read these before changing the design, not to work on the code:

- Architecture overview: https://securepay-riwi.github.io/SecurePay/docs/architecture/overview
- Decisions (ADRs): https://securepay-riwi.github.io/SecurePay/docs/architecture/decisions
- Team decisions: https://securepay-riwi.github.io/SecurePay/docs/architecture/team-decisions
- Open questions: https://securepay-riwi.github.io/SecurePay/docs/architecture/open-questions
- Data flow: https://securepay-riwi.github.io/SecurePay/docs/architecture/data-flow
- Logbook: https://securepay-riwi.github.io/SecurePay/docs/logbook
- This component: https://securepay-riwi.github.io/SecurePay/docs/components/generator
