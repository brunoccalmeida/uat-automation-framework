# UAT Automation Framework

[![Tests](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/brunoccalmeida/uat-automation-framework/branch/master/graph/badge.svg)](https://codecov.io/gh/brunoccalmeida/uat-automation-framework)
[![Python Version](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[English](README.md)** | **[Português (Brasil)]**

📊 **[Ver Relatório de Testes](https://brunoccalmeida.github.io/uat-automation-framework/)**

Framework completo de automação UAT usando Python, Behave (BDD) e Selenium para testar a aplicação e-commerce **Sauce Demo**.

## 📑 Índice

- [Objetivo](#-objetivo)
- [Arquitetura](#️-arquitetura)
- [Começando](#-começando)
- [Estratégia de Testes](#-estratégia-de-testes)
- [Stack Tecnológica](#️-stack-tecnológica)
- [CI/CD](#-cicd)
- [Histórico do Projeto](#-histórico-do-projeto)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

> **Nota**: Originalmente desenvolvido para Parabank (demo bancário), migrado para Sauce Demo devido a problemas de instabilidade da instância pública do Parabank. A arquitetura do framework permanece intacta e demonstra práticas profissionais de teste.

## 🎯 Objetivo

Este framework demonstra práticas profissionais de automação UAT para aplicações web, incluindo:
- **Aplicação Alvo**: [Sauce Demo](https://www.saucedemo.com) - demo e-commerce estável da Sauce Labs
- Behavior-Driven Development (BDD) com Behave
- Padrão de design Page Object Model
- Relatórios abrangentes com Allure
- Usuários de teste pré-configurados (sem necessidade de gerenciamento de credenciais)

### Usuários de Teste

O Sauce Demo fornece usuários de teste pré-configurados (senha: `secret_sauce` para todos):

- `standard_user` - Usuário normal, sem problemas
- `locked_out_user` - Usuário bloqueado
- `problem_user` - Usuário com falhas visuais
- `performance_glitch_user` - Usuário com problemas de performance
- `error_user` - Usuário que encontra erros
- `visual_user` - Usuário com variações de teste visual

**Segurança**: Não é necessário armazenar credenciais - os usuários são fornecidos pela aplicação demo.

## 🏗️ Arquitetura

```
uat-automation-framework/
├── core/              # Núcleo do framework (config, drivers, utilitários)
├── pages/             # Page Object Models
├── features/          # Arquivos de features BDD e definições de steps
├── tests/             # Testes unitários dos componentes do framework
└── reports/           # Relatórios de execução de testes (gitignored)
```

### Paradigma de Design: Abordagem Híbrida Pragmática

Este framework usa uma **abordagem híbrida OOP/Funcional**, escolhendo o paradigma certo para cada componente:

**Programação Orientada a Objetos (60-70%)**
- **Page Objects**: Encapsulam estado e interações da página (adequado naturalmente para automação de UI)
- **Driver Manager**: Gerencia ciclo de vida e estado do WebDriver
- **Classes Base**: Funcionalidade compartilhada através de herança quando apropriado

**Programação Funcional (30-40%)**
- **Utilitários & Helpers**: Funções puras para transformação e geração de dados
- **Carregamento de Configuração**: Operações sem estado
- **Definições de Steps**: Steps do Behave são naturalmente funcionais

**Justificativa:**
- **Pragmatismo sobre pureza**: Usa OOP onde os padrões Selenium/Page Object se encaixam naturalmente
- **Testabilidade**: Funções puras para lógica de negócio facilitam testes unitários
- **Padrões da indústria**: Page Object Model é esperado em automação de teste profissional
- **Manutenibilidade**: Padrões familiares reduzem carga cognitiva para colaboradores
- **Zen do Python**: "Praticidade supera pureza" - escolha o que funciona melhor para cada caso

## 🚀 Começando

### Pré-requisitos

- Python 3.14+
- Poetry (gerenciamento de dependências)
- Navegador Chrome

### Instalação

```bash
# Instalar dependências
poetry install

# Instalar hooks de pre-commit (configuração única)
poetry run pre-commit install
```

**Hooks de Pre-commit:**
O framework usa hooks de pre-commit para manter qualidade de código automaticamente:
- ✅ **Black**: Formatação de código (88 caracteres por linha)
- ✅ **Flake8**: Linting e aplicação de guia de estilo
- ✅ **Pylint**: Análise de código para erros e code smells
- ✅ **Segurança**: Detecção de chaves privadas, conflitos de merge
- ✅ **Qualidade**: Trailing whitespace, validação YAML

Os hooks executam automaticamente no `git commit`. Execução manual: `pre-commit run --all-files`

### Executando Testes

**Testes BDD/E2E (Behave):**
```bash
# Executar todos testes E2E (headless por padrão)
poetry run behave

# Executar feature específica
poetry run behave features/smoke.feature
poetry run behave features/login.feature

# Executar com navegador visível (útil para debugging)
poetry run behave -Dheadless=false

# Sobrescrever para headless se necessário
poetry run behave -Dheadless=true

# Executar headless via variável de ambiente (útil para CI/CD)
$env:HEADLESS="true"; poetry run behave  # PowerShell
export HEADLESS=true && poetry run behave  # Bash

# Executar com relatório Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# Gerar e visualizar relatório Allure
allure serve reports/allure-results
```

**Testes Unitários (Pytest):**
```bash
# Executar todos testes unitários
poetry run pytest tests/ -v

# Executar com relatório de cobertura
poetry run pytest tests/ --cov=core --cov=pages --cov-report=term-missing

# Executar módulo de teste específico
poetry run pytest tests/test_login_page.py -v

# Executar todos testes (unit + integration + E2E)
poetry run pytest tests/ && poetry run pytest tests/integration/ && poetry run behave
```

**Testes de Integração (Pytest + Navegador Real):**
```bash
# Executar todos testes de integração
poetry run pytest tests/integration/ -v

# Executar teste de integração específico
poetry run pytest tests/integration/test_login_page_integration.py -v

# Executar em modo headless
$env:HEADLESS="true"; poetry run pytest tests/integration/ -v  # PowerShell
export HEADLESS=true && poetry run pytest tests/integration/ -v  # Bash
```

**Configuração do Modo Headless:**

O framework executa em **modo headless por padrão** (melhor prática: mais rápido, menos recursos, consistente com CI/CD).

Prioridade de configuração:
1. **Parâmetro CLI** (maior): `-Dheadless=true/false`
2. **Variável de Ambiente**: `HEADLESS=true/false`
3. **Arquivo de Config** (menor): `config.yaml` (padrão: `true`)

Use `-Dheadless=false` para debugging com navegador visível.

Veja [CONFIGURATION.md](CONFIGURATION.md) para opções detalhadas de configuração.

## 🧪 Estratégia de Testes

Este framework implementa a arquitetura completa da **Pirâmide de Testes** com três camadas distintas:

```
        Testes E2E (BDD)          ← Lentos, Fluxos Completos de Usuário
      /-------------------\
     / Testes Integração   \      ← Médio, Página+Navegador
    /-----------------------\
   /   Testes Unitários     \    ← Rápidos, Lógica de Componentes
  /---------------------------\
```

**Distribuição por Camada:**
- **Testes Unitários**: 132 testes (componentes do framework, 98% de cobertura)
- **Testes de Integração**: 56 testes (Page Objects + navegador real, 100% de cobertura)
- **Testes E2E**: 120 steps, 20 cenários (jornadas completas de usuário)
- **Total**: 308 testes em todas as camadas

**Quando Usar Cada Camada:**
| Tipo de Teste | Propósito | Velocidade | Navegador | Exemplo |
|---------------|-----------|------------|-----------|---------|
| **Unitário** | Lógica de componente | Rápido | Mockado | "O método `login()` chama os métodos corretos?" |
| **Integração** | Página + DOM real | Médio | Real | "Os campos de login existem e funcionam?" |
| **E2E** | Fluxos completos de usuário | Lento | Real | "O usuário pode completar login→comprar→checkout?" |

### Testes BDD/E2E (Behave)

| Feature | Cenários | Steps | Status |
|---------|----------|-------|--------|
| **Testes de Smoke** | 4/4 ✅ | 14/14 ✅ | Completo |
| **Login de Usuário** | 4/4 ✅ | 18/18 ✅ | Completo |
| **Carrinho de Compras** | 6/6 ✅ | 35/35 ✅ | Completo |
| **Checkout** | 6/6 ✅ | 52/52 ✅ | Completo |
| **TOTAL** | **20** | **120** | **100%** |

### Testes Unitários (Pytest)

| Módulo | Testes | Cobertura | Status |
|--------|--------|-----------|--------|
| **BasePage** | 19 | 100% | ✅ Completo |
| **LoginPage** | 14 | 100% | ✅ Completo |
| **CartPage** | 13 | 100% | ✅ Completo |
| **InventoryPage** | 12 | 100% | ✅ Completo |
| **CheckoutStepOnePage** | 13 | 100% | ✅ Completo |
| **CheckoutStepTwoPage** | 15 | 100% | ✅ Completo |
| **CheckoutCompletePage** | 12 | 100% | ✅ Completo |
| **ConfigResolver** | 30 | 100% | ✅ Completo |
| **Testes de Smoke** | 4 | N/A | ✅ Completo |
| **TOTAL** | **132** | **98%** | **Completo** |

**Cobertura de Código:**
- **Módulo Pages**: 100% (194/194 statements)
- **Módulo Core**: 95% (62/65 statements)
- **Framework Geral**: 98%+

### Testes de Integração (Pytest + Navegador Real)

Testes de integração validam Page Objects com interações reais de navegador, preenchendo a lacuna entre testes unitários (mockados) e testes E2E (fluxos completos de usuário).

| Módulo | Testes | Navegador | Status |
|--------|--------|-----------|--------|
| **LoginPage** | 9 | Chrome | ✅ Completo |
| **InventoryPage** | 9 | Chrome | ✅ Completo |
| **CartPage** | 10 | Chrome | ✅ Completo |
| **CheckoutStepOnePage** | 15 | Chrome | ✅ Completo |
| **CheckoutStepTwoPage** | 13 | Chrome | ✅ Completo |
| **TOTAL** | **56** | **Real** | **Completo** |

**Principais Diferenças dos Testes Unitários:**
- ✅ Selenium WebDriver Real (não mockado)
- ✅ Validação de elementos DOM reais
- ✅ Verificação verdadeira de locators
- ✅ Testes de interação com navegador
- ✅ Mais rápido que E2E (sem fluxos completos)
- ✅ Cobertura completa de Page Objects (100%)

### Cenários de Teste

**Testes de Smoke**
- ✅ Homepage carrega e exibe corretamente
- ✅ Elementos de formulário de login presentes e funcionais
- ✅ Autenticação de usuário válido
- ✅ Rejeição de credenciais inválidas

**Login de Usuário**
- ✅ Autenticação de usuário válido (standard_user)
- ✅ Rejeição de credenciais inválidas
- ✅ Detecção de usuário bloqueado (locked_out_user)
- ✅ Fluxo de logout bem-sucedido

**Carrinho de Compras**
- ✅ Adicionar produto único ao carrinho
- ✅ Adicionar múltiplos produtos ao carrinho
- ✅ Visualizar conteúdo do carrinho
- ✅ Remover produto do carrinho
- ✅ Continuar comprando do carrinho
- ✅ Persistência do carrinho através de navegação

**Checkout**
- ✅ Completar checkout com informações válidas
- ✅ Validação para campos obrigatórios
- ✅ Resumo do pedido com detalhes de preço
- ✅ Cancelar checkout e retornar ao carrinho
- ✅ Mensagem de confirmação do pedido
- ✅ Limpeza do carrinho pós-compra

## 📊 Relatórios de Teste

Relatórios são gerados no diretório `reports/` e automaticamente excluídos do controle de versão.

```bash
# Gerar relatório Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```

## 🔧 CI/CD

O projeto usa **GitHub Actions** para integração contínua:

- ✅ **Testes automatizados** em todo push e pull request
- ✅ **Python 3.14** versão estável mais recente
- ✅ **Execução headless** de navegador em ambiente CI
- ✅ **Verificações de qualidade de código** (Black, Flake8, Pylint)
- ✅ **Artefatos de teste** enviados para revisão
- ✅ **Relatórios Allure** publicados no GitHub Pages com histórico

**Ver Relatórios de Teste:** [https://brunoccalmeida.github.io/uat-automation-framework/](https://brunoccalmeida.github.io/uat-automation-framework/)

Os relatórios incluem:
- Tendências e histórico de execução de testes (últimas 20 execuções)
- Resultados detalhados de testes com screenshots em caso de falha
- Métricas de duração e rastreamento de performance
- Categorização por features e cenários

Veja [.github/workflows/tests.yml](.github/workflows/tests.yml) para configuração do pipeline.

## 🛠️ Stack Tecnológica

- **Python 3.14**: Linguagem principal
- **Selenium 4**: Automação de navegador
- **Behave**: Framework de testes BDD/E2E
- **Pytest**: Framework de testes unitários
- **Allure**: Relatórios de teste com histórico e tendências
- **Poetry**: Gerenciamento de dependências
- **GitHub Actions**: Pipeline de CI/CD
- **GitHub Pages**: Hospedagem de relatórios de teste ao vivo

## 🎯 Roadmap

Melhorias futuras seguindo as melhores práticas da indústria:

- [ ] **Execução Paralela** - pytest-xdist para execuções de teste mais rápidas
- [ ] **Testes Cross-browser** - Suporte para Firefox e Edge
- [ ] **Containerização Docker** - Ambientes de execução consistentes
- [ ] **Testes de Regressão Visual** - Integração Percy/Applitools
- [ ] **Testes de API** - Feedback mais rápido com testes em nível de API

## 🤝 Contribuindo

Este é um projeto de portfólio demonstrando práticas profissionais de automação UAT seguindo:
- **Pirâmide de Testes**: Testes Unit → Integration → E2E (separação adequada de camadas)
- **TDD/BDD Outside-in**: Ciclo Red-Green-Refactor para todo código de produção
- **Page Object Model**: Separação limpa de lógica de teste de interações de página
- **Esperas Explícitas**: Sem `time.sleep()` - estratégias apropriadas de espera do Selenium
- **Commits Atômicos**: Formato Conventional Commits para histórico claro
- **Código Auto-documentado**: Docstrings abrangentes e type hints
- **Integração CI/CD**: Testes automatizados em todo push
- **Relatórios Ao Vivo**: Hospedagem no GitHub Pages com relatórios Allure e histórico

## 📚 Histórico do Projeto

**Nota de Migração**: Este framework foi originalmente desenvolvido para Parabank (demo bancário) e migrado com sucesso para Sauce Demo em <1 hora, provando a robustez de sua arquitetura. Todos os padrões de design principais (BDD, POM, melhores práticas Selenium) permaneceram inalterados, demonstrando verdadeira portabilidade de framework.

## 📄 Licença

Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Autor**: Bruno Almeida
**Propósito**: Portfólio profissional e demonstração de automação UAT
