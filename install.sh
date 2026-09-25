#!/usr/bin/env bash
# Install the five skills for Claude Code: link them into ~/.claude/skills (so `git pull` updates them), set up each
# skill's Python environment, and check the machine. Nothing is deleted or overwritten: an existing folder with the
# same name stops the install.
#
#   ./install.sh            link the skills (recommended)
#   ./install.sh --copy     copy them instead
#   ./install.sh --test     also run the offline test suites
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mode=link
run_tests=0
for arg in "$@"; do
  case "$arg" in
    --copy) mode=copy ;;
    --test) run_tests=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

command -v python3 >/dev/null || { echo "python3 is required (3.9 or newer)" >&2; exit 1; }
python3 - <<'PY' || exit 1
import sys
if sys.version_info < (3, 9):
    sys.exit("python3 3.9 or newer is required, found " + sys.version.split()[0])
PY

mkdir -p "$dest"
for skill in codex-imagegen codex-design natural-copy agy-watch-video remotion-broll; do
  target="$dest/$skill"
  if [ -L "$target" ]; then
    if [ "$(cd "$target" && pwd -P)" = "$(cd "$here/$skill" && pwd -P)" ]; then
      echo "ok      $skill already linked"
      continue
    fi
    echo "stop    $target links somewhere else; remove that link yourself, then run again" >&2
    exit 1
  fi
  if [ -e "$target" ]; then
    echo "stop    $target already exists; move it away yourself, then run again (nothing was changed)" >&2
    exit 1
  fi
  if [ "$mode" = link ]; then
    ln -s "$here/$skill" "$target"
    echo "linked  $skill"
  else
    rsync -a --exclude .venv --exclude __pycache__ --exclude .DS_Store "$here/$skill/" "$target/"
    echo "copied  $skill"
  fi
done

echo "setting up Python environments (Pillow, segno, pypdf, uharfbuzz, fontTools)"
# each doctor builds its skill's environment first, then reports what is still missing on this machine (the Codex CLI,
# Chrome); a missing tool is a note here, not a failed install
python3 "$dest/codex-imagegen/scripts/codex_image.py" doctor --setup || \
  echo "note    codex-imagegen is set up; its doctor lists what is still missing above (usually the Codex CLI)"
python3 "$dest/codex-design/scripts/design.py" doctor --setup || \
  echo "note    codex-design is set up; its doctor lists what is still missing above"
python3 "$dest/agy-watch-video/scripts/watch_video.py" doctor --setup || \
  echo "note    agy-watch-video is set up; its doctor lists what is still missing above (usually ffmpeg or the Antigravity CLI)"

echo "checking the machine"
python3 "$dest/codex-design/scripts/design.py" doctor || true
command -v codex >/dev/null || echo "note    the Codex CLI is not installed: image generation and the judges need it (then run: codex login)"
[ -d "/Applications/Google Chrome.app" ] || command -v google-chrome >/dev/null || \
  echo "note    Google Chrome was not found: the Compose route renders with headless Chrome"
command -v swiftc >/dev/null || echo "note    swiftc was not found: install the Xcode Command Line Tools for on-device OCR"
command -v ffmpeg >/dev/null || echo "note    ffmpeg was not found: agy-watch-video needs it (brew install ffmpeg)"
command -v agy >/dev/null || [ -x "$HOME/.local/bin/agy" ] || \
  echo "note    the Antigravity CLI (agy) is not installed: agy-watch-video needs it (https://antigravity.google/download#antigravity-cli, then run agy once to sign in)"
command -v node >/dev/null || echo "note    Node.js was not found: remotion-broll needs Node 22.6 or newer (https://nodejs.org)"

if [ "$run_tests" = 1 ]; then
  python3 -m unittest discover -s "$dest/codex-design/tests"
  python3 -m unittest discover -s "$dest/codex-imagegen/tests"
  python3 -m unittest discover -s "$dest/agy-watch-video/tests"
  python3 -m unittest discover -s "$dest/remotion-broll/tests"
fi
echo "done: restart Claude Code so it picks up the skills"
