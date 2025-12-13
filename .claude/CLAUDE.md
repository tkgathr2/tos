# ClaudeCode Project Rules (TOS)

## Output rules
- Do not repeat the same check/command more than once in a single phase.
- When checking something, combine checks into a single command/script.
- Avoid printing intermediate progress lines; print only final summary per phase.

## Command rules
- If you need to confirm paths/files, do it once and cache the result in a file.
- Prefer running a single PowerShell script (wrapper) instead of many Bash calls.

## Stop rules
- If you are about to run the same Bash/PowerShell command again, stop and explain why.
