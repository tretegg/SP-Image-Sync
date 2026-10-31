# SP-Image-Sync

Snap a photo of your handwritten to-do list and sync it into [Super Productivity](https://github.com/super-productivity/super-productivity). SP Image Sync sends the image to Gemini to extract task titles and checkbox states, diffs the result against your existing tasks, and applies the changes after you confirm.

## How it works

1. You point it at an image of a whiteboard with a checklist (empty box = not done, filled box = done).
2. Gemini reads the image and extracts each task's title and status.
3. The tool fetches your current tasks from a local Super Productivity API and builds a sync plan:
   - **Add** — whiteboard tasks marked not-done with no matching task
   - **Complete** — open tasks whose whiteboard match is now checked off
   - **Reopen** — tasks that are done in the tracker but unchecked on the whiteboard
4. The plan is printed for review, and applied only after you confirm (or never, with `--dry-run`).

Matching is done by normalizing titles (whitespace stripped, lowercased), so wording has to line up closely between the whiteboard and the tracker.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Super Productivity app running with its local REST API turned on (Settings → Misc → Enable local REST API)
- A Gemini API key

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env` and fill in:

```
SP_TOKEN=<Super Productivity access token (same settings section where you enabled the REST API)>
GEMINI_API_KEY=<your Gemini API key>
```
`GEMINI_API_KEY`: get one from [Google Ai Studio](https://aistudio.google.com/)

Note: Free tier Gemini requests may be used by Google to improve their models.

## Usage

```bash
uv run sp-image-sync path/to/whiteboard.jpg
```

Use `--dry-run` to print the sync plan without prompting or applying it:

```bash
uv run sp-image-sync path/to/whiteboard.jpg --dry-run
```

Example output:

```
ADD: Do homework
COMPLETE: Buy groceries
REOPEN: Call dentist
Apply plan? (y/n):
```

If nothing changed, it just prints `Nothing to sync`.

## Development

```bash
uv run pytest       # tests
uv run ruff check   # lint
uv run pyright       # type check
```

## License

MIT — see [LICENSE](LICENSE).
