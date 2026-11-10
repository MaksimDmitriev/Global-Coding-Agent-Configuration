#!/usr/bin/env bash
# Link this checkout's shared instructions and completed skills into agent profiles.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: install.sh --agent codex|claude|all [--dry-run] [--backup] [--home-dir PATH]

  --agent TARGET   Install for Codex, Claude Code, or both (all). Required.
  --dry-run        Preview changes without creating directories, links, or backups.
  --backup         Move conflicting destinations aside before linking them.
  --home-dir PATH  Use an alternate absolute home path, ignoring profile overrides.
  -h, --help       Show this help.

Existing configuration is preserved by default. Empty skills are skipped.
EOF
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

agent=''
dry_run=false
backup=false
install_home="${HOME:-}"
custom_home=false
while (( $# > 0 )); do
    case "$1" in
        --agent|--home-dir)
            (( $# >= 2 )) || fail "$1 requires a value. See --help."
            if [[ "$1" == --agent ]]; then
                [[ -z "$agent" ]] || fail 'Specify --agent only once.'
                agent="$2"
            else
                install_home="$2"
                custom_home=true
            fi
            shift 2
            ;;
        --dry-run) dry_run=true; shift ;;
        --backup) backup=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail "Unknown argument: $1. See --help." ;;
    esac
done
case "$agent" in
    codex|claude|all) ;;
    *) usage >&2; fail 'Choose --agent codex, claude, or all.' ;;
esac
[[ "$install_home" == /* ]] || fail 'The home directory must be an absolute path.'

script_path="${BASH_SOURCE[0]}"
[[ "$script_path" == /* ]] || script_path="$PWD/$script_path"
script_dir="$(cd -- "$(dirname -- "$script_path")" && pwd -P)"
repo_root="$(cd -- "$script_dir/.." && pwd -P)"
[[ -s "$repo_root/AGENTS.md" ]] || fail "Missing or empty instructions: $repo_root/AGENTS.md"

codex_dir="$install_home/.codex"
claude_dir="$install_home/.claude"
if ! "$custom_home"; then
    codex_dir="${CODEX_HOME:-$codex_dir}"
    claude_dir="${CLAUDE_CONFIG_DIR:-$claude_dir}"
fi

sources=()
destinations=()
plan_count=0
add_link() {
    sources[plan_count]="$1"
    destinations[plan_count]="$2"
    plan_count=$((plan_count + 1))
}

if [[ "$agent" == codex || "$agent" == all ]]; then
    [[ "$codex_dir" == /* ]] || fail 'CODEX_HOME must be an absolute path.'
    add_link "$repo_root/AGENTS.md" "$codex_dir/AGENTS.md"
fi
if [[ "$agent" == claude || "$agent" == all ]]; then
    [[ "$claude_dir" == /* ]] || fail 'CLAUDE_CONFIG_DIR must be an absolute path.'
    add_link "$repo_root/AGENTS.md" "$claude_dir/CLAUDE.md"
fi
for skill_dir in "$repo_root"/skills/*; do
    [[ -d "$skill_dir" ]] || continue
    if [[ ! -s "$skill_dir/SKILL.md" ]]; then
        printf 'SKIP %s (missing or empty SKILL.md)\n' "${skill_dir##*/}"
        continue
    fi
    if [[ "$agent" == codex || "$agent" == all ]]; then
        add_link "$skill_dir" "$install_home/.agents/skills/${skill_dir##*/}"
    fi
    if [[ "$agent" == claude || "$agent" == all ]]; then
        add_link "$skill_dir" "$claude_dir/skills/${skill_dir##*/}"
    fi
done

exists() { [[ -e "$1" || -L "$1" ]]; }
is_current() { [[ "$1" -ef "$2" ]]; }

# Check every destination before making changes, including obstructed parents.
conflicts=0
for (( i=0; i<plan_count; i++ )); do
    destination="${destinations[i]}"
    parent="$(dirname -- "$destination")"
    while [[ ! -d "$parent" ]]; do
        if exists "$parent"; then
            printf 'CONFLICT %s must be a directory.\n' "$parent" >&2
            conflicts=$((conflicts + 1))
            break
        fi
        parent="$(dirname -- "$parent")"
    done
    if exists "$destination" && ! is_current "$destination" "${sources[i]}" && ! "$backup"; then
        printf 'CONFLICT %s already exists.\n' "$destination" >&2
        conflicts=$((conflicts + 1))
    fi
done
if (( conflicts > 0 )); then
    fail 'No changes made. Resolve conflicting paths or use --backup for destination conflicts.'
fi

backup_stamp="$(date +%Y%m%d-%H%M%S).$$"
for (( i=0; i<plan_count; i++ )); do
    source="${sources[i]}"
    destination="${destinations[i]}"
    if is_current "$destination" "$source"; then
        printf 'UNCHANGED %s\n' "$destination"
        continue
    fi
    if exists "$destination"; then
        "$backup" || fail "Destination appeared during installation: $destination"
        backup_path="$destination.backup.$backup_stamp"
        suffix=0
        while exists "$backup_path"; do
            suffix=$((suffix + 1))
            backup_path="$destination.backup.$backup_stamp.$suffix"
        done
        if "$dry_run"; then
            printf 'WOULD BACK UP %s -> %s\n' "$destination" "$backup_path"
        else
            mv -- "$destination" "$backup_path"
            printf 'BACKED UP %s -> %s\n' "$destination" "$backup_path"
        fi
    fi
    if "$dry_run"; then
        printf 'WOULD LINK %s -> %s\n' "$destination" "$source"
    else
        mkdir -p -- "$(dirname -- "$destination")"
        ln -s -- "$source" "$destination"
        printf 'LINKED %s -> %s\n' "$destination" "$source"
    fi
done

if "$dry_run"; then
    printf 'Dry run complete. No changes made.\n'
else
    printf 'Installation complete. Start a new agent session to load the configuration.\n'
fi
