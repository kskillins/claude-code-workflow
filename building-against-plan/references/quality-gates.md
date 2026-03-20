# Quality Gate Automation

## Contents
- Gate detection and configuration
- Per-stack gate commands
- Gate execution order
- Failure handling
- Gate report format

## Gate detection and configuration

At the start of each build, detect the project's tech stack and configure quality gates accordingly. Use the project's existing configuration when available -- do not override established settings.

### Detection order

1. Check for existing config files:
   - `.eslintrc*`, `eslint.config.*` --> ESLint configured
   - `tsconfig.json` --> TypeScript configured
   - `.prettierrc*`, `prettier.config.*` --> Prettier configured
   - `pyproject.toml` with `[tool.ruff]` or `[tool.pylint]` --> Python linter configured
   - `mypy.ini`, `pyproject.toml` with `[tool.mypy]` --> mypy configured
   - `.flake8`, `setup.cfg` with `[flake8]` --> flake8 configured
   - `rustfmt.toml`, `.rustfmt.toml` --> Rust formatter configured
   - `clippy.toml` --> Clippy configured
2. Check `package.json` scripts for `test`, `lint`, `typecheck`, `format` commands
3. Check `pyproject.toml` or `Makefile` for equivalent commands
4. If no config exists, set up minimal config appropriate to the stack

### Minimal setup when no config exists

**Node/npm projects:**
```bash
# If no test runner found
npm install --save-dev jest    # or vitest if using Vite
# If no linter found
npm install --save-dev eslint
npx eslint --init
```

**Python projects:**
```bash
# If no test runner found
pip install pytest pytest-cov
# If no linter found
pip install ruff
```

**Rust projects:**
```bash
# Built-in: cargo test, cargo clippy, cargo fmt
# No additional setup needed
```

**Go projects:**
```bash
# Built-in: go test, go vet
# Optional: install golangci-lint if not present
```

## Per-stack gate commands

### Node/TypeScript

| Gate | Command | Pass condition |
|------|---------|---------------|
| Tests | `npm test` or `npx jest --passWithNoTests` | Exit code 0, all tests pass |
| Lint | `npx eslint .` or `npm run lint` | Exit code 0, no errors (warnings acceptable) |
| Type check | `npx tsc --noEmit` | Exit code 0, no type errors |
| Format check | `npx prettier --check .` | Exit code 0 (files already formatted) |
| Build | `npm run build` (if exists) | Exit code 0 |

### Python

| Gate | Command | Pass condition |
|------|---------|---------------|
| Tests | `pytest` or `python -m pytest` | Exit code 0, all tests pass |
| Coverage | `pytest --cov` | Exit code 0, report generated |
| Lint | `ruff check .` or `pylint **/*.py` or `flake8` | Exit code 0, no errors |
| Type check | `mypy .` (if configured) | Exit code 0, no errors |
| Format check | `ruff format --check .` or `black --check .` | Exit code 0 |

### Rust

| Gate | Command | Pass condition |
|------|---------|---------------|
| Tests | `cargo test` | Exit code 0 |
| Lint | `cargo clippy -- -D warnings` | Exit code 0, no warnings |
| Format check | `cargo fmt -- --check` | Exit code 0 |
| Build | `cargo build` | Exit code 0 |

### Go

| Gate | Command | Pass condition |
|------|---------|---------------|
| Tests | `go test ./...` | Exit code 0 |
| Vet | `go vet ./...` | Exit code 0 |
| Format check | `gofmt -l .` | No output (all files formatted) |
| Build | `go build ./...` | Exit code 0 |

## Gate execution order

Run gates in this order after each phase. Stop at the first failure and fix before continuing.

1. **Format** -- fix formatting issues first (often auto-fixable)
2. **Lint** -- fix lint errors (may reveal bugs)
3. **Type check** -- fix type errors (prevents runtime failures)
4. **Tests** -- run full test suite (the ultimate arbiter)
5. **Build** -- verify the project compiles/bundles (if applicable)

### Auto-fix where possible

Some gates have auto-fix capabilities. Use them before manual fixes:

```bash
# Node formatting
npx prettier --write .

# Node lint auto-fix
npx eslint --fix .

# Python formatting
ruff format .    # or: black .

# Python lint auto-fix
ruff check --fix .

# Rust formatting
cargo fmt

# Go formatting
gofmt -w .
```

After auto-fixing, re-run the gate to confirm resolution. Then run the full test suite to confirm auto-fixes did not change behavior.

## Failure handling

### Test failures

1. Read the full error output
2. Identify which test(s) failed and why
3. Trace the failure to the production code
4. Fix the production code
5. Re-run the full test suite
6. **NEVER edit the test to resolve a test failure**

### Lint failures

1. Read the lint error messages
2. Fix each issue in the production code
3. If a lint rule is inappropriate for this codebase, do NOT disable it without user approval
4. Re-run the linter

### Type check failures

1. Read the type error messages
2. Fix type annotations or production code logic
3. Do not use `any` types, `# type: ignore`, or `@ts-ignore` to suppress errors unless the type system genuinely cannot express the correct type
4. Re-run the type checker

### Format failures

1. Run the auto-formatter
2. If auto-formatting changes test files, verify the tests still behave identically
3. Re-run the format check

### Build failures

1. Read the build error messages
2. Fix the production code
3. Re-run the build
4. Then re-run the full test suite (build fixes may affect behavior)

## Gate report format

After all gates pass for a phase, produce a brief report:

```
Phase [N] Quality Gates:
- Format:     PASS
- Lint:       PASS (0 errors, 2 warnings)
- Type check: PASS
- Tests:      PASS (24 passed, 0 failed)
- Build:      PASS
```

If a gate required fixes, note what was fixed:

```
Phase [N] Quality Gates:
- Format:     PASS (auto-fixed 3 files)
- Lint:       PASS (fixed 1 unused import in src/utils.ts)
- Type check: PASS
- Tests:      PASS (28 passed, 0 failed -- fixed null handling in parseConfig)
- Build:      PASS
```
