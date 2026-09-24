#!/usr/bin/env bash
# 本机项目盘点·只读：列出候选项目目录、文件数、近14天修改文件数（注意力铺在几条线上的证据）、最近修改日、git/依赖标志、Claude 记忆目录
# 用法: scan_machine.sh [根目录...]   默认扫 ~ 下常见位置。输出 tsv 到 stdout。macOS/Linux 均可；Windows 请在 WSL 里跑。
# 注意：mtime 可能被拷贝/同步重置；Desktop/Documents/Downloads 在 macOS 上受 TCC 保护，终端没授权时会被扫成 0——见 stderr 的「不可读」提示。
set -u
ROOTS=("$@"); [ ${#ROOTS[@]} -eq 0 ] && ROOTS=("$HOME/Projects" "$HOME/Documents" "$HOME/Desktop" "$HOME/Downloads" "$HOME/code" "$HOME/dev" "$HOME/work" "$HOME/src")
EX=(-not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -not -path '*/.next/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/Library/*')
echo -e "dir\tfiles\tmodified_14d\tfirst_seen\tlast_modified\tgit\tproject_markers"
for R in "${ROOTS[@]}"; do [ -d "$R" ] || continue
  for d in "$R"/*/; do [ -d "$d" ] || continue
    ERRF=$(mktemp); n=$(find "$d" -type f "${EX[@]}" 2>"$ERRF" | wc -l | tr -d ' '); [ -s "$ERRF" ] && echo "# 不可读 $(wc -l <"$ERRF" | tr -d ' ') 处: $d" >&2; rm -f "$ERRF"
    if stat -f '%Sm' "$d" >/dev/null 2>&1; then STATF=(stat -f '%Sm' -t '%Y-%m-%d'); else STATF=(stat -c '%y'); fi   # macOS / Linux
    dates=$(find "$d" -type f "${EX[@]}" -not -name '.DS_Store' -exec "${STATF[@]}" {} + 2>/dev/null | cut -c1-10 | sort)
    first=$(echo "$dates" | head -1); last=$(echo "$dates" | tail -1)
    [ -d "$d/.git" ] && gf=$(git -C "$d" log --reverse --format=%cs 2>/dev/null | head -1) && [ -n "$gf" ] && first="$gf"
    m14=$(find "$d" -type f -mtime -14 "${EX[@]}" -not -path '*/data/*' -not -path '*/logs/*' -not -name '.DS_Store' 2>/dev/null | wc -l | tr -d ' ')
    g=$([ -d "$d/.git" ] && echo git || echo -)
    m=$(ls "$d" 2>/dev/null | grep -E -o '^(package\.json|pyproject\.toml|requirements\.txt|Cargo\.toml|go\.mod|README\.md|CLAUDE\.md|AGENTS\.md|project\.config\.json|docker-compose\.ya?ml)$' | tr '\n' ',' )
    echo -e "${d%/}\t$n\t$m14\t${first:-}\t${last:-}\t$g\t${m:-}"
  done
done
echo "# claude memory dirs:" >&2; ls "$HOME/.claude/projects" 2>/dev/null | sed 's/^/#   /' >&2
echo "# automation:" >&2; crontab -l 2>/dev/null | sed 's/^/#   cron: /' >&2; ls "$HOME/Library/LaunchAgents" 2>/dev/null | sed 's/^/#   launchd: /' >&2
