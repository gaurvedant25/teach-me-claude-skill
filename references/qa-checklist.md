# Functional checks before calling a page finished

Build cleanly with `--strict`, then open the `.preview.html` through a local server (browser panes refuse
`file://`; in the Claude desktop app use a `.claude/launch.json` entry and `preview_start`). Run what your
tools support and report which checks ran and which did not - never imply an untested check passed.

## Automatic (script in the page)

`assets/qa.js` (load it into the preview: `<script src="qa.js">`, then `await __qa()`) visits every
section and reports document overflow, elements wider than the screen outside a scroll container,
controls under 40 px tall, and the lesson font size and column width. Run it after
`resize_window` to **320, 390, 768 and 1280 px** (reload after each resize). Then also check:
* No `<math>` is wider than the screen unless inside a scrolling row - loop over every lesson at 320 px
  and over Practice lists with all solutions opened.
* Characters per line in lessons: about 65-75 (measure average character width × column width).

## By interaction

| Check | Pass when |
|---|---|
| Teaching | A worked example shows where every number comes from; search "why divide by 40"-style phrases finds the step |
| Feedback | A wrong answer with a planned mistake shows its specific message; a right one with no unit gets the unit reminder; step check works |
| Honest progress | Hint → "solved with help (you opened a hint)"; viewed solution → "with help"; first-try clean → "independently"; written answers say "self-assessed" |
| Search and return | Opening a result scrolls to and highlights the block; "Back to where you were" restores view, tab and scroll |
| Continue studying | After scrolling a lesson and reloading, the Learn page names the exact step and reopens it |
| Persistence | Read marks, attempts, bookmarks, drafts and position survive reload |
| Backup | Copy/export → reset → restore brings everything back; a safety copy is kept before reset/restore |
| Migration (updates) | A state saved under the old key loads, is marked as carried over, and nothing counts as independent that was not |
| Test | No hint, solution, status or difficulty chips before submit (run several random papers); everything revealed after submit; result separates auto-checked and self-assessed marks |
| Keyboard | `/` opens search with focus in the box; Esc closes; Tab stays inside open sheets; focus ring visible |
| Console | No errors (`read_console_messages onlyErrors`) |

Notes from experience: the browser pane may not run IntersectionObserver or scroll events while hidden -
dispatch a `scroll` event manually to test position tracking. Zoom can't be emulated directly; 320 px at
1280 is the WCAG equivalent of 400% zoom, so a clean 320 px run covers reflow.
