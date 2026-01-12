# Xhungus CLI Specification

## Commands

import-archive <path>
- Parses ZIP archive
- Generates inbox + processed notes

update-api
- Fetches new tweets since last run
- Uses same normalization + emit pipeline

enrich-notes
- Invokes Claude Code for interpretation + hub suggestions

report-missing-hubs
- Outputs list of referenced but non-existent hubs
