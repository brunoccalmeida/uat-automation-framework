## 🧩 Edge Cases & Known Bugs

Some users in Sauce Demo (notably `problem_user`) are intentionally designed to exhibit bugs or non-standard behaviors, such as sorting failures or visual glitches. To ensure clarity and maintainability:

- **Normal user scenarios** are kept in their respective feature files (e.g., `product_sorting.feature`).
- **Edge cases and known bugs** (like `problem_user` sorting bug) are isolated in dedicated feature files (e.g., `product_sorting_problem_user.feature`), tagged with `@edgecase`.

### Why this separation?
- Keeps business requirements and regression tests clean and focused.
- Makes it easy to run only edge case scenarios:
  `poetry run behave --tags=edgecase`
- Facilitates maintenance when bugs are fixed or new edge cases are discovered.
- Improves reporting and communication with stakeholders.


### Example: Running edge case scenarios only

```bash
# Run only edge case scenarios (problem_user, etc)
poetry run behave features/product_sorting_problem_user.feature
# Or, using tags (recommended):
poetry run behave --tags=edgecase
```

See also: [features/product_sorting_problem_user.feature](features/product_sorting_problem_user.feature)

---

## ⚡ Parallel Test Execution & Coverage

This framework is designed for **safe, fast parallel execution** at all test layers (unit, integration, E2E):

- **Pytest**: Unit/integration tests run in parallel via `pytest-xdist` (`-n auto`)
- **Behave**: E2E scenarios are independent and can be run in parallel (see [docs/PARALLEL_TESTING.md](docs/PARALLEL_TESTING.md))
- **CI/CD**: All jobs use parallel execution for maximum speed

### Example: Run all tests in parallel with coverage

```bash
# Run all tests (unit, integration, E2E) in parallel with coverage
poetry run pytest --cov=core --cov=pages --cov=features --cov=tests --cov-report=term-missing --numprocesses=auto
poetry run behave
```

See [docs/PARALLEL_TESTING.md](docs/PARALLEL_TESTING.md) for details and troubleshooting parallel execution.

### Coverage Example (Dec 2025)

- **Total statements:** 258
- **Covered:** 256 (99.2%)
- **Pages module:** 100%
- **Core module:** 95%
- **All critical paths covered**

---

> If the application behavior changes (e.g., bug is fixed), update or remove the edge case scenario accordingly.
# UAT Automation Framework

[![Tests](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/brunoccalmeida/uat-automation-framework/branch/master/graph/badge.svg)](https://codecov.io/gh/brunoccalmeida/uat-automation-framework)
[![Python Version](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[English]** | **[Português (Brasil)](README.pt-BR.md)** | **[Español](README.es.md)**

📊 **[View Latest Test Report](https://brunoccalmeida.github.io/uat-automation-framework/)**

Comprehensive UAT automation framework using Python, Behave (BDD), and Selenium for testing the **Sauce Demo** e-commerce application.

## 📑 Table of Contents

- [Purpose](#-purpose)
- [Architecture](#️-architecture)
- [Getting Started](#-getting-started)
- [Testing Strategy](#-testing-strategy)
- [Technology Stack](#️-technology-stack)
- [CI/CD](#-cicd)
- [Project History](#-project-history)
- [Contributing](#-contributing)
- [License](#-license)

> **Note**: Originally developed for Parabank (banking demo), migrated to Sauce Demo due to instability issues with Parabank public instance. Framework architecture remains fully intact and demonstrates professional testing practices.

## 🎯 Purpose

This framework demonstrates professional UAT automation practices for web applications, featuring:
- **Target Application**: [Sauce Demo](https://www.saucedemo.com) - stable e-commerce demo by Sauce Labs
- Behavior-Driven Development (BDD) with Behave
- Page Object Model design pattern
- Comprehensive reporting with Allure
- Pre-configured test users (no credential management needed)
Test Users

Sauce Demo provides pre-configured test users (password: `secret_sauce` for all):

- `standard_user` - Normal user, no issues
- `locked_out_user` - User has been locked out
- `problem_user` - User experiences visual glitches
- `performance_glitch_user` - User has performance issues
- `error_user` - User encounters errors
- `visual_user` - User has visual testing variations

**Security**: No credential storage needed - users are provided by the demo application.

## 🏗️ Architecture

```
uat-automation-framework/
├── core/              # Framework core (config, drivers, utilities)
├── pages/             # Page Object Models
├── features/          # BDD feature files and step definitions
├── tests/             # Unit tests for framework components
└── reports/           # Test execution reports (gitignored)
```

### Design Paradigm: Pragmatic Hybrid Approach

This framework uses a **hybrid OOP/Functional programming approach**, choosing the right paradigm for each component:

**Object-Oriented Programming (60-70%)**
- **Page Objects**: Encapsulate page state and interactions (natural fit for UI automation)
- **Driver Manager**: Manages WebDriver lifecycle and state
- **Base Classes**: Shared functionality through inheritance where appropriate

**Functional Programming (30-40%)**
- **Utilities & Helpers**: Pure functions for data transformation and generation
- **Configuration Loading**: Stateless operations
- **Step Definitions**: Behave steps are naturally functional

**Rationale:**
- **Pragmatism over purity**: Use OOP where Selenium/Page Object patterns naturally fit
- **Testability**: Pure functions for business logic make unit testing straightforward
- **Industry standards**: Page Object Model is expected in professional test automation
- **Maintainability**: Familiar patterns reduce cognitive load for collaborators
- **Zen of Python**: "Practicality beats purity" - choose what works best for each case

## 🚀 Getting Started

### Prerequisites

- Python 3.14+
- Poetry (dependency management)
- Chrome or Firefox browser (drivers managed automatically by Selenium Manager)

### Installation

```bash
# Install dependencies
poetry install

# Install pre-commit hooks (one-time setup)
poetry run pre-commit install
```


**Pre-commit Hooks & Lint Configuration:**
All linting and formatting configuration is centralized in the `.pre-commit-config.yaml` file. There is **no** `.flake8` file: all Flake8, Black, and Pylint settings are managed via pre-commit hooks only.

- ✅ **Black**: Code formatting (`--line-length=88`)
- ✅ **Flake8**: Linting and style guide enforcement (`--max-line-length=88`, `--extend-ignore=E203,W503,E501`)
- ✅ **Pylint**: Code analysis for errors and smells (configured via `pyproject.toml`)
- ✅ **Security**: Detect private keys, merge conflicts
- ✅ **Quality**: Trailing whitespace, YAML validation

> **Note:** Do **not** create a `.flake8` file. All configuration is managed in `.pre-commit-config.yaml` for consistency and maintainability.

Hooks run automatically on `git commit`. To run all hooks manually: `pre-commit run --all-files`

### Running Tests

**BDD/E2E Tests (Behave):**
```bash
# Run all E2E tests (headless by default)
poetry run behave

# Run specific feature
poetry run behave features/smoke.feature
poetry run behave features/login.feature

# Run with visible browser (useful for debugging)
poetry run behave -Dheadless=false

# Run with Firefox (Chrome is default)
poetry run behave -Dbrowser=firefox

# Run Firefox in visible mode
poetry run behave -Dbrowser=firefox -Dheadless=false

# Run in headless mode via environment variable (useful for CI/CD)
$env:HEADLESS="true"; poetry run behave  # PowerShell
export HEADLESS=true && poetry run behave  # Bash

# Override browser via environment variable
$env:BROWSER="firefox"; poetry run behave  # PowerShell
export BROWSER=firefox && poetry run behave  # Bash

# Run with Allure reporting
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# Generate and view Allure report
allure serve reports/allure-results
```

**Running Tests by Tags:**

The framework uses a hierarchical tag system for precise test filtering:

```bash
# Run by test layer
poetry run behave --tags=@e2e              # All E2E tests (default)

# Run by test type
poetry run behave --tags=@smoke            # Critical smoke tests only
poetry run behave --tags=@functional       # Happy path scenarios
poetry run behave --tags=@negative         # Negative/edge cases
poetry run behave --tags=@user_journey     # Complete user flows

# Run by domain/feature
poetry run behave --tags=@login            # All login tests (functional + negative)
poetry run behave --tags=@cart             # All cart tests
poetry run behave --tags=@checkout         # All checkout tests
poetry run behave --tags=@sorting          # All sorting tests

# Run by priority/special
poetry run behave --tags=@critical         # Critical user journeys
poetry run behave --tags=@edgecase         # Known bugs/edge cases
poetry run behave --tags=@problem_user     # Problem user scenarios

# Combine tags (AND logic)
poetry run behave --tags=@cart --tags=@negative    # Cart negative tests only
poetry run behave --tags=@functional --tags=@cart  # Cart functional tests only

# Exclude tags (NOT logic)
poetry run behave --tags=~@edgecase        # All except edge cases
poetry run behave --tags=@e2e --tags=~@smoke  # E2E excluding smoke
```

**Tag Hierarchy:**
- **Layer**: `@e2e` (all features use this)
- **Type**: `@functional` | `@negative` | `@user_journey` | `@smoke` | `@edgecase`
- **Domain**: `@login` | `@cart` | `@checkout` | `@sorting`
- **Priority**: `@critical` | `@problem_user`

**Cross-Browser Testing:**

The framework supports Chrome and Firefox browsers. Use `-D` flags to override default configuration:

```bash
# Run smoke tests with Firefox (headless)
poetry run behave --tags=@smoke -Dbrowser=firefox -Dheadless=true

# Run smoke tests with Firefox (visible browser)
poetry run behave --tags=@smoke -Dbrowser=firefox -Dheadless=false

# Run all tests with Chrome (default)
poetry run behave -Dbrowser=chrome

# Override multiple config values
poetry run behave -Dbrowser=firefox -Dheadless=false -Dtimeout=15
```

**Supported browsers:**
- `chrome` (default) - Google Chrome with ChromeDriver
- `firefox` - Mozilla Firefox with GeckoDriver

**Note**: Selenium Manager automatically downloads and manages browser drivers - no manual installation required.

```

**Unit Tests (Pytest):**
```bash
# Run all unit tests (parallel execution)
poetry run pytest tests/ -n auto -v

# Run with coverage report (parallel)
poetry run pytest tests/ -n auto --cov=core --cov=pages --cov-report=term-missing

# Run specific test module
poetry run pytest tests/test_login_page.py -v

# Run sequentially (for debugging)
poetry run pytest tests/ -n 0 -v

# Run all tests (unit + integration + E2E)
poetry run pytest tests/ -n auto && poetry run pytest tests/integration/ -n auto && poetry run behave
```

**Integration Tests (Pytest + Real Browser):**
```bash
# Run all integration tests (parallel execution)
poetry run pytest tests/integration/ -n auto -v

# Run specific integration test
poetry run pytest tests/integration/test_login_page_integration.py -v

# Run in headless mode (parallel)
$env:HEADLESS="true"; poetry run pytest tests/integration/ -n auto -v  # PowerShell
export HEADLESS=true && poetry run pytest tests/integration/ -n auto -v  # Bash
```

**Parallel Execution:**

This framework supports parallel test execution using `pytest-xdist`:
- **Performance**: 88% faster (188 tests in ~37s vs ~305s)
- **Safety**: All tests are independent (function-scoped fixtures)
- **Automatic**: Use `-n auto` to detect CPU cores automatically
- **Debugging**: Use `-n 0` to disable parallelization

See [docs/PARALLEL_TESTING.md](docs/PARALLEL_TESTING.md) for detailed documentation.

**Headless Mode Configuration:**

The framework runs in **headless mode by default** (best practice: faster, less resources, consistent with CI/CD).

Configuration priority:
1. **CLI Parameter** (highest): `-Dheadless=true/false`
2. **Environment Variable**: `HEADLESS=true/false`
3. **Config File** (lowest): `config.yaml` (default: `true`)

Use `-Dheadless=false` for debugging with visible browser.

See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

## � CI/CD

The project uses **GitHub Actions** for continuous integration:

- ✅ **Automated testing** on every push and pull request
- ✅ **Python 3.14** latest stable version
- ✅ **Headless browser** execution in CI environment
- ✅ **Code quality** checks (Black, Flake8, Pylint)
- ✅ **Test artifacts** uploaded for review
- ✅ **Allure reports** published to GitHub Pages with history

**View Test Reports:** [https://brunoccalmeida.github.io/uat-automation-framework/](https://brunoccalmeida.github.io/uat-automation-framework/)

The reports include:
- Test execution trends and history (last 20 runs)
- Detailed test results with screenshots on failure
- Duration metrics and performance tracking
- Categorization by features and scenarios

See [.github/workflows/tests.yml](.github/workflows/tests.yml) for pipeline configuration.

## 🛠️ Technology Stack

- **Python 3.14**: Core language
- **Selenium 4**: Browser automation
- **Behave**: BDD/E2E testing framework
- **Pytest**: Unit testing framework
- **Allure**: Test reporting with history and trends
- **Poetry**: Dependency management
- **GitHub Actions**: CI/CD pipeline
- **GitHub Pages**: Live test report hosting

## 🧪 Testing Strategy

This framework implements the complete **Testing Pyramid** architecture with three distinct layers:

```
        E2E Tests (BDD)           ← Slow, Full User Flows
      /-------------------\
     / Integration Tests   \      ← Medium, Page+Browser
    /-----------------------\
   /      Unit Tests         \    ← Fast, Component Logic
  /---------------------------\
```

**Layer Distribution:**
- **Unit Tests**: 132 tests (framework components, 98% coverage)
- **Integration Tests**: 56 tests (Page Objects + real browser, 100% coverage)
- **E2E Tests**: 120 steps, 20 scenarios (complete user journeys)
- **Total**: 308 tests across all layers

**When to Use Each Layer:**
| Test Type | Purpose | Speed | Browser | Example |
|-----------|---------|-------|---------|---------|
| **Unit** | Component logic | Fast | Mocked | "Does `login()` call correct methods?" |
| **Integration** | Page + real DOM | Medium | Real | "Do login fields exist and work?" |
| **E2E** | Full user flows | Slow | Real | "Can user complete login→shop→checkout?" |

### BDD/E2E Tests (Behave)

| Feature | Scenarios | Steps | Status |
|---------|-----------|-------|--------|
| **Smoke Tests** | 4/4 ✅ | 14/14 ✅ | Complete |
| **User Login** | 4/4 ✅ | 18/18 ✅ | Complete |
| **Shopping Cart** | 6/6 ✅ | 35/35 ✅ | Complete |
| **Checkout** | 6/6 ✅ | 52/52 ✅ | Complete |
| **TOTAL** | **20** | **120** | **100%** |

### Unit Tests (Pytest)

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| **BasePage** | 19 | 100% | ✅ Complete |
| **LoginPage** | 14 | 100% | ✅ Complete |
| **CartPage** | 13 | 100% | ✅ Complete |
| **InventoryPage** | 12 | 100% | ✅ Complete |
| **CheckoutStepOnePage** | 13 | 100% | ✅ Complete |
| **CheckoutStepTwoPage** | 15 | 100% | ✅ Complete |
| **CheckoutCompletePage** | 12 | 100% | ✅ Complete |
| **ConfigResolver** | 30 | 100% | ✅ Complete |
| **Smoke Tests** | 4 | N/A | ✅ Complete |
| **TOTAL** | **132** | **98%** | **Complete** |

**Code Coverage:**
- **Pages Module**: 100% (194/194 statements)
- **Core Module**: 95% (62/65 statements)
- **Overall Framework**: 98%+

### Integration Tests (Pytest + Real Browser)

Integration tests validate Page Objects with real browser interactions, filling the gap between unit tests (mocked) and E2E tests (full user flows).

| Module | Tests | Browser | Status |
|--------|-------|---------|--------|
| **LoginPage** | 9 | Chrome | ✅ Complete |
| **InventoryPage** | 9 | Chrome | ✅ Complete |
| **CartPage** | 10 | Chrome | ✅ Complete |
| **CheckoutStepOnePage** | 15 | Chrome | ✅ Complete |
| **CheckoutStepTwoPage** | 13 | Chrome | ✅ Complete |
| **TOTAL** | **56** | **Real** | **Complete** |

**Key Differences from Unit Tests:**
- ✅ Real Selenium WebDriver (not mocked)
- ✅ Actual DOM elements validation
- ✅ True locator verification
- ✅ Browser interaction testing
- ✅ Faster than E2E (no full flows)
- ✅ Complete Page Object coverage (100%)

### Test Scenarios

**Smoke Tests**
- ✅ Homepage loads and displays correctly
- ✅ Login form elements present and functional
- ✅ Valid user authentication
- ✅ Invalid credentials rejection

**User Login**
- ✅ Valid user authentication (standard_user)
- ✅ Invalid credentials rejection
- ✅ Locked user detection (locked_out_user)
- ✅ Successful logout flow

**Shopping Cart**
- ✅ Add single product to cart
- ✅ Add multiple products to cart
- ✅ View cart contents
- ✅ Remove product from cart
- ✅ Continue shopping from cart
- ✅ Cart persistence across navigation

**Checkout**
- ✅ Complete checkout with valid information
- ✅ Validation for required fields
- ✅ Order summary with pricing details
- ✅ Cancel checkout and return to cart
- ✅ Order confirmation message
- ✅ Post-purchase cart clearing
- 🚧� Test Reports

Reports are generated in the `reports/` directory and are automatically excluded from version control.

```bash
# Generate Allure report
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```

## 🎯 Roadmap

Future enhancements following industry best practices:

- [x] **Parallel Execution** - pytest-xdist implemented (88% faster, ~37s for 188 tests)
- [ ] **Cross-browser Testing** - Firefox and Edge support
- [ ] **Docker Containerization** - Consistent execution environments
- [ ] **Visual Regression Testing** - Percy/Applitools integration
- [ ] **API Tests** - Faster feedback with API-level testing

## 🤝 Contributing

This is a portfolio project demonstrating professional UAT automation practices following:
- **Testing Pyramid**: Unit → Integration → E2E tests (proper layer separation)
- **Outside-in TDD/BDD**: Red-Green-Refactor cycle for all production code
- **Page Object Model**: Clean separation of test logic from page interactions
- **Explicit Waits**: No `time.sleep()` - proper Selenium wait strategies
- **Atomic Commits**: Conventional Commits format for clear history
- **Self-documenting Code**: Comprehensive docstrings and type hints
- **CI/CD Integration**: Automated testing with every push
- **Live Reporting**: GitHub Pages hosting with Allure reports and history

## 📚 Project History

**Migration Note**: This framework was originally developed for Parabank (banking demo) and successfully migrated to Sauce Demo in <1 hour, proving the robustness of its architecture. All core design patterns (BDD, POM, Selenium best practices) remained unchanged, demonstrating true framework portability.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Author**: Bruno Almeida
**Purpose**: Professional portfolio and UAT automation demonstration
