# grem quick-start walkthrough
# Regenerate with: make demo
# https://github.com/ewiger/grem

Output .github/assets/demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 760
Set Padding 24
Set TypingSpeed 70ms
Set Theme "Dracula"

# --- Setup (hidden): isolated working dir, clean prompt, grem on PATH ---
Hide
Type `export PATH="$PWD/.venv/bin:$PATH"` Enter
Type `cd "$(mktemp -d)"` Enter
Type `export PS1='\[\033[36m\]\$ \[\033[0m\]'` Enter
Type "clear" Enter
Show

Sleep 1s

# 1. Stamp a new project from the bundled python template.
#    init prompts for a project name; press Enter to accept the default.
Type "grem init demo" Sleep 400ms Enter
Sleep 1500ms
Enter
Sleep 3s

# 2. Step inside the stamped project
Type "cd demo" Sleep 300ms Enter
Sleep 1500ms

# 3. Show the generated project structure
Type "eza --tree --level=2 --all" Sleep 400ms Enter
Sleep 4s

# 4. Print (and copy) the agent-alignment prompt
Type "grem agent --copy" Sleep 400ms Enter
Sleep 9s

# 5. Print a semantic-diff prompt comparing two project scopes
Type "grem diff doc/models src" Sleep 400ms Enter
Sleep 11s
