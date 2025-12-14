# UAT Automation Framework

Comprehensive UAT automation framework using Python, Behave (BDD), and Selenium for testing the **Sauce Demo** e-commerce application.

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
- Chrome/Firefox browser

### Installation

```bash
# Install dependencies
poetry install
```

### Running Tests

```bash
# Run all tests (uses config.yaml default)
poetry run behave

# Run specific feature
poetry run behave features/smoke.feature
poetry run behave features/login.feature

# Run in headless mode (CLI override)
poetry run behave -Dheadless=true

# Run with visible browser (useful for debugging)
poetry run behave -Dheadless=false

# Run in headless mode via environment variable (useful for CI/CD)
$env:HEADLESS="true"; poetry run behave  # PowerShell
export HEADLESS=true && poetry run behave  # Bash

# Run with Allure reporting
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# Generate and view Allure report
allure serve reports/allure-results
```

**Headless Mode Configuration:**

The framework supports flexible headless mode configuration with the following priority:
1. **CLI Parameter** (highest): `-Dheadless=true/false`
2. **Environment Variable**: `HEADLESS=true/false`
3. **Config File** (lowest): `config.yaml` default value

See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

## 🛠️ Technology Stack

- **Python 3.14**: Core language
- **Selenium 4**: Browser automation
- **Behave**: BDD framework
- **Allure**: Test reporting
- **Poetry**: Implemented

| Feature | Scenarios | Steps | Status |
|---------|-----------|-------|--------|
| **Smoke Tests** | 4/4 ✅ | 14/14 ✅ | Complete |
| **User Login** | 4/4 ✅ | 18/18 ✅ | Complete |
| **Shopping Cart** | 6/6 ✅ | 35/35 ✅ | Complete |
| **Checkout** | 6/6 ✅ | 52/52 ✅ | Complete |
| **Product Catalog** | - | - | Planned |

### Test Coverage

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

## 🤝 Contributing

This is a portfolio project demonstrating professional UAT automation practices following:
- Outside-in TDD/BDD (Red-Green-Refactor)
- Page Object Model design pattern
- Explicit waits (no `time.sleep()`)
- Atomic commits with Conventional Commits
- Self-documenting code with docstrings

## 📚 Project History

**Migration Note**: This framework was originally developed for Parabank (banking demo) and successfully migrated to Sauce Demo in <1 hour, proving the robustness of its architecture. All core design patterns (BDD, POM, Selenium best practices) remained unchanged, demonstrating true framework portability.ogin: Successful login (with dynamic pre-registration) and failed login
- Driver setup: Maximize window, disable autofill prompts, reduce automation detection
- Instructions: Workspace-wide rules in .github/copilot-instructions.md

### Quick Run

```bash
# Run registration feature
poetry run behave features/register.feature

# Run login feature
poetry run behave features/login.feature
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Author**: Bruno Almeida  
**Purpose**: Professional portfolio and UAT automation demonstration
