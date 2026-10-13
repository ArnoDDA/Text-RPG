# Portable project and privacy

Open this folder as a local Codex project and run `npm run start`. The server
uses whichever Codex account is signed into that computer. The project does not
contain an account token, API key, or personal save.

By default, personal saves are outside the project at:

```text
~/.codex-rpg-memory/campaign.sqlite3
```

One-click backups are stored with owner-only permissions under:

```text
~/.codex-rpg-memory/backups/
```

Export downloads a transactionally consistent portable SQLite copy. Import
validates the file, applies known schema migrations, makes an automatic
pre-import backup, and then replaces the live database atomically.

The local server listens only on `127.0.0.1`, and the save directory and SQLite
file use owner-only POSIX permissions when the operating system supports them.
Set `CAMPAIGN_DB` or `CODEX_RPG_DATA_DIR` before starting if you want another
private location.

The local database is ordinary SQLite data. Use FileVault or equivalent
full-disk encryption for protection against device loss or another user with
disk access. Narration prompts must still be sent to the Codex service, so this
project cannot override service-level retention, security controls, or lawful
account auditing.
