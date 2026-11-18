# Grok Bot (bash)

A shell teammate that chats with Grok. Each bot keeps a memory file and a workspace. Shell commands and file writes run only after you approve them.

This is not the Grok Bot desktop app. It has no cloud computer and does not replace the `grok-bot` package.

## Requirements

- bash 4.2 or newer
- `curl`
- `jq`
- `coreutils`
- `ca-certificates`
- An [xAI API key](https://console.x.ai/team/default/api-keys)

## Setup

```bash
export XAI_API_KEY="your_api_key"
./grok-bot
```

The first run creates a bot named Grok Bot. Bots are stored in `$XDG_DATA_HOME/grok-bot`, or `~/.local/share/grok-bot` when `XDG_DATA_HOME` is unset.

| Variable | Default | Purpose |
| --- | --- | --- |
| `XAI_API_KEY` | unset | API key. Required for chat. |
| `GROK_BOT_MODEL` | `grok-4.7` | Model sent to the Responses API. |
| `GROK_BOT_API` | `https://api.x.ai/v1` | API base URL. |
| `GROK_BOT_YES` | `0` | Set to `1` to approve commands and writes without a prompt. |

## Usage

```bash
./grok-bot                         # chat with the current bot
./grok-bot "Summarize this folder"
./grok-bot new "Notes Bot" --job "Keep notes"
./grok-bot list
./grok-bot use "Notes Bot"
./grok-bot memory                  # print memory
./grok-bot memory edit             # open memory in $EDITOR
./grok-bot routine add morning "Say good morning"
./grok-bot routine list
./grok-bot routine run morning
./grok-bot routine remove morning
./grok-bot self-test               # local checks, no API call
```

Options come before the command or message:

- `--bot NAME` uses that bot for one invocation.
- `--yes` approves local commands and file writes without asking.
- `--data-dir DIR` stores bots in `DIR`.
- `--` ends option parsing, so a message can start with a dash.

In chat, type `/help`. `/quit` leaves. `/new`, `/use`, `/job`, `/memory`, `/bots`, and `/routine` match the commands above.

A routine is a saved prompt. Run it from cron with the bot slug:

```bash
0 8 * * 1-5 /path/to/grok-bot --bot notes-bot routine run morning
```

Add `--yes` only when that job should run shell commands with nobody there to approve them.

## Marketplace sync

Public agents from the [Grok Bot marketplace](https://x.ai/bot/marketplace) are stored in `marketplace/`. Refresh them, then commit and push this repo to keep GitHub in sync:

```bash
python3 scripts/pull-marketplace.py
```

Each file under `marketplace/agents/` is the public template: name, job blurb, skills, routines, and memories. The shell reads those files directly:

```bash
./grok-bot agents
./grok-bot agent show dr-eggbot-v2
./grok-bot agent use dr-eggbot-v2
```

`agent use` creates a local bot from that JSON: the description becomes the job, memories are saved, routines are saved, and skills are included in every reply. Import into the Grok Bot desktop app still happens on x.ai.

## Development

`make lint`, `make test`, and `make deb` make no xAI API call.

```bash
make lint
make test
make deb
sudo make install
```

`make lint` runs shellcheck on `grok-bot`. `make test` runs `./grok-bot self-test`.

## Package

The Debian source is native. The binary package is `grok-bot-bash` and installs `/usr/bin/grok-bot-bash`. It does not take the `grok-bot` name used by the desktop app.

`make deb` reads the version from `debian/changelog`, copies this tree to `/tmp/grok-bot-bash-<version>`, and runs `dpkg-buildpackage -us -uc --ignore-builtin-builddeps`. This package does not compile, so the build does not need `build-essential`. The `.deb` is left in the current directory. `sudo make install` builds that package and installs it with `dpkg -i`.

Hand build for the 1.0.0 changelog entry. `dpkg-buildpackage` writes the `.deb` next to the build directory:

```bash
cp -a grok-bot-bash /tmp/grok-bot-bash-1.0.0
cd /tmp/grok-bot-bash-1.0.0
dpkg-buildpackage -us -uc --ignore-builtin-builddeps
sudo dpkg -i ../grok-bot-bash_1.0.0_all.deb
```

## License

MIT. See [LICENSE](LICENSE).
