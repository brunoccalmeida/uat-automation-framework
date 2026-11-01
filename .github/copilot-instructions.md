# UAT Automation Framework - Coding Guidelines

## ⚠️ REGRA DE OURO: TDD É OBRIGATÓRIO
**NUNCA implemente código de produção sem antes ter um teste falhando.**

## ⚠️ REGRA: MELHORES PRÁTICAS SEMPRE
**Toda decisão (código, testes, CI, ambiente, processo) segue as melhores práticas reconhecidas da indústria.**

- Havendo mais de um caminho, recomende o indicado pelas melhores práticas e cite o princípio que o sustenta (ex.: dev/prod parity, YAGNI, fail fast).
- Não escolha atalhos por conveniência (ex.: contornar um problema de ambiente com código novo).
- Desvios só com justificativa explícita, registrada no commit ou na documentação.

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

## ⚠️ REGRA: ESPERE O ESTADO FICAR PRONTO ANTES DE AGIR
**Toda ação seguida de uma leitura ou decisão deve esperar o resultado da ação, nunca um estado intermediário.**

Vale para código de teste, scripts e automação de CI. Antes de ler ou decidir, pergunte: *"isto vê o resultado da ação, ou um estado que ainda está mudando?"*

| Contexto | Estado intermediário (armadilha) | Como esperar corretamente |
|---|---|---|
| Selenium em SPA | A URL muda antes de a nova página renderizar | Navegação retorna só após o `PAGE_LOADED` do destino (`wait_until_loaded`) |
| Formulário com erro | Mensagem de erro antiga ainda na tela parece o resultado do novo envio | Remover o estado antigo antes de agir (`submit_and_wait_for_outcome`) |
| API do GitHub | `mergeStateStatus` = `UNKNOWN` logo após um merge no `master` | Aguardar até o estado deixar de ser `UNKNOWN` antes de decidir |
| Checks de CI | Logo após atualizar a branch, os checks verdes ainda são do commit anterior | Consultar os checks pelo SHA da head atual |

- **"Ainda não sei" não é "sim".** Estados como `UNKNOWN`, pendente ou resposta vazia significam *esperar*, nunca *seguir*.
- **Quando o estado final pode ser igual ao inicial**, não há como saber se a ação ocorreu: altere o estado inicial antes de agir (ex.: fechar o erro antigo antes de reenviar).
- **Espere por condição, nunca por tempo fixo** (`sleep`). Em polling, o intervalo é só o ritmo da checagem; a saída do laço é sempre a condição.

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

## 🔍 Error Diagnosis & Debugging (MANDATÓRIO)

**NUNCA "chute" soluções ao encontrar erros. Siga o processo sistemático:**

### Fluxo de Diagnóstico Profissional

```
┌──────────────────────────────────────────┐
│ 1. OBSERVE: Leia a mensagem de erro      │
│    ✓ Stack trace completo                │
│    ✓ Linha do erro                        │
│    ✓ Tipo da exception                    │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 2. CONTEXTUALIZE: Entenda o ambiente     │
│    ✓ Leia o código ao redor (±10 linhas) │
│    ✓ Identifique dependências            │
│    ✓ Verifique padrões no projeto        │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 3. INVESTIGUE: Busque padrões similares  │
│    ✓ grep_search por patterns            │
│    ✓ Leia arquivos relacionados          │
│    ✓ Compare com código funcionando      │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 4. DIAGNOSTIQUE: Identifique causa raiz  │
│    ✓ É um bug ou design problem?         │
│    ✓ Qual o padrão esperado?             │
│    ✓ Há outros locais com mesmo issue?   │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 5. PLANEJE: Solução consistente          │
│    ✓ Fix único ou refactor sistêmico?    │
│    ✓ Impacto em outros componentes?      │
│    ✓ Testes precisam ser ajustados?      │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 6. IMPLEMENTE: Aplique a solução         │
│    ✓ Multi-replace quando múltiplos      │
│    ✓ Mantenha consistência               │
│    ✓ Documente decisão se não óbvio      │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 7. VALIDE: Execute testes                │
│    ✓ Erro foi resolvido?                 │
│    ✓ Nenhuma regressão?                  │
│    ✓ Edge cases cobertos?                │
└──────────────────────────────────────────┘
```

### ❌ ANTI-PATTERNS de Debugging:

```python
# ❌ ERRADO: "Quick fix" sem investigação
# Erro: AttributeError: 'Context' object has no attribute 'cart_page'
# Solução RUIM: Apenas adicionar context.cart_page = CartPage() no step
def step_impl(context):
    context.cart_page = CartPage(context.driver)  # Fix pontual sem entender padrão

# ✅ CORRETO: Investigar padrão do projeto primeiro
# 1. grep_search: como outros steps criam pages?
# 2. Descobrir: alguns criam instância local, outros usam context
# 3. Decisão: padronizar TODOS para instância local (mais testável)
# 4. multi_replace: aplicar em todos os steps afetados
def step_impl(context):
    page = CartPage(context.driver)  # Consistente com padrão do projeto
    page.do_something()
```

```python
# ❌ ERRADO: Corrigir erro por erro sem ver padrão
# ImportError: cannot import name 'Select'
# Fix 1: Adiciona import no método
# Fix 2: Outra ImportError em outro arquivo
# Fix 3: Repete processo...

# ✅ CORRETO: Diagnosticar causa raiz antes de agir
# 1. read_file: verificar todos os imports no topo
# 2. grep_search: buscar padrão de imports no projeto
# 3. Verificar: Select deve ser importado no topo ou inline?
# 4. Decisão baseada em padrão existente + melhores práticas
# 5. Aplicar consistentemente
```

### Checklist de Diagnóstico

Antes de propor uma solução:

- [ ] Li a mensagem de erro COMPLETA (não apenas a última linha)?
- [ ] Entendi o contexto (±10 linhas ao redor do erro)?
- [ ] Busquei padrões similares no código (grep_search)?
- [ ] Identifiquei a causa raiz (não apenas o sintoma)?
- [ ] Verifiquei se há outros locais com mesmo problema?
- [ ] Planejei solução consistente com arquitetura do projeto?
- [ ] Considerei impacto em testes existentes?

### Comunicação de Diagnóstico

Ao reportar um erro ao usuário:

```markdown
## 🔴 Diagnóstico do Erro

**Erro Observado:**
[Stack trace ou mensagem]

**Causa Raiz:**
[Explicação técnica do PORQUÊ ocorreu]

**Análise:**
- Investigação: [O que foi verificado]
- Padrão identificado: [Consistência no código]
- Impacto: [Outros locais afetados]

**Solução Proposta:**
[Estratégia de correção com justificativa]

**Prevenção:**
[Como evitar recorrência]
```

---

## Language & Communication
- Sempre comunicar em **Português (Brasil)**
- Explicar **WHY**, não apenas WHAT
- Opiniões fundamentadas, não apenas concordância
- **Diagnósticos profissionais, não "chutes"**

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

### Pull Requests e Merge (limite de trabalho em andamento)
O `master` é protegido (ruleset): só aceita PR com os checks obrigatórios verdes e **branch atualizada**. Por isso cada merge desatualiza todos os outros PRs abertos, custando um novo ciclo de CI e revisão para cada um.

- **Um PR aberto por vez.** Trabalho pronto espera em commit local até a fila esvaziar; só então abra o próximo PR.
- **Merge antes do próximo PR**, não PRs empilhados. Empilhar só se justifica quando a revisão demora (equipes), não em fluxo solo.
- **Dependabot agrupado:** GitHub Actions e Python minor/patch em um PR cada; só versões maiores do Python ficam isoladas, uma por PR.
- **Merge só com checks verdes no commit mais recente do PR** (SHA da head). Branch atrás do `master`: atualizar e esperar o CI de novo.
- **Nunca usar `--admin`** para furar o ruleset. Se a regra atrapalha, discuta a regra, não a contorne.
- **Squash merge**, mantendo o histórico do `master` linear.
- Automação de merge segue lista de permissão: só faz o merge se **cada** check obrigatório estiver explicitamente aprovado; qualquer outro estado (falha, pendente, resposta vazia) interrompe.

---

## Core Principles (Zen of Python)
- Explicit is better than implicit
- Simple is better than complex
- Practicality beats purity
- **Readability counts**
- Errors should never pass silently
- In the face of ambiguity, refuse the temptation to guess
