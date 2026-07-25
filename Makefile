.PHONY: demo

demo:
	@command -v vhs >/dev/null || { echo "error: vhs is required to render the demo"; exit 1; }
	@command -v eza >/dev/null || { echo "error: eza is required to display the project tree"; exit 1; }
	@test -x .venv/bin/grem || { echo "error: .venv/bin/grem is missing; run 'uv sync' first"; exit 1; }
	vhs .github/assets/demo.tape
