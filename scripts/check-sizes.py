#!/usr/bin/env python3
"""
SSI Dashboard — Data Size Monitor
Checks all ssi-data.json files against GitHub's size limits.

GitHub limits:
  - File warning: 50 MB
  - File hard limit: 100 MB
  - Repo recommended: < 5 GB

Usage: python3 scripts/check-sizes.py
"""
import os, json

WARN_MB = 50
CRITICAL_MB = 100

countries = ['france','italy','uk','spain','germany','switzerland','austria',
             'us','canada','japan','australia','chile','greece','turkey','ireland']

total_size = 0
issues = []

for c in countries:
    filepath = f'{c}/ssi-data.json'
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        size_mb = size / (1024 * 1024)
        total_size += size
        
        status = '\u2705' if size_mb < WARN_MB else '\u26A0\uFE0F' if size_mb < CRITICAL_MB else '\u274C'
        print(f'  {status} {c:15s} {size_mb:6.1f} MB')
        
        if size_mb >= WARN_MB:
            issues.append(f'{c}: {size_mb:.1f} MB (>={WARN_MB} MB warning)')
    else:
        print(f'  \u2753 {c:15s} not found')

print(f'\n  Total: {total_size / (1024*1024):.1f} MB across {len(countries)} countries')

if issues:
    print(f'\n  \u26A0\uFE0F {len(issues)} file(s) near or over GitHub size limit:')
    for issue in issues:
        print(f'    - {issue}')
    print(f'\n  Recommendation: Consider Git LFS for files > {WARN_MB} MB')
    print(f'  To enable: git lfs track "*/ssi-data.json" && git lfs install')
else:
    print(f'\n  \u2705 All files within GitHub size limits')
