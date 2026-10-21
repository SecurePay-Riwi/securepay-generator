# securepay-generator

Synthetic transaction stream for the SecurePay Antifraude project. It acts as
the wallet's core system.

## What it does

Reads the master data (users, accounts, devices, merchants) that **securepay-seed**
loads into PostgreSQL and produces a stream of transactions with one fraud
pattern per antifraud rule, each with its control case:

| Pattern | Rule it should trigger |
|---------|------------------------|
| `VELOCITY` | More than 5 outgoing P2P transfers in 10 minutes |
| `MULE` | Receives 3 or more transfers and withdraws 80 % or more in under 30 minutes |
| `ACCOUNT_TAKEOVER` | Device change + password change + transaction over USD 200 in under 1 hour |
| `RESTRICTED_LIST` | Document on the sanctions / PEP list |
| `SPLITTING` | 3 or more transactions under the daily limit that together exceed it |

It also injects three defects: resends, out-of-order events and extra decimals.
With seed 42 and default settings it prints `Listo: 1036 eventos`.

## Setup

```bash
git clone https://github.com/SecurePay-Riwi/securepay-generator.git
cd securepay-generator
cp .env.example .env   # DATABASE_URL points to the Compose PostgreSQL (port 5433)
uv sync                # installs securepay-shared from PyPI
```

The seed must have run first (**securepay-seed**).

## Exchange rates

Accounts hold COP, USD, EUR or JPY, while amounts and rule thresholds are
thought in USD. The generator converts **each amount with the Frankfurter rate
of its own transaction date**, from `src/securepay_generator/data/tasas_2026-10.json`
(one entry per published day since the reference date, 2026-10-01; Frankfurter
blends several providers and usually publishes every day, weekends included).
A day without a rate, or not published yet, uses the last earlier one, the
same way the decision engine reads the DynamoDB table.

The file is committed on purpose, so every run gives the same data without
internet. To add the days published since the last update:

```bash
uv run python -m securepay_generator.fetch_rates   # needs internet
```

Then commit the updated file. New rates change the amounts of the days they
cover, so do it on purpose, not on every run.

## Local services

PostgreSQL (port 5433) and LocalStack run with the Docker Compose of the
[SecurePay](https://github.com/SecurePay-Riwi/SecurePay) repository (`docker compose up -d`).

## Usage

```bash
# Write the events to files (generated/instance-0/)
uv run python -m securepay_generator

# Send the events to the decision engine
GEN_OUTPUT=http uv run python -m securepay_generator          # bash
$env:GEN_OUTPUT="http"; uv run python -m securepay_generator  # PowerShell

# Run the tests (no database needed)
uv run pytest
```

### Output files (`generated/instance-0/`)

| File | Contents |
|------|----------|
| `events.jsonl` | Events as the engine receives them |
| `labels.jsonl` | Pattern, expected rule and engine response per event |
| `generation_report.json` | Counts by pattern, type and defect |

**securepay-csv** reads `events.jsonl` to build the partner statements.

## Key environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEN_OUTPUT` | `file` | `file` writes to disk; `http` sends to the engine |
| `GEN_ENGINE_URL` | `http://localhost:8000` | Decision engine URL when `GEN_OUTPUT=http` |
| `GEN_RATE` | `50` | Transactions per second |
| `GEN_FRAUD_PERCENTAGE` | `5` | Percentage of events that carry a fraud pattern |
| `SEED` | `42` | Random seed; change it for a different dataset |

The full list is in `.env.example`.

## Repository layout

```
src/securepay_generator/
├── __main__.py     # entry point: python -m securepay_generator
├── config.py       # environment variables and modes
├── catalog.py      # reads the seed from PostgreSQL once
├── core.py         # simulated wallet core (balances in memory)
├── patterns.py     # one fraud pattern per rule, with controls
├── defects.py      # resends, out-of-order, extra decimals
├── money.py        # currency conversion and rounding
├── sender.py       # file or HTTP output
├── fetch_rates.py  # refreshes data/tasas_2026-10.json
└── data/           # exchange rates per day, versioned on purpose
tests/
```

All code lives in one package under `src/`; tests mirror it under `tests/`.
Read [AGENTS.md](AGENTS.md) before adding folders or modules.

## Working with the other repositories

The repositories pass data through files (and through S3 in AWS), never through
imports. Clone them side by side in the same folder and each one finds the files
the others produce, without setting paths by hand:

```
SecurePay-Riwi/
├── securepay-seed/        # PostgreSQL master data + restricted list export
├── securepay-generator/   # reads the seed, writes generated/instance-*/
├── securepay-csv/         # Kaggle downloads + partner statements (reads the generator)
└── securepay-apis/        # restricted-list service (reads the seed export)
```

Environment variables still override every path (see `.env.example`).

## Dependencies

- [`securepay-shared`](https://pypi.org/project/securepay-shared/): shared models, database and config
- PostgreSQL with the seed loaded (**securepay-seed**)
- Decision engine on `localhost:8000` when `GEN_OUTPUT=http`


## Docker

The Python 3.12 image with uv defaults to running the transaction generator:

```bash
docker build -t securepay-generator .
```

Provide `DATABASE_URL` for the seeded PostgreSQL database. For HTTP output,
set `GEN_OUTPUT=http` and `GEN_ENGINE_URL` to an engine URL reachable from
the container. Mount a writable volume at `/app/generated` to share event files
with the partner-statements job.
