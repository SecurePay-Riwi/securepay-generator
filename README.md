# securepay-generator

Synthetic transaction stream generator for the SecurePay Antifraude project.

## Data sources

| ID | Source | Type |
|----|--------|------|
| F3 | Simulated transaction stream | Generator — acts as the wallet's core system |

## What it does

Reads master data (users, accounts, devices, merchants) from PostgreSQL and produces
a stream of transactions with realistic fraud patterns:

| Pattern | Rule triggered |
|---------|---------------|
| `VELOCITY` | > 5 outgoing P2P transfers in 10 min (RN-02) |
| `MULE` | Receives ≥ 3 transfers + withdraws ≥ 80 % in < 30 min (RN-03) |
| `ACCOUNT_TAKEOVER` | Device change + password change + transaction > USD 200 in < 1 h (RN-07) |
| `RESTRICTED_LIST` | Document on sanctions/PEP list (RN-06) |
| `SPLITTING` | ≥ 3 transactions under daily limit that together exceed it (RN-05) |

With seed 42 and default settings: **1 035 events**, finishing in `Listo: 1035 eventos`.

## Setup

```bash
git clone https://github.com/SecurePay-Riwi/securepay-generator.git
cd securepay-generator
cp .env.example .env   # set DATABASE_URL
uv sync                # installs securepay-shared from PyPI automatically
```

Requires the seed to have been run first (securepay-seed repo).

## Usage

```bash
# Write events to files (generated/instance-0/)
uv run python -m generators

# Send events to the decision engine in real time
GEN_OUTPUT=http uv run python -m generators   # bash
$env:GEN_OUTPUT="http"; uv run python -m generators  # PowerShell

# Run tests
uv run pytest
```

### Output files (`generated/instance-0/`)

| File | Contents |
|------|----------|
| `events.jsonl` | Events as the engine would receive them |
| `labels.jsonl` | Pattern + expected rule + engine response per event |
| `generation_report.json` | Counts by pattern, type and defect |

## Key environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEN_OUTPUT` | `file` | `file` writes to disk; `http` sends to the engine |
| `GEN_TPS` | `50` | Transactions per second when `GEN_OUTPUT=http` |
| `GEN_FRAUD_RATE` | `0.01` | Fraction of events that carry a fraud pattern |
| `SEED` | `42` | Random seed — change for a different dataset |

## Dependencies

- [`securepay-shared`](https://pypi.org/project/securepay-shared/) — shared models, DB and config
- PostgreSQL with seed data (securepay-seed)
- Decision engine running on `localhost:8000` when `GEN_OUTPUT=http`
