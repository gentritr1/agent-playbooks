---
name: ctx-skill
description: Use when testing context detection in check-applicability; fixture only.
---

# Context fixture

### CTX-001 · Web rule
- **Rule:** fixture rule for ctx:web.
- **Kind:** fact — synthetic.
- **Evidence:** fixture → [ev](evidence/ctx.md)
- **Confidence:** VERIFIED
- **Gate:** none
- **Valid while:** `ctx:web` · last_validated: 2026-10-07
- **Source:** CTX-001

### CTX-002 · Wasm rule
- **Rule:** fixture rule for ctx:wasm.
- **Kind:** fact — synthetic.
- **Evidence:** fixture → [ev](evidence/ctx.md)
- **Confidence:** VERIFIED
- **Gate:** none
- **Valid while:** `ctx:wasm` · last_validated: 2026-10-07
- **Source:** CTX-002

### CTX-003 · Versioned web-test rule
- **Rule:** fixture rule for a package declared in web/.
- **Kind:** fact — synthetic.
- **Evidence:** fixture → [ev](evidence/ctx.md)
- **Confidence:** VERIFIED
- **Gate:** none
- **Valid while:** `playwright@1.63` `ctx:web` · last_validated: 2026-10-07
- **Source:** CTX-003

## Not covered / defer to
- Anything else.
