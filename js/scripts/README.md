# JavaScript SDK Example Scripts

Run from the repository `js/` directory.

## Prerequisites

```bash
npm install
npm run build
export STRUAI_API_KEY=your_api_key
export STRUAI_BASE_URL=https://api.stru.ai  # optional
export STRUAI_PDF=/absolute/path/to/structural.pdf
```

## Scripts

```bash
# Tier 1 drawings flow
STRUAI_PAGE=12 node scripts/drawings_quickstart.mjs

# Full Tier 1 + Tier 2 workflow
STRUAI_PAGE=12 node scripts/projects_workflow.mjs

# Full workflow + cleanup
STRUAI_PAGE=12 STRUAI_CLEANUP=1 node scripts/projects_workflow.mjs
```
