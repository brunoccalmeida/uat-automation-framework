# UAT Automation Framework - Coding Guidelines

## ⚠️ REGRA DE OURO: TDD É OBRIGATÓRIO
**NUNCA implemente código de produção sem antes ter um teste falhando.**

---

## 🔄 TDD/BDD Workflow (FLUXOGRAMA OBRIGATÓRIO)

### Para QUALQUER nova funcionalidade:

```
┌─────────────────────────────────────┐
│ 1. Feature Gherkin existe?          │
│    └─ NÃO → Escreva AGORA          │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 2. Steps definitions existem?       │
│    └─ NÃO → Escreva AGORA          │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 3. 🔴 RED: Execute behave            │
│    ✓ Deve FALHAR                     │
│    ✓ Documente o erro esperado       │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 4. 🟢 GREEN: Implemente MÍNIMO       │
│    ✓ Page Object com método básico  │
│    ✓ Execute behave após CADA método│
│    ✓ Repita até todos passarem       │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 5. 🔵 REFACTOR: Melhore código       │
│    ✓ Adicione unit tests             │
│    ✓ Otimize lógica                  │
│    ✓ Execute tudo novamente          │
└──────────────────────────────────────┘
```

### ❌ ANTI-PATTERNS (O QUE NUNCA FAZER):

```python
# ❌ ERRADO: Implementar Page Object primeiro
class InventoryPage:
    def select_sort_option(self, option):  # Código sem teste
        ...

# ✅ CORRETO: Feature → Steps → Executar (RED) → Implementar (GREEN)
@when('I select sort option "{option}"')
def step_impl(context, option):
    page.select_sort_option(option)  # Vai falhar - ESPERADO!
```

**Se você está escrevendo código que não falha em um teste existente, PARE.**

---

## Development Process Checklist

Antes de implementar QUALQUER funcionalidade:

- [ ] Feature Gherkin escrita?
- [ ] Steps definitions escritos?
- [ ] `behave` executado e FALHOU? (RED)
- [ ] Erro documentado/entendido?
- [ ] Implementação mínima feita?
- [ ] `behave` executado e PASSOU? (GREEN)
- [ ] Código refatorado? (REFACTOR)
- [ ] Unit tests adicionados?
- [ ] Testes executados 100% passing?

---

## Selenium Best Practices (MANDATÓRIO)

### Waits Strategy

```python
# ✅ CORRETO: Interações
self.wait.until(EC.element_to_be_clickable(locator)).click()

# ✅ CORRETO: Ler texto/verificar presença
element = self.wait.until(EC.visibility_of_element_located(locator))
text = element.text

# ❌ PROIBIDO: Interações com presence_of
element = self.wait.until(EC.presence_of_element_located(locator))
element.click()  # Pode falhar se não estiver clickable!

# ❌ PROIBIDO: Sleep fixo
time.sleep(5)  # NÃO-DETERMINÍSTICO
```

---

## Code Organization

### Import Rules
```python
# ✅ CORRETO: Imports no topo do arquivo
from selenium.webdriver.support.select import Select

class Page:
    def method(self):
        select = Select(element)  # OK

# ❌ ERRADO: Import dentro de método
class Page:
    def method(self):
        from selenium.webdriver.support.select import Select  # DIFICULTA MOCKING
        select = Select(element)
```

---

## Testing Hierarchy

1. **E2E (Behave)**: Fluxos completos de usuário
2. **Integration**: Page Objects com driver real
3. **Unit**: Lógica isolada, mocks para dependencies

**Regra**: Unit tests são escritos DEPOIS (fase REFACTOR), não antes.

---

## Code Style
- Follow community conventions (Behave: features/, steps/)
- English names for all code
- Type hints when improving clarity
- Use linters: pylint, flake8, black
- Code should be self-documenting with docstrings
- Follow Zen of Python principles

---

## Language & Communication
- Sempre comunicar em **Português (Brasil)**
- Explicar **WHY**, não apenas WHAT
- Opiniões fundamentadas, não apenas concordância

---

## Dependencies & Security
- Use Poetry for dependency management
- Never commit credentials or sensitive data
- Keep config separate from code
- Consult official documentation before solving problems

---

## Git Workflow
- **Conventional Commits**: `feat:`, `fix:`, `refactor:`, `test:`
- Commits atômicos (uma mudança lógica por commit)
- Atualizar README.md ao final da sessão

---

## Core Principles (Zen of Python)
- Explicit is better than implicit
- Simple is better than complex
- Practicality beats purity
- **Readability counts**
- Errors should never pass silently
- In the face of ambiguity, refuse the temptation to guess
