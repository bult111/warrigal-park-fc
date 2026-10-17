# Test Environment — Final Verification 2026-10-16

Everything recorded here was read from the machine that actually ran the
verification. Nothing on this page is inferred or copied from earlier documents.

## Machine and toolchain

| Item | Value |
|------|-------|
| Operating system | Microsoft Windows 11 Home (Chinese), version `10.0.26200` |
| Shell | PowerShell 7 (`pwsh`, `-Command`) |
| Python | 3.10.11 (`tags/v3.10.11:7d4cc5a`, MSC v.1929 64-bit AMD64) |
| Python executable | `…\warrigal-park-fc\warrigal-park-fc\.venv\Scripts\python.exe` |
| Git | `git version 2.56.0.windows.1` |
| Node.js | v24.9.0 (used only to drive the browser over CDP; not a project dependency) |
| Browser | Microsoft Edge `Edg/155.0.4283.45`, launched headless |
| Browser automation | Chrome DevTools Protocol on `127.0.0.1:9333`, via a dependency-free `cdp.mjs` client |

## Python packages in the project virtual environment

Declared in `requirements.txt`:

```text
# Runtime dependencies
Flask==3.0.3
python-dotenv==1.0.1

# Test dependencies
pytest==8.3.3
```

Full `pip freeze` of the virtual environment used:

```text
blinker==1.9.0          Flask==3.0.3            Jinja2==3.1.6
click==8.5.0            iniconfig==2.3.1        MarkupSafe==3.0.4
colorama==0.4.6         itsdangerous==2.2.0     packaging==26.3
et_xmlfile==2.0.0       lxml==6.1.3             pluggy==1.6.0
exceptiongroup==1.3.1   openpyxl==3.1.5         pypdf==6.21.0
pytest==8.3.3           python-docx==1.2.0      python-dotenv==1.0.1
tomli==2.5.0            typing_extensions==4.16.0  Werkzeug==3.1.9
```

**Environment-hygiene observation (not an application defect).** The virtual
environment contains packages that `requirements.txt` does not declare
(`lxml`, `openpyxl`, `pypdf`, `python-docx`, `et_xmlfile`, `exceptiongroup`,
`tomli`, `typing_extensions`, plus their transitive `blinker`/`click`/`colorama`/
`itsdangerous`/`MarkupSafe`/`packaging`/`pluggy`). A grep of `app/` and `tests/`
confirms the application and the test suite import **none** of them, so they do
not affect the result. This repeats an observation already recorded in the
Sprint 1 defect log; it is left unchanged because removing packages from a shared
environment is outside the scope of a verification pass.

No dependency installation was required or performed for this verification — the
existing `.venv` already satisfied `requirements.txt`.

## Path placeholders

Absolute local paths are deliberately not published in this repository. Three
placeholders are used throughout these documents:

| Placeholder | Meaning |
|-------------|---------|
| `<PROJECT_ROOT>` | The repository checkout — the directory that contains `README.md`, `app/`, `tests/` and `requirements.txt`. |
| `<AUDIT_WORKSPACE>` | The scratch workspace used for the browser run, located **outside** the repository. It holds the temporary SQLite database, the Edge profile and the acceptance driver scripts. |
| `<AUDIT_ARCHIVE>` | The local audit archive, located **outside** the repository, holding the internal audit artifacts that are deliberately excluded from this repository. |

## Database isolation

| Item | Path | Touched by this verification? |
|------|------|-------------------------------|
| Real project database | `<PROJECT_ROOT>\instance\warrigal_park_fc.db` | **No.** The file does not exist on this machine; it was never opened or created. |
| Other pre-existing file | `<PROJECT_ROOT>\instance\presentation_demo.db` (2026-10-15) | **No.** Never opened. |
| Unit-test databases | pytest `tmp_path` per test | Yes — created and discarded by the test suite itself. |
| Browser acceptance database | `<AUDIT_WORKSPACE>\final-verify.db` | Yes — the only database the Flask instance under test used. |

The Flask server for the browser run was started with
`DATABASE=<AUDIT_WORKSPACE>\final-verify.db`, and `init_temp_db.py` printed that
same path together with `REAL DB EXISTS: False` before and after the run
(`database-state-final.txt`).

## Git state during the verification

| Item | Value |
|------|-------|
| Local branch checked out | `audit/final-verification-20261016` (created for this task) |
| Base commit of that branch | `3205042ade4beef2753dde4c86fbb5292dc418c8` |
| Tree of that base commit | `a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd` |
| Real remote `main` tip (GitHub API) | `fd7b68c15d92e0511b8609f3c9ce84c9943724ee` |
| Tree of remote `main` tip | `a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd` |
| `main` branch left untouched | Yes — still `1ec3a25` |
| Push / merge / PR created | None |

The two tree hashes match exactly, so the code and documentation verified here are
byte-identical to remote `main`, even though `git fetch` could not run.

## Network

`git` could not reach `github.com:443` from this machine, so
`git fetch`/`git ls-remote` failed. The GitHub REST API was reachable through the
agent's HTTP fetch tool, and that is the source of every remote fact recorded in
these documents. This distinction matters: remote **Git state** was read from the
API, not from a Git fetch.

## Commands actually executed

```powershell
# unit tests (project virtual environment)
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --collect-only -q

# whitespace / conflict-marker check
git diff --check

# bytecode compilation check
.\.venv\Scripts\python.exe -m compileall -q app tests

# browser acceptance (driver scripts run from <AUDIT_WORKSPACE>)
$env:DATABASE = "<AUDIT_WORKSPACE>\final-verify.db"
$env:PORT = "5066"
.\.venv\Scripts\python.exe run.py
node run1.mjs                       # 35 scenarios
python inject_legacy.py             # legacy-data injection; script in <AUDIT_ARCHIVE>
node run2.mjs                       # 2 scenarios
python db_dump.py
```
