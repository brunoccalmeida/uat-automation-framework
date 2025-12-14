# UAT Automation Framework

Comprehensive UAT automation framework using Python, Behave (BDD), and Selenium for testing the Parabank demo banking application.

## 🎯 Purpose

This framework demonstrates professional UAT automation practices for banking applications, featuring:
- Behavior-Driven Development (BDD) with Behave
- Page Object Model design pattern
- Comprehensive reporting with Allure
- Support for both remote and local (Docker) environments

## 🔐 Security Approach: Ephemeral Credentials

**Why we use dynamically generated credentials:**

This framework implements **ephemeral credential management** rather than storing secrets for the following reasons:

1. **Security by Design**: No sensitive credentials are stored in configuration files, environment variables, or code
2. **Test Isolation**: Each test run can create fresh users, ensuring complete independence between test executions
3. **Zero Configuration**: No manual credential management required - tests work out of the box
4. **Production-Ready Pattern**: Demonstrates real-world security practices suitable for banking/regulated environments
5. **CI/CD Friendly**: No secrets to inject or manage in pipelines

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

## 📝 Development Guidelines

See [.copilot-instructions.md](.copilot-instructions.md) for detailed development practices.

Key principles:
- Zen of Python philosophy
- TDD for production code
- Page Object pattern for maintainability
- Ephemeral credentials for security
- Comprehensive documentation

## 🐳 Docker Support

(Coming soon: Instructions for running Parabank locally via Docker)

## 📊 Test Reports

Reports are generated in the `reports/` directory and are automatically excluded from version control.

## 🤝 Contributing

This is a portfolio project demonstrating professional UAT automation practices.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Author**: Bruno Almeida  
**Purpose**: Professional portfolio and UAT automation demonstration
