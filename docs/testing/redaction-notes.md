# Redaction notes for the historical test records

**Editorial note — not part of the historical record.**

- **Date:** 2026-10-17
- **Scope:** `docs/testing/sprint-1-*`, `sprint-2-*` and `sprint-3-*` (`.md` / `.txt`)
- **Reason:** those records were written on team members' own machines and quoted
  full Windows paths, which published local user names and directory layouts in a
  public repository.

## What was changed

Only the local path strings were replaced. **No test result, test date, defect,
limitation, scenario status, file name, screenshot reference, Story identifier or
count was altered**, and no document was re-worded beyond the four headings noted
below.

Four headings that said "absolute path" were corrected to say "local path; user
profile redacted", because after redaction they no longer contain an absolute
path. Nothing else in the prose was changed.

## Placeholders used

| Placeholder | Meaning |
|-------------|---------|
| `<PROJECT_ROOT>` | The repository checkout on the machine that ran the test — the directory containing `README.md`, `app/` and `tests/`. |
| `<LOCAL_EVIDENCE_DIR>` | A folder **outside** the repository where screenshots, logs or manifests were kept on the tester's own machine. The sub-folder name is preserved, e.g. `<LOCAL_EVIDENCE_DIR>\Sprint2_Browser_Evidence\`. |
| `<TEMP_DIR>` | The operating-system temporary directory used for a throwaway SQLite database. |
| `<USER_PROFILE>` | The tester's Windows user profile directory. Used only where the record documents a desktop-path verification (`<USER_PROFILE>\Desktop`). |

## What was deliberately preserved

- The drive-relative structure and trailing separators, so the paths still read as
  Windows paths and still show *where* the evidence sat relative to the
  repository.
- `<LOCAL_EVIDENCE_DIR>` sub-folder names (`Sprint1_Browser_Test`,
  `Sprint2_Browser_Evidence`, `Sprint3_Evidence`, `Sprint3_Test_Evidence`), which
  are what the original records used to identify each evidence set.
- The statement that some evidence lived outside the repository and was not part
  of the deliverable — that distinction still matters for review.

## Note on reproducibility

These redacted paths cannot be used to locate the original evidence on this
machine. Where an evidence file was copied into the repository it is still
referenced by its in-repository relative path, and those references are
unchanged.
