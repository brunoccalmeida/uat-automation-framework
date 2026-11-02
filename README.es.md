<!-- LTeX: language=es -->
<!-- translation-source: README.md sha256:0492a00cc437963304862c95cbf1143d2ed72ad102529e11e5a7d00b62d24a2c -->
# UAT Automation Framework

[![Tests](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml)
[![Security](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/security.yml/badge.svg)](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/brunoccalmeida/uat-automation-framework/branch/master/graph/badge.svg)](https://codecov.io/gh/brunoccalmeida/uat-automation-framework)
[![Python Version](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[English](README.md)** | **[Português (Brasil)](README.pt-BR.md)** | **[Español]**

📊 **[Ver el Informe de Pruebas Más Reciente](https://brunoccalmeida.github.io/uat-automation-framework/)**

Framework completo de automatización UAT con Python, Behave (BDD) y Selenium para probar la aplicación de e-commerce **Sauce Demo**.

## 📑 Índice

- [Propósito](#-propósito)
- [Arquitectura](#️-arquitectura)
- [Primeros Pasos](#-primeros-pasos)
- [Estrategia de Pruebas](#-estrategia-de-pruebas)
- [Stack Tecnológico](#️-stack-tecnológico)
- [CI/CD](#-cicd)
- [Historia del Proyecto](#-historia-del-proyecto)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

> **Nota**: Desarrollado originalmente para Parabank (demo bancaria), se migró a Sauce Demo por la inestabilidad de la instancia pública de Parabank. La arquitectura del framework sigue intacta y demuestra prácticas profesionales de testing.

## 🎯 Propósito

Este framework demuestra prácticas profesionales de automatización UAT para aplicaciones web, con:
- **Aplicación objetivo**: [Sauce Demo](https://www.saucedemo.com) - demo de e-commerce estable de Sauce Labs
- Behavior-Driven Development (BDD) con Behave
- Patrón de diseño Page Object Model
- Informes completos con Allure
- Usuarios de prueba preconfigurados (sin gestión de credenciales)

### Usuarios de Prueba

Sauce Demo ofrece usuarios de prueba preconfigurados (contraseña `secret_sauce` para todos):

- `standard_user` - Usuario normal, sin problemas
- `locked_out_user` - Usuario bloqueado
- `problem_user` - Usuario con fallos visuales
- `performance_glitch_user` - Usuario con problemas de rendimiento
- `error_user` - Usuario que encuentra errores
- `visual_user` - Usuario con variaciones para pruebas visuales

**Seguridad**: No hace falta almacenar credenciales - los usuarios los proporciona la propia aplicación de demostración.

## 🏗️ Arquitectura

```
uat-automation-framework/
├── core/              # Núcleo del framework (config, drivers, utilidades)
├── pages/             # Page Object Models
├── features/          # Archivos feature del BDD y step definitions
├── tests/             # Pruebas unitarias de los componentes del framework
└── reports/           # Informes de ejecución (en .gitignore)
```

### Paradigma de Diseño: Enfoque Híbrido Pragmático

Este framework usa un **enfoque híbrido de programación OO/funcional**, eligiendo el paradigma adecuado para cada componente:

**Programación Orientada a Objetos (60-70%)**
- **Page Objects**: Encapsulan el estado y las interacciones de la página (encaje natural para automatización de UI)
- **Driver Manager**: Gestiona el ciclo de vida y el estado del WebDriver
- **Clases Base**: Funcionalidad compartida por herencia donde tiene sentido

**Programación Funcional (30-40%)**
- **Utilidades y Helpers**: Funciones puras para transformación y generación de datos
- **Carga de Configuración**: Operaciones sin estado
- **Step Definitions**: Los steps de Behave son naturalmente funcionales

**Justificación:**
- **Pragmatismo sobre pureza**: OO donde los patrones de Selenium/Page Object encajan de forma natural
- **Testabilidad**: Las funciones puras para la lógica de negocio facilitan las pruebas unitarias
- **Estándares de la industria**: El Page Object Model es lo esperado en automatización de pruebas profesional
- **Mantenibilidad**: Los patrones conocidos reducen la carga cognitiva de quien colabora
- **Zen of Python**: "Practicality beats purity" - elegir lo que mejor funciona en cada caso

## 🚀 Primeros Pasos

### Requisitos Previos

- Python 3.14+
- Poetry (gestión de dependencias)
- Navegador Chrome o Firefox (drivers gestionados automáticamente por Selenium Manager)

### Instalación

```bash
# Instalar las dependencias
poetry install

# Instalar los hooks de pre-commit (configuración única)
poetry run pre-commit install
```


**Hooks de Pre-commit y Configuración de Lint:**
Los hooks de `.pre-commit-config.yaml` son la puerta de lint: el job `lint` del CI ejecuta los mismos hooks (`pre-commit run --all-files`), sin carpetas excluidas y sin fallos ignorados (`tests/test_lint_gate.py`). Los linters se ejecutan con Poetry, así que sus versiones vienen del `poetry.lock`.

- ✅ **Black**: Formato de código (88 columnas)
- ✅ **Ruff**: Reglas de estilo y de error (`E`, `W`, `F` de flake8) y orden de imports (`I`), configuradas en `[tool.ruff.lint]` (`pyproject.toml`)
- ✅ **Pylint**: Errores y code smells (`[tool.pylint.*]` en `pyproject.toml`; cada chequeo desactivado tiene su motivo al lado)
- ✅ **Pyright**: Chequeo estático de tipos (`[tool.pyright]` en `pyproject.toml`; el editor usa el mismo verificador)
- ✅ **Seguridad**: Detecta claves privadas y conflictos de merge
- ✅ **Calidad**: Espacios al final de línea, validación de YAML, métricas de los READMEs y sus traducciones

Los hooks se ejecutan automáticamente en `git commit`. Para ejecutarlos todos a mano: `pre-commit run --all-files`

### Ejecutando las Pruebas

**Pruebas BDD/E2E (Behave):**
```bash
# Ejecutar todas las pruebas E2E (headless por defecto)
poetry run behave

# Ejecutar una feature específica
poetry run behave features/smoke.feature
poetry run behave features/login.feature

# Ejecutar con el navegador visible (útil para depurar)
poetry run behave -Dheadless=false

# Ejecutar con Firefox (Chrome es el predeterminado)
poetry run behave -Dbrowser=firefox

# Ejecutar Firefox en modo visible
poetry run behave -Dbrowser=firefox -Dheadless=false

# Ejecutar en modo headless con una variable de entorno (útil en CI/CD)
$env:HEADLESS="true"; poetry run behave  # PowerShell
export HEADLESS=true && poetry run behave  # Bash

# Cambiar el navegador con una variable de entorno
$env:BROWSER="firefox"; poetry run behave  # PowerShell
export BROWSER=firefox && poetry run behave  # Bash

# Ejecutar con informe Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# Generar y abrir el informe Allure
allure serve reports/allure-results
```

**Ejecutando Pruebas por Tags:**

El framework usa un sistema jerárquico de tags para filtrar las pruebas con precisión:

```bash
# Por capa de prueba
poetry run behave --tags=@e2e              # Todas las pruebas E2E (predeterminado)

# Por tipo de prueba
poetry run behave --tags=@smoke            # Solo las smoke tests críticas
poetry run behave --tags=@functional       # Escenarios de camino feliz
poetry run behave --tags=@negative         # Casos negativos/límite
poetry run behave --tags=@user_journey     # Flujos completos de usuario

# Por dominio/feature
poetry run behave --tags=@login            # Todas las pruebas de login (funcionales + negativas)
poetry run behave --tags=@cart             # Todas las pruebas de carrito
poetry run behave --tags=@checkout         # Todas las pruebas de checkout
poetry run behave --tags=@sorting          # Todas las pruebas de ordenación

# Por prioridad/casos especiales
poetry run behave --tags=@critical         # Jornadas críticas de usuario
poetry run behave --tags=@edgecase         # Bugs conocidos/casos límite
poetry run behave --tags=@problem_user     # Escenarios del problem_user

# Combinar tags (lógica Y)
poetry run behave --tags=@cart --tags=@negative    # Solo las pruebas negativas de carrito
poetry run behave --tags=@functional --tags=@cart  # Solo las pruebas funcionales de carrito

# Excluir tags (lógica NO)
poetry run behave --tags=~@edgecase        # Todo, menos los casos límite
poetry run behave --tags=@e2e --tags=~@smoke  # E2E sin las smoke tests
```

**Jerarquía de Tags:**
- **Capa**: `@e2e` (todas las features la usan)
- **Tipo**: `@functional` | `@negative` | `@user_journey` | `@smoke` | `@edgecase`
- **Dominio**: `@login` | `@cart` | `@checkout` | `@sorting`
- **Prioridad**: `@critical` | `@problem_user`

**Pruebas Cross-Browser:**

El framework soporta los navegadores Chrome y Firefox. Usa los flags `-D` para sobrescribir la configuración predeterminada:

```bash
# Smoke tests con Firefox (headless)
poetry run behave --tags=@smoke -Dbrowser=firefox -Dheadless=true

# Smoke tests con Firefox (navegador visible)
poetry run behave --tags=@smoke -Dbrowser=firefox -Dheadless=false

# Todas las pruebas con Chrome (predeterminado)
poetry run behave -Dbrowser=chrome

# Sobrescribir varios valores de configuración
poetry run behave -Dbrowser=firefox -Dheadless=false -Dtimeout=15
```

**Navegadores soportados:**
- `chrome` (predeterminado) - Google Chrome con ChromeDriver
- `firefox` - Mozilla Firefox con GeckoDriver

**Nota**: Selenium Manager descarga y gestiona los drivers de los navegadores automáticamente - no hace falta instalar nada a mano.


**Pruebas Unitarias (Pytest):**
```bash
# Ejecutar todas las pruebas unitarias (ejecución paralela)
poetry run pytest tests/ -n auto -v

# Ejecutar con informe de cobertura (paralelo)
poetry run pytest tests/ -n auto --cov=core --cov=pages --cov-report=term-missing

# Ejecutar un módulo de prueba específico
poetry run pytest tests/test_login_page.py -v

# Ejecutar secuencialmente (para depurar)
poetry run pytest tests/ -n 0 -v

# Ejecutar todas las pruebas (unit + integración + E2E)
poetry run pytest tests/ -n auto && poetry run pytest tests/integration/ -n auto && poetry run behave
```

**Pruebas de Integración (Pytest + Navegador Real):**
```bash
# Ejecutar todas las pruebas de integración (ejecución paralela)
poetry run pytest tests/integration/ -n auto -v

# Ejecutar una prueba de integración específica
poetry run pytest tests/integration/test_login_page_integration.py -v

# Ejecutar en modo headless (paralelo)
$env:HEADLESS="true"; poetry run pytest tests/integration/ -n auto -v  # PowerShell
export HEADLESS=true && poetry run pytest tests/integration/ -n auto -v  # Bash
```

**Ejecución Paralela:**

Este framework soporta la ejecución paralela de pruebas con `pytest-xdist`:
- **Rendimiento**: 88% más rápido (188 pruebas en ~37s frente a ~305s)
- **Seguridad**: Todas las pruebas son independientes (fixtures con alcance de función)
- **Automático**: Usa `-n auto` para detectar los núcleos de CPU automáticamente
- **Depuración**: Usa `-n 0` para desactivar la paralelización

Consulta [docs/PARALLEL_TESTING.md](docs/PARALLEL_TESTING.md) para la documentación detallada.

**Configuración del Modo Headless:**

El framework se ejecuta en **modo headless por defecto** (buena práctica: más rápido, usa menos recursos, coherente con el CI/CD).

Prioridad de la configuración:
1. **Parámetro de CLI** (mayor): `-Dheadless=true/false`
2. **Variable de Entorno**: `HEADLESS=true/false`
3. **Archivo de Configuración** (menor): `config.yaml` (predeterminado: `true`)

Usa `-Dheadless=false` para depurar con el navegador visible.

Consulta [CONFIGURATION.md](CONFIGURATION.md) para las opciones de configuración detalladas.

## 🔄 CI/CD

El proyecto usa **GitHub Actions** para la integración continua:

- ✅ **Pruebas automatizadas** en cada push y pull request
- ✅ **Python 3.14**, la versión estable más reciente
- ✅ Ejecución con **navegador headless** en el entorno de CI
- ✅ Chequeos de **calidad de código** (Black, Ruff, Pylint, Pyright)
- ✅ **Artefactos de prueba** subidos para revisión
- ✅ **Informes Allure** publicados en GitHub Pages con historial
- ✅ **Auditoría de vulnerabilidades** con `pip-audit` (PyPI/OSV) en cada pull request y a diario, como segunda fuente junto a Dependabot (GitHub Advisory Database)

**Ver los Informes de Prueba:** [https://brunoccalmeida.github.io/uat-automation-framework/](https://brunoccalmeida.github.io/uat-automation-framework/)

Los informes incluyen:
- Tendencias e historial de ejecución (últimas 20 ejecuciones)
- Resultados detallados con capturas de pantalla en los fallos
- Métricas de duración y seguimiento del rendimiento
- Organización por features y escenarios

Consulta [.github/workflows/tests.yml](.github/workflows/tests.yml) y [.github/workflows/security.yml](.github/workflows/security.yml) para la configuración del pipeline.

**Auditando las dependencias en local** (mismo comando y misma versión fijada que el CI):

```bash
poetry sync --no-root            # deja el entorno idéntico al poetry.lock
poetry run pip-audit --strict    # falla con cualquier vulnerabilidad conocida o paquete no auditable
```

Cualquier vulnerabilidad conocida hace fallar el check `pip-audit`. Para aceptar una, añade `--ignore-vuln <ID>` en `security.yml` con la justificación y la issue que sigue su eliminación.

## 🛠️ Stack Tecnológico

- **Python 3.14**: Lenguaje principal
- **Selenium 4**: Automatización de navegador
- **Behave**: Framework de pruebas BDD/E2E
- **Pytest**: Framework de pruebas unitarias
- **Allure**: Informes de prueba con historial y tendencias
- **Poetry**: Gestión de dependencias
- **GitHub Actions**: Pipeline de CI/CD
- **GitHub Pages**: Alojamiento del informe de pruebas en vivo

## 🧪 Estrategia de Pruebas

Este framework implementa la arquitectura completa de la **Pirámide de Pruebas**, con tres capas distintas:

```
      Pruebas E2E (BDD)           ← Lentas, flujos completos de usuario
      /-------------------\
     / Pruebas Integración \      ← Medias, página + navegador
    /-----------------------\
   /    Pruebas Unitarias    \    ← Rápidas, lógica de componente
  /---------------------------\
```

**Distribución por Capa:**
- **Pruebas Unitarias**: 378 pruebas (componentes del framework, 100% de cobertura de los Page Objects, salvaguardas del CI)
- **Pruebas de Integración**: 71 pruebas (Page Objects + navegador real, incluida la sincronización de la navegación)
- **Pruebas E2E**: 55 escenarios, 386 steps (jornadas completas de usuario)
- **Total**: 449 pruebas unitarias/de integración + 55 escenarios E2E

**Cuándo Usar Cada Capa:**
| Tipo de Prueba | Propósito | Velocidad | Navegador | Ejemplo |
|----------------|-----------|-----------|-----------|---------|
| **Unitaria** | Lógica de componente | Rápida | Mockeado | "¿`login()` llama a los métodos correctos?" |
| **Integración** | Página + DOM real | Media | Real | "¿Los campos de login existen y funcionan?" |
| **E2E** | Flujos completos de usuario | Lenta | Real | "¿El usuario puede completar login→compra→checkout?" |

### Pruebas BDD/E2E (Behave)

| Feature | Fuente | Escenarios | Steps | Estado |
|---------|--------|------------|-------|--------|
| **Smoke Tests** | `features/smoke.feature` | 4 | 14 | ✅ Completo |
| **Login de Usuario** | `features/login.feature`, `features/login_negative.feature` | 9 | 42 | ✅ Completo |
| **Carrito de Compras** | `features/cart.feature`, `features/cart_negative.feature` | 11 | 65 | ✅ Completo |
| **Checkout** | `features/checkout.feature`, `features/checkout_negative.feature` | 12 | 95 | ✅ Completo |
| **Ordenación de Productos** | `features/product_sorting.feature`, `features/product_sorting_negative.feature`, `features/product_sorting_problem_user.feature` | 14 | 92 | ✅ Completo |
| **Jornada del Usuario** | `features/user_journey_purchase.feature`, `features/user_journey_variations.feature`, `features/problem_user_journey.feature` | 5 | 78 | ✅ Completo |
| **TOTAL** | | **55** | **386** | **100%** |

### Pruebas Unitarias (Pytest)

| Módulo | Fuente | Pruebas | Cobertura | Estado |
|--------|--------|---------|-----------|--------|
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
| **Step definitions (lógica O, contraseña de la config, page objects locales)** | `tests/test_login_steps.py`, `tests/test_smoke_steps.py`, `tests/test_step_page_objects.py` | 16 | N/A | ✅ Completo |
| **Smoke Tests** | `tests/test_smoke.py` | 4 | N/A | ✅ Completo |
| **Fijación de las actions (CI)** | `tests/test_workflow_pinning.py` | 24 | N/A | ✅ Completo |
| **Puerta del CI (check obligatorio)** | `tests/test_ci_gate.py` | 16 | N/A | ✅ Completo |
| **Subida a Codecov (CI)** | `tests/test_codecov_upload.py` | 6 | N/A | ✅ Completo |
| **Reglas del agente (tamaño, sincronía, diagnósticos del editor, code intelligence)** | `tests/test_agent_rules.py` | 28 | N/A | ✅ Completo |
| **Hook de salida de pruebas del agente** | `tests/test_filter_test_output.py` | 21 | N/A | ✅ Completo |
| **Puerta de lint (pre-commit + CI + orden de imports en el editor, ruff en lugar de flake8)** | `tests/test_lint_gate.py` | 22 | N/A | ✅ Completo |
| **Métricas de los READMEs (sincronía por fila desde la columna Fuente, traducciones)** | `tests/test_validate_readme_metrics.py` | 49 | N/A | ✅ Completo |
| **Puerta de codificación (pre-commit, `.gitattributes`)** | `tests/test_check_text_encoding.py` | 12 | N/A | ✅ Completo |
| **Clave de caché del venv (CI, versión exacta de Python)** | `tests/test_venv_cache_key.py` | 3 | N/A | ✅ Completo |
| **TOTAL** | | **378** | **100%** | **Completo** |

**Cobertura de Código:**
- **Total de statements:** 352
- **Cubiertos:** 351 (99%)
- **Módulo Pages**: 100%
- **Módulo Core**: 99% (1 línea sin cubrir en `core/config.py`)

### Pruebas de Integración (Pytest + Navegador Real)

Las pruebas de integración validan los Page Objects con interacciones reales en el navegador, cubriendo el hueco entre las pruebas unitarias (mockeadas) y las E2E (flujos completos).

| Módulo | Fuente | Pruebas | Navegador | Estado |
|--------|--------|---------|-----------|--------|
| **LoginPage** | `tests/integration/test_login_page_integration.py` | 9 | Chrome | ✅ Completo |
| **InventoryPage** | `tests/integration/test_inventory_page_integration.py` | 10 | Chrome | ✅ Completo |
| **InventoryPage (ordenación)** | `tests/integration/test_inventory_sorting_integration.py` | 1 | Chrome | ✅ Completo |
| **CartPage** | `tests/integration/test_cart_page_integration.py` | 10 | Chrome | ✅ Completo |
| **CheckoutStepOnePage** | `tests/integration/test_checkout_step_one_integration.py` | 15 | Chrome | ✅ Completo |
| **CheckoutStepTwoPage** | `tests/integration/test_checkout_step_two_integration.py` | 13 | Chrome | ✅ Completo |
| **Sincronización de la navegación** | `tests/integration/test_navigation_integration.py` | 13 | Chrome | ✅ Completo |
| **TOTAL** | | **71** | **Real** | **Completo** |

**Diferencias con las Pruebas Unitarias:**
- ✅ Selenium WebDriver real (no mockeado)
- ✅ Validación de elementos reales del DOM
- ✅ Verificación real de los locators
- ✅ Pruebas de las interacciones con el navegador
- ✅ Más rápidas que las E2E (sin flujos completos)
- ✅ Cobertura completa de los Page Objects (100%)

### Escenarios de Prueba

**Smoke Tests**
- ✅ La página de inicio carga y se muestra correctamente
- ✅ Elementos del formulario de login presentes y funcionando
- ✅ Autenticación de usuario válido
- ✅ Rechazo de credenciales inválidas

**Login de Usuario**
- ✅ Autenticación de usuario válido (standard_user)
- ✅ Rechazo de credenciales inválidas
- ✅ Detección de usuario bloqueado (locked_out_user)
- ✅ Flujo de logout correcto

**Carrito de Compras**
- ✅ Añadir un producto al carrito
- ✅ Añadir varios productos al carrito
- ✅ Ver el contenido del carrito
- ✅ Eliminar un producto del carrito
- ✅ Seguir comprando desde el carrito
- ✅ Carrito conservado durante la navegación

**Checkout**
- ✅ Checkout completo con información válida
- ✅ Validación de los campos obligatorios
- ✅ Resumen del pedido con detalle de precios
- ✅ Cancelar el checkout y volver al carrito
- ✅ Mensaje de confirmación del pedido
- ✅ Carrito vacío después de la compra

### Casos Límite y Bugs Conocidos

Algunos usuarios de Sauce Demo (sobre todo `problem_user`) están diseñados a propósito para mostrar bugs o comportamientos no estándar, como fallos de ordenación o defectos visuales. Para mantener la suite clara y fácil de mantener:

- **Los escenarios de usuario normal** están en sus respectivos archivos feature (p. ej., `product_sorting.feature`).
- **Los casos límite y bugs conocidos** (como el bug de ordenación de `problem_user`) están aislados en archivos feature dedicados (p. ej., [`product_sorting_problem_user.feature`](features/product_sorting_problem_user.feature)), con el tag `@edgecase`.

¿Por qué esta separación?
- Mantiene los requisitos de negocio y las pruebas de regresión limpios y enfocados
- Facilita ejecutar solo los escenarios de casos límite: `poetry run behave --tags=edgecase`
- Simplifica el mantenimiento cuando se corrigen bugs o aparecen nuevos casos límite
- Mejora los informes y la comunicación con las partes interesadas

> Si el comportamiento de la aplicación cambia (p. ej., se corrige un bug), actualiza o elimina el escenario de caso límite correspondiente.

## 📊 Informes de Prueba

Los informes se generan en la carpeta `reports/` y quedan fuera del control de versiones automáticamente.

```bash
# Generar el informe Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```

## 🎯 Roadmap

Mejoras futuras siguiendo las mejores prácticas de la industria:

- [x] **Ejecución Paralela** - pytest-xdist implementado (88% más rápido)
- [x] **Pruebas Cross-browser** - Soporte de Chrome + Firefox con jerarquía CLI/ENV/config
- [x] **Matriz en el CI** - Las smoke tests se ejecutan en los dos navegadores automáticamente
- [ ] **Contenerización con Docker** - Entornos de ejecución coherentes
- [ ] **Pruebas de Regresión Visual** - Integración con Percy/Applitools
- [ ] **Pruebas de API** - Feedback más rápido con pruebas a nivel de API

## 🤝 Contribuir

Este es un proyecto de portafolio que demuestra prácticas profesionales de automatización UAT, siguiendo:
- **Pirámide de Pruebas**: Pruebas unitarias → integración → E2E (separación correcta de las capas)
- **TDD/BDD de fuera hacia dentro**: Ciclo Red-Green-Refactor para todo el código de producción
- **Page Object Model**: Separación clara entre la lógica de prueba y las interacciones con la página
- **Esperas Explícitas**: Nada de `time.sleep()` - estrategias de espera adecuadas de Selenium
- **Commits Atómicos**: Formato Conventional Commits para un historial claro
- **Código Autodocumentado**: Docstrings completas y type hints
- **Integración con CI/CD**: Pruebas automatizadas en cada push
- **Informes en Vivo**: Alojamiento en GitHub Pages con informes Allure e historial

## 📚 Historia del Proyecto

**Nota de Migración**: Este framework se desarrolló originalmente para Parabank (demo bancaria) y se migró con éxito a Sauce Demo en menos de 1 hora, lo que demuestra la robustez de su arquitectura. Todos los patrones de diseño centrales (BDD, POM, buenas prácticas de Selenium) se mantuvieron, demostrando la portabilidad real del framework.

## 📄 Licencia

Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

---

**Autor**: Bruno Almeida, QA Automation Engineer / SDET · [LinkedIn](https://www.linkedin.com/in/brunoccalmeida/)
**Propósito**: Portafolio profesional y demostración de automatización UAT
