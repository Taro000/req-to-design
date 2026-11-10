#!/usr/bin/env bash
# Copies shared/*.md into every skill's references/ directory, and shared/scripts/*.py into every skill's scripts/.
# Each skill must be self-contained, because `npx skills add --skill <name>` installs only that directory.
# A skill's scripts/ holds only copies of shared/scripts/: a copy whose original is gone is removed.
# Usage: scripts/sync-shared.sh          copy
#        scripts/sync-shared.sh --check  report copies that differ from shared/ and exit 1
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
check=false
[[ "${1:-}" == "--check" ]] && check=true
status=0

sync_file() {
  local src="$1" dest="$2"
  if $check; then
    if ! cmp -s "$src" "$dest"; then
      echo "out of sync: ${dest#"$root"/}"
      status=1
    fi
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    [[ -x "$src" ]] && chmod +x "$dest"
  fi
  return 0
}

for skill in "$root"/skills/*/; do
  for src in "$root"/shared/*.md; do
    sync_file "$src" "${skill}references/$(basename "$src")"
  done
  for src in "$root"/shared/scripts/*.py; do
    [[ -e "$src" ]] || continue
    sync_file "$src" "${skill}scripts/$(basename "$src")"
  done
  for dest in "${skill}"scripts/*; do
    [[ -f "$dest" ]] || continue
    if [[ ! -e "$root/shared/scripts/$(basename "$dest")" ]]; then
      if $check; then
        echo "not in shared/scripts: ${dest#"$root"/}"
        status=1
      else
        rm "$dest"
      fi
    fi
  done
done

exit $status
