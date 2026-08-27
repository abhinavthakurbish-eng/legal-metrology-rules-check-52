#!/usr/bin/env bash
set -o errexit

pip install --no-cache-dir --upgrade pip setuptools wheel
pip install --no-cache-dir -r requirements.txt

mkdir -p uploads generated_reports static/annotated static/samples database
