#!/usr/bin/env bash
set -euo pipefail

# Verifies published Python + npm packages in clean temp envs.
#
# Usage:
#   ./scripts/verify_release_install.sh 2.0.0
#
# Optional env:
#   PYPI_PACKAGE=struai
#   PYPI_IMPORT=struai
#   NPM_PACKAGE=struai
#   STRUAI_API_KEY=...
#   STRUAI_BASE_URL=http://localhost:8000
#   STRUAI_PDF=/absolute/path/to/file.pdf
#   STRUAI_PAGE=12

VERSION="${1:-2.0.0}"
PYPI_PACKAGE="${PYPI_PACKAGE:-struai}"
PYPI_IMPORT="${PYPI_IMPORT:-struai}"
NPM_PACKAGE="${NPM_PACKAGE:-struai}"
PAGE="${STRUAI_PAGE:-12}"

WORKDIR="$(mktemp -d -t struai-release-check-XXXXXX)"
PY_DIR="$WORKDIR/python"
JS_DIR="$WORKDIR/js"

cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

mkdir -p "$PY_DIR" "$JS_DIR"

echo "[info] Workdir: $WORKDIR"
echo "[info] Checking Python package: ${PYPI_PACKAGE}==${VERSION}"
python3 -m venv "$PY_DIR/.venv"
# shellcheck disable=SC1091
source "$PY_DIR/.venv/bin/activate"
python -m pip install --upgrade pip >/dev/null
python -m pip install "${PYPI_PACKAGE}==${VERSION}" >/dev/null

PYPI_IMPORT="$PYPI_IMPORT" python - <<'PY'
import importlib
import os

mod_name = os.environ["PYPI_IMPORT"]
mod = importlib.import_module(mod_name)
version = getattr(mod, "__version__", "<missing>")
print(f"[ok] Python import: {mod_name} __version__={version}")
PY

if [[ -n "${STRUAI_API_KEY:-}" && -n "${STRUAI_BASE_URL:-}" && -n "${STRUAI_PDF:-}" ]]; then
  python - <<'PY'
import os
from pathlib import Path

from struai import StruAI

api_key = os.environ["STRUAI_API_KEY"]
base_url = os.environ["STRUAI_BASE_URL"]
pdf = Path(os.environ["STRUAI_PDF"])
page = int(os.environ.get("STRUAI_PAGE", "12"))

if not pdf.exists():
    raise SystemExit(f"PDF not found: {pdf}")

client = StruAI(api_key=api_key, base_url=base_url)
file_hash = client.drawings.compute_file_hash(pdf)
cache = client.drawings.check_cache(file_hash)
if cache.cached:
    drawing = client.drawings.analyze(page=page, file_hash=file_hash)
else:
    drawing = client.drawings.analyze(file=str(pdf), page=page)

print(f"[ok] Python demo smoke: drawing_id={drawing.id} page={drawing.page}")
PY
else
  echo "[warn] Skipping Python demo smoke (set STRUAI_API_KEY, STRUAI_BASE_URL, STRUAI_PDF)."
fi

deactivate

echo "[info] Checking npm package: ${NPM_PACKAGE}@${VERSION}"
cd "$JS_DIR"
npm init -y >/dev/null
npm install "${NPM_PACKAGE}@${VERSION}" >/dev/null

node --input-type=module <<'JS'
import { StruAI } from 'struai';

const client = new StruAI({
  apiKey: process.env.STRUAI_API_KEY || 'windowseat',
  baseUrl: process.env.STRUAI_BASE_URL || 'http://localhost:8000',
});

if (!client || !client.drawings || !client.projects) {
  throw new Error('SDK export shape invalid');
}
console.log('[ok] npm import: StruAI class loaded');
JS

if [[ -n "${STRUAI_API_KEY:-}" && -n "${STRUAI_BASE_URL:-}" && -n "${STRUAI_PDF:-}" ]]; then
  node --input-type=module <<'JS'
import { StruAI } from 'struai';

const client = new StruAI({
  apiKey: process.env.STRUAI_API_KEY,
  baseUrl: process.env.STRUAI_BASE_URL,
});

const pdf = process.env.STRUAI_PDF;
const page = Number(process.env.STRUAI_PAGE || '12');

const fileHash = await client.drawings.computeFileHash(pdf);
const cache = await client.drawings.checkCache(fileHash);
const drawing = cache.cached
  ? await client.drawings.analyze(null, { page, fileHash })
  : await client.drawings.analyze(pdf, { page });

console.log(`[ok] JS demo smoke: drawing_id=${drawing.id} page=${drawing.page}`);
JS
else
  echo "[warn] Skipping JS demo smoke (set STRUAI_API_KEY, STRUAI_BASE_URL, STRUAI_PDF)."
fi

echo "[ok] Release verification complete for version ${VERSION}."
