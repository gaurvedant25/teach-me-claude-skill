# Updating an existing chapter page

Read when the user asks to change, extend or upgrade a page that already exists (theirs or one you
built earlier). Students keep progress in these pages; an update must not lose content or progress.

## 1. Get the real source, then back up

* Find the content folder used to build it. If it is not available, read the published artifact
  (Artifact tool `read`); the page embeds its data in `<script id="teachme-data">`. Extract that JSON
  as the starting content. If neither is possible, tell the user what you need before replacing anything.
* Before any substantial edit, copy the content folder, the built HTML and the skill files into
  `versions/<label>-<date>/`. Say where the copy is.

## 2. Preserve, don't rewrite

* Keep every id: topics, lessons, questions (including `<case>.<n>` parts and `-or` alternatives),
  flashcard `id`s (`fc-001`...). Progress is keyed by them. New items get new ids; never reuse an old id
  for different content.
* Flashcards keep their order (v1 pages stored card progress by position).
* Add teaching fields to existing questions through `patches` files (`{"patches": {"<id>": {...}}}`) so
  the original wording, options, key and source stay untouched; the build refuses patches that change
  those. Edit a question's wording only to fix an error, and log it in `corrections`.
* Moving lesson text into the new structure is fine; dropping it is not. Superseded content files go to
  `content/_superseded/` (not built) rather than being deleted.
* Run `python scripts/preserve_check.py <old content> <new content> --report preserve-report.md`.
  "Removed" must be empty; every "changed" line must be a restructuring or a logged correction.

## 3. Progress migration

The template stores progress under `teachme2:<board|class|subject|chapter|session>` and migrates the
older `teachme:` key automatically (keeping a backup copy in the browser). Do not change `meta.board`,
`class`, `subject`, `chapter` or `session` on an update - that changes the storage key and orphans the
student's progress. If the template's state shape must change, add a migration in `loadState()` and keep
the old key's backup.

## 4. Publish to the same link

Publish the rebuilt `.html` to the existing artifact `url` (read it first). Keep the capabilities
declaration (`{db: {}, user: {}, downloads: true}`) so account sync and backup downloads keep working.
After publishing, check the private progress document once with ArtifactData (`list` on
`data/users/me`); remember the page only adopts an account copy that is newer *and* not smaller than
the local one.

## 5. Report

Tell the user separately what changed in the page, what was verified, what is still open, and where the
backup lives.
