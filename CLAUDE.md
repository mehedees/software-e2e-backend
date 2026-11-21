# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@README.md

## Where docs live

Each fact has one home. Update it there and don't copy it anywhere else.

- **README.md** (imported above): stack, commands, layout, API conventions and commit rules. These are short rules that point into the code.
- **Code comments and docstrings:** how a piece of code works and how to use it. `core/schema/response.py` covers the envelopes, and `core/router.py` covers the 422 logic and the `get_flat_params` upgrade checklist.
- **`docs/adr/`:** architecture decisions: what was chosen, the alternatives, and why. They point to the code for details instead of repeating them. Add a new numbered ADR to change a decision; don't rewrite an accepted one.
- **This file:** only notes for Claude that don't belong in the README.

When the structure, commands or conventions change, update the README in the same change.

## Notes for Claude

- Early stage. There are no tests yet, so add pytest to the dev dependencies before you write any. The first test to write is the `get_flat_params` upgrade check in `core/router.py`.
- `httpx2` is a dev dependency because Starlette's `TestClient` imports it.
