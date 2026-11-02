#!/usr/bin/env bash
# Copies shared/*.md into every skill's references/ directory.
# Each skill must be self-contained, because `npx skills add --skill <name>` installs only that directory.
# Usage: scripts/sync-shared.sh          copy
#        scripts/sync-shared.sh --check  report copies that differ from shared/ and exit 1
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
check=false
[[ "${1:-}" == "--check" ]] && check=true
status=0

for skill in "$root"/skills/*/; do
  for src in "$root"/shared/*.md; do
    dest="${skill}references/$(basename "$src")"
    if $check; then
      if ! cmp -s "$src" "$dest"; then
        echo "out of sync: ${dest#"$root"/}"
        status=1
      fi
    else
      mkdir -p "${skill}references"
      cp "$src" "$dest"
    fi
  done
done

exit $status
