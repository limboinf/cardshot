# Adaptive Card Ratios Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ratio presets and custom dimensions reflow card content consistently in WebUI previews and generated screenshots without changing card source files.

**Architecture:** `shooter.py` owns a pure HTML transformation that appends a high-priority runtime canvas override and optional base URL. The server uses it for a dimension-aware preview endpoint, while screenshot generation renders a temporary transformed copy; the WebUI keeps one width/height state and reloads that preview whenever the card or dimensions change.

**Tech Stack:** Python 3 standard library, `unittest`, vanilla HTML/CSS/JavaScript, headless Chrome.

## Global Constraints

- Do not modify HTML source files under `cards/` when switching dimensions or taking screenshots.
- Preview and screenshot must use the same adaptive HTML transformation.
- Invalid custom dimensions must leave the current canvas unchanged and show an error.
- Do not add third-party dependencies.

---

### Task 1: Shared adaptive HTML rendering

**Files:**
- Create: `tests/test_adaptive_render.py`
- Modify: `shooter.py`

**Interfaces:**
- Consumes: source HTML text, positive integer width and height, optional base URL.
- Produces: `render_adaptive_html(source: str, width: int, height: int, base_href: str | None = None) -> str`; `shoot()` uses the transformed result through a temporary file.

- [ ] **Step 1: Write failing unit tests**

Add standard-library `unittest` cases proving that the transform injects target dimensions before `</head>`, includes an escaped optional `<base>` URL, rejects non-positive dimensions, and leaves the input string unchanged.

- [ ] **Step 2: Verify the tests fail**

Run: `python3 -m unittest tests/test_adaptive_render.py -v`

Expected: import failure because `render_adaptive_html` does not exist.

- [ ] **Step 3: Implement the pure transform and screenshot integration**

Add a runtime style that sets `html` and `body` to the requested pixel dimensions with `!important`, zeroes margins, and hides overflow. Insert it before a case-insensitive closing head tag, or prepend it when no head exists. Update `shoot()` to render this transformed HTML from a temporary directory, adding the source directory URI as `<base href>` so relative resources still resolve, and always clean up the temporary file.

- [ ] **Step 4: Run unit and syntax checks**

Run: `python3 -m unittest tests/test_adaptive_render.py -v && python3 -m py_compile shooter.py server.py`

Expected: all tests pass and compilation exits 0.

- [ ] **Step 5: Commit the shared renderer**

```bash
git add shooter.py tests/test_adaptive_render.py
git commit -m "feat: render cards at adaptive canvas sizes"
```

### Task 2: Dimension-aware WebUI preview and controls

**Files:**
- Modify: `server.py`
- Modify: `static/index.html`

**Interfaces:**
- Consumes: `render_adaptive_html()` from Task 1 and query parameters `f`, `w`, `h`.
- Produces: `GET /api/preview?f=<name>&w=<width>&h=<height>` and a WebUI `refreshPreview()` path used by selection, resize, and editor save.

- [ ] **Step 1: Add the preview endpoint**

Import the shared renderer in `server.py`. Validate width and height as positive integers, read the safe card, transform it with `/cards/` as its base URL, and return UTF-8 HTML. Return HTTP 400 JSON for invalid names or dimensions.

- [ ] **Step 2: Unify frontend dimension state**

In `static/index.html`, add helpers to synchronize the active ratio chip, build the adaptive preview URL, refresh the current preview, and fit the frame to the available stage. Make `setSize()` reject invalid values, update width/height inputs and state, reload the preview, and fit automatically.

- [ ] **Step 3: Route all preview reloads through the helper**

Update ratio clicks, custom Apply, card selection, and editor saves to call the shared size/preview functions. Preserve the current target dimensions when switching or editing cards and activate a preset whenever custom dimensions exactly match it.

- [ ] **Step 4: Verify service and browser behavior**

Run the server, request a transformed preview with `curl`, and generate demo-card screenshots at 1080×1080 and 1920×1080. Confirm both PNG dimensions, confirm injected dimensions are present in preview HTML, and compare the source card checksum before and after.

- [ ] **Step 5: Run final checks and commit**

Run: `python3 -m unittest discover -s tests -v && python3 -m py_compile shooter.py server.py && git diff --check`

Expected: all tests pass, compilation exits 0, and no whitespace errors are reported.

```bash
git add server.py static/index.html
git commit -m "feat: sync ratio controls with adaptive previews"
```
