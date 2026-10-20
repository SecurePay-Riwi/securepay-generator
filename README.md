# securepay-generator

Synthetic transaction and entity generator for the SecurePay Antifraude project.

## Sources

| ID | Source | Type | Frequency |
|----|--------|------|-----------|
| F3 | Simulated transaction stream (P2P, QR, RECARGA, RETIRO) | Stream simulado | Continuous |

Reproduces fraud patterns: account takeover, money mule (receives and withdraws in < 30 min),
and amount splitting. Fraud rate is configurable.

## Setup

```bash
git clone https://github.com/SecurePay-Riwi/securepay-generator.git
cd securepay-generator
cp .env.example .env
uv sync
```

## Usage

```bash
# Start the transaction stream
uv run python -m generator

# Run tests
uv run pytest
```

## Dependencies

- [`securepay-shared`](https://pypi.org/project/securepay-shared/) — shared models, DB and config
