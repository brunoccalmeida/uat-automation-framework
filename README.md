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

**Security**: No credential storage needed - users are provided by the demo application
Parabank's `/register` endpoint allows dynamic user creation, making this approach both secure and practical.

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
# Run all Behave scenarios
poetry run behave

# Run with Allure reporting
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# Generate and view Allure report
allure serve reports/allure-results
```

## 🛠️ Technology Stack

- **Python 3.14**: Core language
- **Selenium 4**: Browser automation
- **Behave**: BDD framework
- **Allure**: Test reporting
- **Poetry**: Dependency management
- **pytest**: Unit testing framework
- **PyYAML**: Configuration management

## ✅ Features Status
Implemented

- ✅ **Smoke Tests**: Basic application availability checks
- ✅ **User Login**: Login with valid/invalid credentials, locked users, logout
- 🚧 **Shopping Cart**: Add/remove items, checkout flow (planned)
- 🚧 **Product Catalog**: Sorting, filtering, details (planned)
## 📝 Development Guidelines

See [.github/copilot-instructions.md](.github/copilot-instructions.md) for project rules applied automatically in VS Code Copilot Chat.

Key principles:
- Zen of Python
- Outside-in TDD/BDD (Red-Green-Refactor)
- Page Object Model
- Ephemeral test users (no stored credentials)
- Explicit waits with Selenium (no `time.sleep()`)

## 🐳 Docker Support

(Coming soon: Instructions for running Parabank locally via Docker)

## 📊 Test Reports

Reports are generated in the `reports/` directory and are automatically excluded from version control.

## 🤝 Contributing

This is a portfolio project demonstrating professional UAT automation practices.

## ✅ Current Feature Status

- Registration: Successful registration creates account and auto-login
- Login: Successful login (with dynamic pre-registration) and failed login
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
