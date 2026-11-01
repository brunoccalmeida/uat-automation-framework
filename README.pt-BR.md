<!-- LTeX: language=pt-BR -->
<!-- translation-source: README.md sha256:7d3620305cc092040ab7e5c40779d355f6a865bf0c10dd1a8f2cda92538003e7 -->
# UAT Automation Framework

[![Tests](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml)
[![Security](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/security.yml/badge.svg)](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/brunoccalmeida/uat-automation-framework/branch/master/graph/badge.svg)](https://codecov.io/gh/brunoccalmeida/uat-automation-framework)
[![Python Version](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[English](README.md)** | **[Português (Brasil)]** | **[Español](README.es.md)**

📊 **[Ver o Relatório de Testes Mais Recente](https://brunoccalmeida.github.io/uat-automation-framework/)**

Framework completo de automação UAT usando Python, Behave (BDD) e Selenium para testar a aplicação de e-commerce **Sauce Demo**.

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

> **Nota**: Desenvolvido originalmente para o Parabank (demo bancário), foi migrado para o Sauce Demo por causa da instabilidade da instância pública do Parabank. A arquitetura do framework continua intacta e demonstra práticas profissionais de teste.

## 🎯 Objetivo

Este framework demonstra práticas profissionais de automação UAT para aplicações web, com:
- **Aplicação-alvo**: [Sauce Demo](https://www.saucedemo.com) - demo de e-commerce estável da Sauce Labs
- Behavior-Driven Development (BDD) com Behave
- Padrão de projeto Page Object Model
- Relatórios completos com Allure
- Usuários de teste pré-configurados (sem gestão de credenciais)

### Usuários de Teste

O Sauce Demo oferece usuários de teste pré-configurados (senha `secret_sauce` para todos):

- `standard_user` - Usuário normal, sem problemas
- `locked_out_user` - Usuário bloqueado
- `problem_user` - Usuário com falhas visuais
- `performance_glitch_user` - Usuário com problemas de desempenho
- `error_user` - Usuário que encontra erros
- `visual_user` - Usuário com variações para teste visual

**Segurança**: Nenhuma credencial precisa ser armazenada - os usuários são fornecidos pela própria aplicação de demonstração.

## 🏗️ Arquitetura

```
uat-automation-framework/
├── core/              # Núcleo do framework (config, drivers, utilitários)
├── pages/             # Page Object Models
├── features/          # Arquivos feature do BDD e step definitions
├── tests/             # Testes unitários dos componentes do framework
└── reports/           # Relatórios de execução (no .gitignore)
```

### Paradigma de Design: Abordagem Híbrida Pragmática

Este framework usa uma **abordagem híbrida de programação OO/funcional**, escolhendo o paradigma certo para cada componente:

**Programação Orientada a Objetos (60-70%)**
- **Page Objects**: Encapsulam o estado e as interações da página (encaixe natural para automação de UI)
- **Driver Manager**: Gerencia o ciclo de vida e o estado do WebDriver
- **Classes Base**: Funcionalidade compartilhada por herança onde faz sentido

**Programação Funcional (30-40%)**
- **Utilitários e Helpers**: Funções puras para transformação e geração de dados
- **Carregamento de Configuração**: Operações sem estado
- **Step Definitions**: Os steps do Behave são naturalmente funcionais

**Justificativa:**
- **Pragmatismo acima de pureza**: OO onde os padrões do Selenium/Page Object se encaixam naturalmente
- **Testabilidade**: Funções puras para a lógica de negócio tornam o teste unitário direto
- **Padrões da indústria**: O Page Object Model é esperado em automação de testes profissional
- **Manutenibilidade**: Padrões conhecidos reduzem a carga cognitiva de quem colabora
- **Zen of Python**: "Practicality beats purity" - escolher o que funciona melhor em cada caso

## 🚀 Começando

### Pré-requisitos

- Python 3.14+
- Poetry (gestão de dependências)
- Navegador Chrome ou Firefox (drivers gerenciados automaticamente pelo Selenium Manager)

### Instalação

```bash
# Instalar as dependências
poetry install

# Instalar os hooks de pre-commit (configuração única)
poetry run pre-commit install
```


**Hooks de Pre-commit e Configuração de Lint:**
Os hooks do `.pre-commit-config.yaml` são o portão de lint: o job `lint` do CI roda os mesmos hooks (`pre-commit run --all-files`), sem pastas excluídas e sem falhas ignoradas (`tests/test_lint_gate.py`). Os linters rodam pelo Poetry, então as versões vêm do `poetry.lock`.

- ✅ **Black**: Formatação de código (88 colunas)
- ✅ **Ruff**: Regras de estilo e de erro (`E`, `W`, `F` do flake8) e ordem dos imports (`I`), configuradas em `[tool.ruff.lint]` (`pyproject.toml`)
- ✅ **Pylint**: Erros e code smells (`[tool.pylint.*]` no `pyproject.toml`; cada checagem desligada tem o motivo ao lado)
- ✅ **Pyright**: Checagem estática de tipos (`[tool.pyright]` no `pyproject.toml`; o editor roda o mesmo verificador)
- ✅ **Segurança**: Detecta chaves privadas e conflitos de merge
- ✅ **Qualidade**: Espaços no fim da linha, validação de YAML, métricas dos READMEs e suas traduções

Os hooks rodam automaticamente no `git commit`. Para rodar todos manualmente: `pre-commit run --all-files`

### Executando os Testes

**Testes BDD/E2E (Behave):**
```bash
# Executar todos os testes E2E (headless por padrão)
poetry run behave

# Executar uma feature específica
poetry run behave features/smoke.feature
poetry run behave features/login.feature

# Executar com o navegador visível (útil para depurar)
poetry run behave -Dheadless=false

# Executar com Firefox (Chrome é o padrão)
poetry run behave -Dbrowser=firefox

# Executar o Firefox em modo visível
poetry run behave -Dbrowser=firefox -Dheadless=false

# Executar em modo headless via variável de ambiente (útil em CI/CD)
$env:HEADLESS="true"; poetry run behave  # PowerShell
export HEADLESS=true && poetry run behave  # Bash

# Trocar o navegador via variável de ambiente
$env:BROWSER="firefox"; poetry run behave  # PowerShell
export BROWSER=firefox && poetry run behave  # Bash

# Executar com relatório Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# Gerar e abrir o relatório Allure
allure serve reports/allure-results
```

**Executando Testes por Tags:**

O framework usa um sistema hierárquico de tags para filtrar os testes com precisão:

```bash
# Por camada de teste
poetry run behave --tags=@e2e              # Todos os testes E2E (padrão)

# Por tipo de teste
poetry run behave --tags=@smoke            # Só os smoke tests críticos
poetry run behave --tags=@functional       # Cenários de caminho feliz
poetry run behave --tags=@negative         # Casos negativos/de borda
poetry run behave --tags=@user_journey     # Fluxos completos de usuário

# Por domínio/feature
poetry run behave --tags=@login            # Todos os testes de login (funcionais + negativos)
poetry run behave --tags=@cart             # Todos os testes de carrinho
poetry run behave --tags=@checkout         # Todos os testes de checkout
poetry run behave --tags=@sorting          # Todos os testes de ordenação

# Por prioridade/casos especiais
poetry run behave --tags=@critical         # Jornadas críticas de usuário
poetry run behave --tags=@edgecase         # Bugs conhecidos/casos de borda
poetry run behave --tags=@problem_user     # Cenários do problem_user

# Combinar tags (lógica E)
poetry run behave --tags=@cart --tags=@negative    # Só os testes negativos de carrinho
poetry run behave --tags=@functional --tags=@cart  # Só os testes funcionais de carrinho

# Excluir tags (lógica NÃO)
poetry run behave --tags=~@edgecase        # Tudo, menos os casos de borda
poetry run behave --tags=@e2e --tags=~@smoke  # E2E sem os smoke tests
```

**Hierarquia de Tags:**
- **Camada**: `@e2e` (todas as features usam)
- **Tipo**: `@functional` | `@negative` | `@user_journey` | `@smoke` | `@edgecase`
- **Domínio**: `@login` | `@cart` | `@checkout` | `@sorting`
- **Prioridade**: `@critical` | `@problem_user`

**Testes Cross-Browser:**

O framework suporta os navegadores Chrome e Firefox. Use as flags `-D` para sobrescrever a configuração padrão:

```bash
# Smoke tests com Firefox (headless)
poetry run behave --tags=@smoke -Dbrowser=firefox -Dheadless=true

# Smoke tests com Firefox (navegador visível)
poetry run behave --tags=@smoke -Dbrowser=firefox -Dheadless=false

# Todos os testes com Chrome (padrão)
poetry run behave -Dbrowser=chrome

# Sobrescrever vários valores de configuração
poetry run behave -Dbrowser=firefox -Dheadless=false -Dtimeout=15
```

**Navegadores suportados:**
- `chrome` (padrão) - Google Chrome com ChromeDriver
- `firefox` - Mozilla Firefox com GeckoDriver

**Nota**: O Selenium Manager baixa e gerencia os drivers dos navegadores automaticamente - não é preciso instalar nada à mão.


**Testes Unitários (Pytest):**
```bash
# Executar todos os testes unitários (execução paralela)
poetry run pytest tests/ -n auto -v

# Executar com relatório de cobertura (paralelo)
poetry run pytest tests/ -n auto --cov=core --cov=pages --cov-report=term-missing

# Executar um módulo de teste específico
poetry run pytest tests/test_login_page.py -v

# Executar sequencialmente (para depurar)
poetry run pytest tests/ -n 0 -v

# Executar todos os testes (unit + integração + E2E)
poetry run pytest tests/ -n auto && poetry run pytest tests/integration/ -n auto && poetry run behave
```

**Testes de Integração (Pytest + Navegador Real):**
```bash
# Executar todos os testes de integração (execução paralela)
poetry run pytest tests/integration/ -n auto -v

# Executar um teste de integração específico
poetry run pytest tests/integration/test_login_page_integration.py -v

# Executar em modo headless (paralelo)
$env:HEADLESS="true"; poetry run pytest tests/integration/ -n auto -v  # PowerShell
export HEADLESS=true && poetry run pytest tests/integration/ -n auto -v  # Bash
```

**Execução Paralela:**

Este framework suporta execução paralela de testes com `pytest-xdist`:
- **Desempenho**: 88% mais rápido (188 testes em ~37s contra ~305s)
- **Segurança**: Todos os testes são independentes (fixtures com escopo de função)
- **Automático**: Use `-n auto` para detectar os núcleos de CPU automaticamente
- **Depuração**: Use `-n 0` para desligar a paralelização

Veja [docs/PARALLEL_TESTING.md](docs/PARALLEL_TESTING.md) para a documentação detalhada.

**Configuração do Modo Headless:**

O framework roda em **modo headless por padrão** (boa prática: mais rápido, usa menos recursos, consistente com o CI/CD).

Prioridade da configuração:
1. **Parâmetro de CLI** (maior): `-Dheadless=true/false`
2. **Variável de Ambiente**: `HEADLESS=true/false`
3. **Arquivo de Configuração** (menor): `config.yaml` (padrão: `true`)

Use `-Dheadless=false` para depurar com o navegador visível.

Veja [CONFIGURATION.md](CONFIGURATION.md) para as opções de configuração detalhadas.

## 🔄 CI/CD

O projeto usa **GitHub Actions** para integração contínua:

- ✅ **Testes automatizados** em todo push e pull request
- ✅ **Python 3.14**, a versão estável mais recente
- ✅ Execução com **navegador headless** no ambiente de CI
- ✅ Checagens de **qualidade de código** (Black, Ruff, Pylint, Pyright)
- ✅ **Artefatos de teste** enviados para revisão
- ✅ **Relatórios Allure** publicados no GitHub Pages com histórico
- ✅ **Auditoria de vulnerabilidades** com `pip-audit` (PyPI/OSV) em todo pull request e diariamente, como segunda fonte ao lado do Dependabot (GitHub Advisory Database)

**Ver os Relatórios de Teste:** [https://brunoccalmeida.github.io/uat-automation-framework/](https://brunoccalmeida.github.io/uat-automation-framework/)

Os relatórios incluem:
- Tendências e histórico de execução (últimas 20 execuções)
- Resultados detalhados com screenshots nas falhas
- Métricas de duração e acompanhamento de desempenho
- Organização por features e cenários

Veja [.github/workflows/tests.yml](.github/workflows/tests.yml) e [.github/workflows/security.yml](.github/workflows/security.yml) para a configuração do pipeline.

**Auditando as dependências localmente** (mesmo comando e mesma versão travada do CI):

```bash
poetry sync --no-root            # deixa o ambiente idêntico ao poetry.lock
poetry run pip-audit --strict    # falha com qualquer vulnerabilidade conhecida ou pacote não auditável
```

Qualquer vulnerabilidade conhecida reprova o check `pip-audit`. Para aceitar uma, adicione `--ignore-vuln <ID>` no `security.yml` com a justificativa e a issue que acompanha a remoção.

## 🛠️ Stack Tecnológica

- **Python 3.14**: Linguagem principal
- **Selenium 4**: Automação de navegador
- **Behave**: Framework de testes BDD/E2E
- **Pytest**: Framework de testes unitários
- **Allure**: Relatórios de teste com histórico e tendências
- **Poetry**: Gestão de dependências
- **GitHub Actions**: Pipeline de CI/CD
- **GitHub Pages**: Hospedagem do relatório de testes ao vivo

## 🧪 Estratégia de Testes

Este framework implementa a arquitetura completa da **Pirâmide de Testes**, com três camadas distintas:

```
     Testes E2E (BDD)             ← Lentos, fluxos completos de usuário
      /-------------------\
     / Testes de Integração\      ← Médios, página + navegador
    /-----------------------\
   /    Testes Unitários     \    ← Rápidos, lógica de componente
  /---------------------------\
```

**Distribuição por Camada:**
- **Testes Unitários**: 374 testes (componentes do framework, 100% de cobertura dos Page Objects, proteções do CI)
- **Testes de Integração**: 71 testes (Page Objects + navegador real, incluindo a sincronização da navegação)
- **Testes E2E**: 55 cenários, 386 steps (jornadas completas de usuário)
- **Total**: 445 testes unitários/de integração + 55 cenários E2E

**Quando Usar Cada Camada:**
| Tipo de Teste | Propósito | Velocidade | Navegador | Exemplo |
|---------------|-----------|------------|-----------|---------|
| **Unitário** | Lógica de componente | Rápido | Mockado | "O `login()` chama os métodos corretos?" |
| **Integração** | Página + DOM real | Médio | Real | "Os campos de login existem e funcionam?" |
| **E2E** | Fluxos completos de usuário | Lento | Real | "O usuário consegue completar login→compra→checkout?" |

### Testes BDD/E2E (Behave)

| Feature | Fonte | Cenários | Steps | Status |
|---------|-------|----------|-------|--------|
| **Smoke Tests** | `features/smoke.feature` | 4 | 14 | ✅ Completo |
| **Login de Usuário** | `features/login.feature`, `features/login_negative.feature` | 9 | 42 | ✅ Completo |
| **Carrinho de Compras** | `features/cart.feature`, `features/cart_negative.feature` | 11 | 65 | ✅ Completo |
| **Checkout** | `features/checkout.feature`, `features/checkout_negative.feature` | 12 | 95 | ✅ Completo |
| **Ordenação de Produtos** | `features/product_sorting.feature`, `features/product_sorting_negative.feature`, `features/product_sorting_problem_user.feature` | 14 | 92 | ✅ Completo |
| **Jornada do Usuário** | `features/user_journey_purchase.feature`, `features/user_journey_variations.feature`, `features/problem_user_journey.feature` | 5 | 78 | ✅ Completo |
| **TOTAL** | | **55** | **386** | **100%** |

### Testes Unitários (Pytest)

| Módulo | Fonte | Testes | Cobertura | Status |
|--------|-------|--------|-----------|--------|
| **BasePage** | `tests/test_base_page.py` | 23 | 100% | ✅ Completo |
| **LoginPage** | `tests/test_login_page.py` | 14 | 100% | ✅ Completo |
| **CartPage** | `tests/test_cart_page.py` | 13 | 100% | ✅ Completo |
| **InventoryPage** | `tests/test_inventory_page.py` | 26 | 100% | ✅ Completo |
| **CheckoutStepOnePage** | `tests/test_checkout_step_one_page.py` | 13 | 100% | ✅ Completo |
| **CheckoutStepTwoPage** | `tests/test_checkout_step_two_page.py` | 15 | 100% | ✅ Completo |
| **CheckoutCompletePage** | `tests/test_checkout_complete_page.py` | 12 | 100% | ✅ Completo |
| **Config** | `tests/test_config.py` | 2 | 94% | ✅ Completo |
| **ConfigResolver** | `tests/test_config_resolver.py` | 40 | 100% | ✅ Completo |
| **DriverManager** | `tests/test_driver_manager.py` | 19 | 100% | ✅ Completo |
| **Step definitions (lógica OU, senha da config)** | `tests/test_login_steps.py`, `tests/test_smoke_steps.py` | 12 | N/A | ✅ Completo |
| **Smoke Tests** | `tests/test_smoke.py` | 4 | N/A | ✅ Completo |
| **Fixação das actions (CI)** | `tests/test_workflow_pinning.py` | 24 | N/A | ✅ Completo |
| **Portão do CI (check obrigatório)** | `tests/test_ci_gate.py` | 16 | N/A | ✅ Completo |
| **Upload para o Codecov (CI)** | `tests/test_codecov_upload.py` | 6 | N/A | ✅ Completo |
| **Regras do agente (tamanho, sincronia, diagnósticos do editor, code intelligence)** | `tests/test_agent_rules.py` | 28 | N/A | ✅ Completo |
| **Hook de saída de testes do agente** | `tests/test_filter_test_output.py` | 21 | N/A | ✅ Completo |
| **Portão de lint (pre-commit + CI + ordem de imports no editor, ruff no lugar do flake8)** | `tests/test_lint_gate.py` | 22 | N/A | ✅ Completo |
| **Métricas dos READMEs (sincronia por linha pela coluna Fonte, traduções)** | `tests/test_validate_readme_metrics.py` | 49 | N/A | ✅ Completo |
| **Portão de encoding (pre-commit, `.gitattributes`)** | `tests/test_check_text_encoding.py` | 12 | N/A | ✅ Completo |
| **Chave do cache do venv (CI, versão exata do Python)** | `tests/test_venv_cache_key.py` | 3 | N/A | ✅ Completo |
| **TOTAL** | | **374** | **100%** | **Completo** |

**Cobertura de Código:**
- **Total de statements:** 350
- **Cobertos:** 349 (99%)
- **Módulo Pages**: 100%
- **Módulo Core**: 99% (1 linha sem cobertura em `core/config.py`)

### Testes de Integração (Pytest + Navegador Real)

Os testes de integração validam os Page Objects com interações reais no navegador, preenchendo a lacuna entre os testes unitários (mockados) e os E2E (fluxos completos).

| Módulo | Fonte | Testes | Navegador | Status |
|--------|-------|--------|-----------|--------|
| **LoginPage** | `tests/integration/test_login_page_integration.py` | 9 | Chrome | ✅ Completo |
| **InventoryPage** | `tests/integration/test_inventory_page_integration.py` | 10 | Chrome | ✅ Completo |
| **InventoryPage (ordenação)** | `tests/integration/test_inventory_sorting_integration.py` | 1 | Chrome | ✅ Completo |
| **CartPage** | `tests/integration/test_cart_page_integration.py` | 10 | Chrome | ✅ Completo |
| **CheckoutStepOnePage** | `tests/integration/test_checkout_step_one_integration.py` | 15 | Chrome | ✅ Completo |
| **CheckoutStepTwoPage** | `tests/integration/test_checkout_step_two_integration.py` | 13 | Chrome | ✅ Completo |
| **Sincronização da navegação** | `tests/integration/test_navigation_integration.py` | 13 | Chrome | ✅ Completo |
| **TOTAL** | | **71** | **Real** | **Completo** |

**Diferenças em Relação aos Testes Unitários:**
- ✅ Selenium WebDriver real (não mockado)
- ✅ Validação de elementos reais do DOM
- ✅ Verificação real dos locators
- ✅ Teste das interações com o navegador
- ✅ Mais rápidos que os E2E (sem fluxos completos)
- ✅ Cobertura completa dos Page Objects (100%)

### Cenários de Teste

**Smoke Tests**
- ✅ A página inicial carrega e é exibida corretamente
- ✅ Elementos do formulário de login presentes e funcionando
- ✅ Autenticação de usuário válido
- ✅ Rejeição de credenciais inválidas

**Login de Usuário**
- ✅ Autenticação de usuário válido (standard_user)
- ✅ Rejeição de credenciais inválidas
- ✅ Detecção de usuário bloqueado (locked_out_user)
- ✅ Fluxo de logout bem-sucedido

**Carrinho de Compras**
- ✅ Adicionar um produto ao carrinho
- ✅ Adicionar vários produtos ao carrinho
- ✅ Ver o conteúdo do carrinho
- ✅ Remover um produto do carrinho
- ✅ Continuar comprando a partir do carrinho
- ✅ Carrinho mantido durante a navegação

**Checkout**
- ✅ Checkout completo com informações válidas
- ✅ Validação dos campos obrigatórios
- ✅ Resumo do pedido com detalhes de preço
- ✅ Cancelar o checkout e voltar ao carrinho
- ✅ Mensagem de confirmação do pedido
- ✅ Carrinho limpo após a compra

### Casos de Borda e Bugs Conhecidos

Alguns usuários do Sauce Demo (principalmente o `problem_user`) foram projetados de propósito para apresentar bugs ou comportamentos fora do padrão, como falhas de ordenação ou defeitos visuais. Para manter a suíte clara e fácil de manter:

- **Cenários de usuário normal** ficam nos respectivos arquivos feature (ex.: `product_sorting.feature`).
- **Casos de borda e bugs conhecidos** (como o bug de ordenação do `problem_user`) ficam isolados em arquivos feature dedicados (ex.: [`product_sorting_problem_user.feature`](features/product_sorting_problem_user.feature)), com a tag `@edgecase`.

Por que essa separação?
- Mantém os requisitos de negócio e os testes de regressão limpos e focados
- Facilita rodar só os cenários de casos de borda: `poetry run behave --tags=edgecase`
- Simplifica a manutenção quando bugs são corrigidos ou novos casos de borda aparecem
- Melhora os relatórios e a comunicação com as partes interessadas

> Se o comportamento da aplicação mudar (ex.: um bug for corrigido), atualize ou remova o cenário de caso de borda correspondente.

## 📊 Relatórios de Teste

Os relatórios são gerados na pasta `reports/` e ficam fora do controle de versão automaticamente.

```bash
# Gerar o relatório Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```

## 🎯 Roadmap

Melhorias futuras seguindo as melhores práticas da indústria:

- [x] **Execução Paralela** - pytest-xdist implementado (88% mais rápido)
- [x] **Testes Cross-browser** - Suporte a Chrome + Firefox com hierarquia CLI/ENV/config
- [x] **Matriz no CI** - Smoke tests rodam nos dois navegadores automaticamente
- [ ] **Containerização com Docker** - Ambientes de execução consistentes
- [ ] **Testes de Regressão Visual** - Integração com Percy/Applitools
- [ ] **Testes de API** - Feedback mais rápido com testes no nível da API

## 🤝 Contribuindo

Este é um projeto de portfólio que demonstra práticas profissionais de automação UAT, seguindo:
- **Pirâmide de Testes**: Testes unitários → integração → E2E (separação correta das camadas)
- **TDD/BDD de fora para dentro**: Ciclo Red-Green-Refactor para todo código de produção
- **Page Object Model**: Separação clara entre a lógica de teste e as interações com a página
- **Esperas Explícitas**: Nada de `time.sleep()` - estratégias de espera adequadas do Selenium
- **Commits Atômicos**: Formato Conventional Commits para um histórico claro
- **Código Autodocumentado**: Docstrings completas e type hints
- **Integração com CI/CD**: Testes automatizados a cada push
- **Relatórios ao Vivo**: Hospedagem no GitHub Pages com relatórios Allure e histórico

## 📚 Histórico do Projeto

**Nota de Migração**: Este framework foi desenvolvido originalmente para o Parabank (demo bancário) e migrado com sucesso para o Sauce Demo em menos de 1 hora, o que comprova a robustez da arquitetura. Todos os padrões de design centrais (BDD, POM, boas práticas de Selenium) continuaram iguais, demonstrando a portabilidade real do framework.

## 📄 Licença

Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Autor**: Bruno Almeida, QA Automation Engineer / SDET · [LinkedIn](https://www.linkedin.com/in/brunoccalmeida/)
**Propósito**: Portfólio profissional e demonstração de automação UAT
