# UAT Automation Framework

[![Tests](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/brunoccalmeida/uat-automation-framework/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/brunoccalmeida/uat-automation-framework/branch/master/graph/badge.svg)](https://codecov.io/gh/brunoccalmeida/uat-automation-framework)
[![Python Version](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[English](README.md)** | **[Português (Brasil)](README.pt-BR.md)** | **[Español]**

📊 **[Ver Informe de Pruebas](https://brunoccalmeida.github.io/uat-automation-framework/)**

Framework completo de automatización UAT utilizando Python, Behave (BDD) y Selenium para probar la aplicación e-commerce **Sauce Demo**.

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

> **Nota**: Originalmente desarrollado para Parabank (demo bancario), migrado a Sauce Demo debido a problemas de inestabilidad de la instancia pública de Parabank. La arquitectura del framework permanece intacta y demuestra prácticas profesionales de testing.

## 🎯 Propósito

Este framework demuestra prácticas profesionales de automatización UAT para aplicaciones web, incluyendo:
- **Aplicación Objetivo**: [Sauce Demo](https://www.saucedemo.com) - demo e-commerce estable de Sauce Labs
- Behavior-Driven Development (BDD) con Behave
- Patrón de diseño Page Object Model
- Reportes completos con Allure
- Usuarios de prueba preconfigurados (sin necesidad de gestión de credenciales)

### Usuarios de Prueba

Sauce Demo proporciona usuarios de prueba preconfigurados (contraseña: `secret_sauce` para todos):

- `standard_user` - Usuario normal, sin problemas
- `locked_out_user` - Usuario bloqueado
- `problem_user` - Usuario con fallos visuales
- `performance_glitch_user` - Usuario con problemas de rendimiento
- `error_user` - Usuario que encuentra errores
- `visual_user` - Usuario con variaciones de prueba visual

**Seguridad**: No es necesario almacenar credenciales - los usuarios son proporcionados por la aplicación demo.

## 🏗️ Arquitectura

```
uat-automation-framework/
├── core/              # Núcleo del framework (config, drivers, utilidades)
├── pages/             # Page Object Models
├── features/          # Archivos de features BDD y definiciones de steps
├── tests/             # Pruebas unitarias de los componentes del framework
└── reports/           # Informes de ejecución de pruebas (gitignored)
```

### Paradigma de Diseño: Enfoque Híbrido Pragmático

Este framework utiliza un **enfoque híbrido OOP/Funcional**, eligiendo el paradigma correcto para cada componente:

**Programación Orientada a Objetos (60-70%)**
- **Page Objects**: Encapsulan estado e interacciones de la página (ajuste natural para automatización de UI)
- **Driver Manager**: Gestiona ciclo de vida y estado del WebDriver
- **Clases Base**: Funcionalidad compartida a través de herencia cuando es apropiado

**Programación Funcional (30-40%)**
- **Utilidades & Helpers**: Funciones puras para transformación y generación de datos
- **Carga de Configuración**: Operaciones sin estado
- **Definiciones de Steps**: Steps de Behave son naturalmente funcionales

**Justificación:**
- **Pragmatismo sobre pureza**: Usa OOP donde los patrones Selenium/Page Object encajan naturalmente
- **Testabilidad**: Funciones puras para lógica de negocio facilitan pruebas unitarias
- **Estándares de la industria**: Page Object Model es esperado en automatización de pruebas profesional
- **Mantenibilidad**: Patrones familiares reducen carga cognitiva para colaboradores
- **Zen de Python**: "La practicidad supera la pureza" - elige lo que funciona mejor para cada caso

## 🚀 Primeros Pasos

### Requisitos Previos

- Python 3.14+
- Poetry (gestión de dependencias)
- Navegador Chrome

### Instalación

```bash
# Instalar dependencias
poetry install

# Instalar hooks de pre-commit (configuración única)
poetry run pre-commit install
```

**Hooks de Pre-commit:**
El framework usa hooks de pre-commit para mantener calidad de código automáticamente:
- ✅ **Black**: Formateo de código (88 caracteres por línea)
- ✅ **Flake8**: Linting y aplicación de guía de estilo
- ✅ **Pylint**: Análisis de código para errores y code smells
- ✅ **Seguridad**: Detección de claves privadas, conflictos de merge
- ✅ **Calidad**: Trailing whitespace, validación YAML

Los hooks se ejecutan automáticamente en `git commit`. Ejecución manual: `pre-commit run --all-files`

### Ejecutando Pruebas

**Pruebas BDD/E2E (Behave):**
```bash
# Ejecutar todas las pruebas E2E (headless por defecto)
poetry run behave

# Ejecutar feature específica
poetry run behave features/smoke.feature
poetry run behave features/login.feature

# Ejecutar con navegador visible (útil para debugging)
poetry run behave -Dheadless=false

# Sobrescribir a headless si es necesario
poetry run behave -Dheadless=true

# Ejecutar headless vía variable de entorno (útil para CI/CD)
$env:HEADLESS="true"; poetry run behave  # PowerShell
export HEADLESS=true && poetry run behave  # Bash

# Ejecutar con reporte Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# Generar y visualizar reporte Allure
allure serve reports/allure-results
```

**Pruebas Unitarias (Pytest):**
```bash
# Ejecutar todas las pruebas unitarias
poetry run pytest tests/ -v

# Ejecutar con reporte de cobertura
poetry run pytest tests/ --cov=core --cov=pages --cov-report=term-missing

# Ejecutar módulo de prueba específico
poetry run pytest tests/test_login_page.py -v

# Ejecutar todas las pruebas (unit + integration + E2E)
poetry run pytest tests/ && poetry run pytest tests/integration/ && poetry run behave
```

**Pruebas de Integración (Pytest + Navegador Real):**
```bash
# Ejecutar todas las pruebas de integración
poetry run pytest tests/integration/ -v

# Ejecutar prueba de integración específica
poetry run pytest tests/integration/test_login_page_integration.py -v

# Ejecutar en modo headless
$env:HEADLESS="true"; poetry run pytest tests/integration/ -v  # PowerShell
export HEADLESS=true && poetry run pytest tests/integration/ -v  # Bash
```

**Configuración del Modo Headless:**

El framework se ejecuta en **modo headless por defecto** (mejor práctica: más rápido, menos recursos, consistente con CI/CD).

Prioridad de configuración:
1. **Parámetro CLI** (mayor): `-Dheadless=true/false`
2. **Variable de Entorno**: `HEADLESS=true/false`
3. **Archivo de Config** (menor): `config.yaml` (predeterminado: `true`)

Usa `-Dheadless=false` para debugging con navegador visible.

Ver [CONFIGURATION.md](CONFIGURATION.md) para opciones detalladas de configuración.

## 🧪 Estrategia de Pruebas

Este framework implementa la arquitectura completa de la **Pirámide de Pruebas** con tres capas distintas:

```
        Pruebas E2E (BDD)         ← Lentas, Flujos Completos de Usuario
      /-------------------\
     / Pruebas Integración \      ← Medio, Página+Navegador
    /-----------------------\
   /   Pruebas Unitarias    \    ← Rápidas, Lógica de Componentes
  /---------------------------\
```

**Distribución por Capa:**
- **Pruebas Unitarias**: 132 pruebas (componentes del framework, 98% de cobertura)
- **Pruebas de Integración**: 56 pruebas (Page Objects + navegador real, 100% de cobertura)
- **Pruebas E2E**: 120 steps, 20 escenarios (jornadas completas de usuario)
- **Total**: 308 pruebas en todas las capas

**Cuándo Usar Cada Capa:**
| Tipo de Prueba | Propósito | Velocidad | Navegador | Ejemplo |
|----------------|-----------|-----------|-----------|---------|
| **Unitaria** | Lógica de componente | Rápida | Mockeado | "¿El método `login()` llama los métodos correctos?" |
| **Integración** | Página + DOM real | Media | Real | "¿Los campos de login existen y funcionan?" |
| **E2E** | Flujos completos de usuario | Lenta | Real | "¿El usuario puede completar login→comprar→checkout?" |

### Pruebas BDD/E2E (Behave)

| Feature | Escenarios | Steps | Estado |
|---------|------------|-------|--------|
| **Pruebas de Smoke** | 4/4 ✅ | 14/14 ✅ | Completo |
| **Login de Usuario** | 4/4 ✅ | 18/18 ✅ | Completo |
| **Carrito de Compras** | 6/6 ✅ | 35/35 ✅ | Completo |
| **Checkout** | 6/6 ✅ | 52/52 ✅ | Completo |
| **TOTAL** | **20** | **120** | **100%** |

### Pruebas Unitarias (Pytest)

| Módulo | Pruebas | Cobertura | Estado |
|--------|---------|-----------|--------|
| **BasePage** | 19 | 100% | ✅ Completo |
| **LoginPage** | 14 | 100% | ✅ Completo |
| **CartPage** | 13 | 100% | ✅ Completo |
| **InventoryPage** | 12 | 100% | ✅ Completo |
| **CheckoutStepOnePage** | 13 | 100% | ✅ Completo |
| **CheckoutStepTwoPage** | 15 | 100% | ✅ Completo |
| **CheckoutCompletePage** | 12 | 100% | ✅ Completo |
| **ConfigResolver** | 30 | 100% | ✅ Completo |
| **Pruebas de Smoke** | 4 | N/A | ✅ Completo |
| **TOTAL** | **132** | **98%** | **Completo** |

**Cobertura de Código:**
- **Módulo Pages**: 100% (194/194 statements)
- **Módulo Core**: 95% (62/65 statements)
- **Framework General**: 98%+

### Pruebas de Integración (Pytest + Navegador Real)

Las pruebas de integración validan Page Objects con interacciones reales de navegador, llenando el vacío entre pruebas unitarias (mockeadas) y pruebas E2E (flujos completos de usuario).

| Módulo | Pruebas | Navegador | Estado |
|--------|---------|-----------|--------|
| **LoginPage** | 9 | Chrome | ✅ Completo |
| **InventoryPage** | 9 | Chrome | ✅ Completo |
| **CartPage** | 10 | Chrome | ✅ Completo |
| **CheckoutStepOnePage** | 15 | Chrome | ✅ Completo |
| **CheckoutStepTwoPage** | 13 | Chrome | ✅ Completo |
| **TOTAL** | **56** | **Real** | **Completo** |

**Principales Diferencias de las Pruebas Unitarias:**
- ✅ Selenium WebDriver Real (no mockeado)
- ✅ Validación de elementos DOM reales
- ✅ Verificación verdadera de locators
- ✅ Pruebas de interacción con navegador
- ✅ Más rápido que E2E (sin flujos completos)
- ✅ Cobertura completa de Page Objects (100%)

### Escenarios de Prueba

**Pruebas de Smoke**
- ✅ Homepage carga y muestra correctamente
- ✅ Elementos de formulario de login presentes y funcionales
- ✅ Autenticación de usuario válido
- ✅ Rechazo de credenciales inválidas

**Login de Usuario**
- ✅ Autenticación de usuario válido (standard_user)
- ✅ Rechazo de credenciales inválidas
- ✅ Detección de usuario bloqueado (locked_out_user)
- ✅ Flujo de logout exitoso

**Carrito de Compras**
- ✅ Agregar producto único al carrito
- ✅ Agregar múltiples productos al carrito
- ✅ Visualizar contenido del carrito
- ✅ Remover producto del carrito
- ✅ Continuar comprando desde el carrito
- ✅ Persistencia del carrito a través de navegación

**Checkout**
- ✅ Completar checkout con información válida
- ✅ Validación para campos obligatorios
- ✅ Resumen del pedido con detalles de precio
- ✅ Cancelar checkout y retornar al carrito
- ✅ Mensaje de confirmación del pedido
- ✅ Limpieza del carrito post-compra

## 📊 Informes de Prueba

Los informes se generan en el directorio `reports/` y se excluyen automáticamente del control de versiones.

```bash
# Generar informe Allure
poetry run behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```

## 🔧 CI/CD

El proyecto usa **GitHub Actions** para integración continua:

- ✅ **Pruebas automatizadas** en cada push y pull request
- ✅ **Python 3.14** versión estable más reciente
- ✅ **Ejecución headless** de navegador en ambiente CI
- ✅ **Verificaciones de calidad de código** (Black, Flake8, Pylint)
- ✅ **Artefactos de prueba** subidos para revisión
- ✅ **Informes Allure** publicados en GitHub Pages con historial

**Ver Informes de Prueba:** [https://brunoccalmeida.github.io/uat-automation-framework/](https://brunoccalmeida.github.io/uat-automation-framework/)

Los informes incluyen:
- Tendencias e historial de ejecución de pruebas (últimas 20 ejecuciones)
- Resultados detallados de pruebas con screenshots en caso de fallo
- Métricas de duración y seguimiento de rendimiento
- Categorización por features y escenarios

Ver [.github/workflows/tests.yml](.github/workflows/tests.yml) para configuración del pipeline.

## 🛠️ Stack Tecnológico

- **Python 3.14**: Lenguaje principal
- **Selenium 4**: Automatización de navegador
- **Behave**: Framework de pruebas BDD/E2E
- **Pytest**: Framework de pruebas unitarias
- **Allure**: Informes de prueba con historial y tendencias
- **Poetry**: Gestión de dependencias
- **GitHub Actions**: Pipeline de CI/CD
- **GitHub Pages**: Hosting de informes de prueba en vivo

## 🎯 Roadmap

Mejoras futuras siguiendo las mejores prácticas de la industria:

- [ ] **Ejecución Paralela** - pytest-xdist para ejecuciones de prueba más rápidas
- [ ] **Pruebas Cross-browser** - Soporte para Firefox y Edge
- [ ] **Containerización Docker** - Ambientes de ejecución consistentes
- [ ] **Pruebas de Regresión Visual** - Integración Percy/Applitools
- [ ] **Pruebas de API** - Feedback más rápido con pruebas a nivel de API

## 🤝 Contribuir

Este es un proyecto de portafolio demostrando prácticas profesionales de automatización UAT siguiendo:
- **Pirámide de Pruebas**: Pruebas Unit → Integration → E2E (separación apropiada de capas)
- **TDD/BDD Outside-in**: Ciclo Red-Green-Refactor para todo código de producción
- **Page Object Model**: Separación limpia de lógica de prueba de interacciones de página
- **Esperas Explícitas**: Sin `time.sleep()` - estrategias apropiadas de espera de Selenium
- **Commits Atómicos**: Formato Conventional Commits para historial claro
- **Código Auto-documentado**: Docstrings completos y type hints
- **Integración CI/CD**: Pruebas automatizadas en cada push
- **Informes en Vivo**: Hosting en GitHub Pages con informes Allure e historial

## 📚 Historia del Proyecto

**Nota de Migración**: Este framework fue originalmente desarrollado para Parabank (demo bancario) y migrado exitosamente a Sauce Demo en <1 hora, probando la robustez de su arquitectura. Todos los patrones de diseño principales (BDD, POM, mejores prácticas Selenium) permanecieron sin cambios, demostrando verdadera portabilidad de framework.

## 📄 Licencia

Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**Autor**: Bruno Almeida
**Propósito**: Portafolio profesional y demostración de automatización UAT
