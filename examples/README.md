# Python SDK Examples

These examples are portable and do not use hardcoded local paths.

## Prerequisites

```bash
pip install struai
export STRUAI_API_KEY=your_api_key
export STRUAI_BASE_URL=https://api.stru.ai  # optional
export STRUAI_PDF=/absolute/path/to/structural.pdf
```

## Scripts

```bash
# Tier 1 drawings flow
python3 test_prod_page12.py --page 12

# Full Tier 1 + Tier 2 workflow
python3 test_prod_page12_full.py --page 12

# Full workflow + cleanup
python3 test_prod_page12_full.py --page 12 --cleanup

# Async full workflow
python3 async_projects_workflow.py --page 12
```
