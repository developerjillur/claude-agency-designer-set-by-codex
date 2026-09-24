# Running codex-imagegen on a cloud server (headless)

The Codex engine needs only: the Codex CLI, a ChatGPT login stored by `codex login`, Python 3.9+ and outbound HTTPS. No OpenAI API key.

## 1. Install and log in

```bash
# official installer (the same one `codex update` uses); alternative: npm install -g @openai/codex
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# headless login: prints a URL + one-time code; open it on any device and approve
codex login --device-auth

# must print: Logged in using ChatGPT
codex login status

# must show: image_generation  stable  true
codex features list | grep image_generation
```

Requirements: a ChatGPT plan that includes Codex (the Free plan has no image tool). API-key logins (`codex login --with-api-key`) do **not** expose Codex's built-in image tool.

## 2. Install the skill

```bash
# from your laptop: copy the skill without the macOS venv and caches
rsync -a --exclude .venv --exclude __pycache__ ~/.claude/skills/codex-imagegen user@server:~/.claude/skills/

# on the server
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py doctor --setup      # skill venv with Pillow
sudo apt install -y librsvg2-bin                                                     # SVG logos -> favicons/OG
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py doctor --image-smoke # one real image end to end
python3 -m unittest discover -s ~/.claude/skills/codex-imagegen/tests                # offline suite
```

`doctor` reports these, and `ready_for_codex_engine: true` covers the first two only:
- the login and the image feature flag;
- the Codex binary and version;
- Pillow (WebP/AVIF) and the SVG rasterizer;
- the locales data and the Codex timezone;
- the skill version.

`--image-smoke` proves the whole image path, so run it after every `codex update`.

## 3. Use it

- From Claude Code on the server: just ask for an image; the skill runs the script.
- From a plain shell / cron / CI on the server:

```bash
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py generate --workdir /srv/project --aspect 16:9 --size 1920x1080 --prompt "..."
```

Images land in `<workdir>/output/imagegen/` with a `.meta.json` each; Codex keeps its originals in `~/.codex/generated_images/<thread>/`.

## 4. Keep it healthy

| Item | Why |
|---|---|
| `codex update` regularly | Newer Codex agent models (e.g. `gpt-6-astra`) reject old CLIs with "requires a newer version of Codex" |
| `doctor --setup` | Pillow in the skill venv: finish, transparent cleanup, export/favicon/og/cutout/audit and `--size` crops on Linux |
| Server `~/.codex/config.toml` | Codex defaults. `--codex-model` affects agent mode only; fast-mode image sessions use the config default |
| Usage limits | Watch `telemetry.plan_usage_percent` in the output; cap a run with `--max-images`; put several images in one `batch` |
| `~/.codex/auth.json` | Holds the login tokens: keep it private (`chmod 600`, single-user account, never commit or copy it around) |

## 5. Optional API engine on a server

Only if you want explicit `gpt-image-2.5-sunburst` / `-flare` routing: provide `OPENAI_API_KEY` through the server's secret manager or environment (never in a repo), then add `--engine api`. The organization may need API Organization Verification for GPT Image models.
