#!/bin/zsh
set -eu

PROJECT_DIR="${0:A:h:h}"
USER_HOME="$(/usr/bin/dscl . -read "/Users/$(/usr/bin/id -un)" NFSHomeDirectory | /usr/bin/awk '{print $2}')"
export HOME="$USER_HOME"
export CODEX_HOME="$HOME/.codex"
export PATH="/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export CODEX_CLI="/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"

cd "$PROJECT_DIR"
exec node server.mjs
