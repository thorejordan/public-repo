# TryHackMe Module Data Repository

This repository contains structured JSON datasets describing TryHackMe-style cybersecurity learning modules.

## Contents
- `structured_tryhackme_modules.json`: Four richly attributed module entries for analytics and curriculum planning.
- `THM_Rooms_Sheet1.json` and `THM Rooms - Sheet1.txt`: Earlier room exports kept for reference.
- `teams1_raw.txt`, `teams1_1.json`, and `teams1 (1).txt`: Raw and lightly structured snapshots from prior collection runs.

## GUI Availability
There is no graphical user interface in this repository. It provides data files only; no web front-end or desktop client is included.

## Usage
Consume the JSON files directly in data pipelines, BI tools, or recommendation engines. No build or runtime steps are required beyond standard JSON processing.

## Validation
The JSON files are plain UTF-8 documents. You can quickly sanity-check them locally with:

```bash
jq . structured_tryhackme_modules.json >/dev/null
```
