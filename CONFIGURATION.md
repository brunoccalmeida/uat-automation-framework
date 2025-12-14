# Configuração do Framework

Referência rápida para configuração e execução do framework de testes UAT.

## 🎯 Modo Headless

O framework suporta execução em modo headless (sem interface gráfica do browser) através de três níveis de configuração com prioridade bem definida.

### Hierarquia de Configuração

**Ordem de Prioridade** (do maior para o menor):

1. **Parâmetro CLI** - Override imediato via linha de comando
2. **Variável de Ambiente** - Configuração do ambiente (ideal para CI/CD)
3. **Arquivo de Configuração** - Valor padrão do projeto (`config.yaml`)

### Exemplos de Uso

#### 1. Parâmetro CLI (Prioridade Máxima)

```bash
# Forçar execução headless
poetry run behave -Dheadless=true

# Forçar execução com browser visível
poetry run behave -Dheadless=false

# Aplicar em feature específica
poetry run behave features/login.feature -Dheadless=true
```

**Quando usar:**
- ✅ Desenvolvimento local quando quer mudar comportamento pontualmente
- ✅ Debug de testes (forçar browser visível)
- ✅ Testar comportamento headless antes do commit

#### 2. Variável de Ambiente (Prioridade Média)

**PowerShell (Windows):**
```powershell
# Temporário (apenas sessão atual)
$env:HEADLESS="true"
poetry run behave

# Permanente (usuário atual)
[System.Environment]::SetEnvironmentVariable('HEADLESS', 'true', 'User')
```

**Bash/Zsh (Linux/Mac):**
```bash
# Temporário
export HEADLESS=true
poetry run behave

# Inline (apenas para este comando)
HEADLESS=true poetry run behave

# Permanente (adicionar ao ~/.bashrc ou ~/.zshrc)
export HEADLESS=true
```

**Quando usar:**
- ✅ CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI)
- ✅ Ambientes de teste automatizado
- ✅ Containers Docker
- ✅ Execução em servidores sem interface gráfica

#### 3. Arquivo de Configuração (Prioridade Baixa)

Edite `config.yaml`:
```yaml
browser:
  name: chrome
  headless: false  # true ou false
  window_size: "1920,1080"
```

**Quando usar:**
- ✅ Configuração padrão do time
- ✅ Comportamento consistente do projeto
- ✅ Documentação do setup esperado

### Cenários Práticos

#### Desenvolvimento Local
```bash
# Browser visível (padrão do projeto)
poetry run behave

# Testar headless pontualmente
poetry run behave -Dheadless=true
```

#### CI/CD (GitHub Actions)
```yaml
# .github/workflows/tests.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        env:
          HEADLESS: true  # Variável de ambiente
        run: poetry run behave
```

#### Debug Específico
```bash
# Forçar browser visível mesmo com HEADLESS=true no ambiente
poetry run behave -Dheadless=false features/checkout.feature
```

### Validação da Configuração

Para verificar qual configuração está sendo aplicada, você pode:

1. **Observar o comportamento**: Browser abre = headless false, não abre = headless true
2. **Adicionar log temporário** em `features/environment.py`:
   ```python
   print(f"Headless mode: {browser_config['headless']}")
   ```

### Valores Aceitos

O framework aceita múltiplos formatos para flexibilidade:

**Valores True** (case-insensitive):
- `true`
- `True`
- `TRUE`
- `1`
- `yes`
- `Yes`

**Valores False**:
- `false`
- `False`
- `FALSE`
- `0`
- `no`
- Qualquer outro valor

## 🔧 Outras Configurações

### Window Size

Configurado apenas via `config.yaml`:
```yaml
browser:
  window_size: "1920,1080"  # largura,altura
```

### Browser Type

Atualmente suporta apenas Chrome. Configurado via `config.yaml`:
```yaml
browser:
  name: chrome
```

### Timeout Padrão

Configurado via `config.yaml`:
```yaml
browser:
  implicit_wait: 10  # segundos
  page_load_timeout: 30  # segundos
```

## 📚 Boas Práticas

### Para Desenvolvedores

1. **Desenvolvimento**: Deixe headless `false` no config.yaml
2. **Debug**: Use `-Dheadless=false` para forçar browser visível
3. **Pre-commit**: Teste com `-Dheadless=true` antes de fazer push
4. **Não commite** variáveis de ambiente locais

### Para CI/CD

1. **Use variável de ambiente** `HEADLESS=true`
2. **Não dependa** de CLI parameters em pipelines
3. **Configure timeout** adequado para headless (pode ser mais rápido)
4. **Salve screenshots** em caso de falha (mesmo em headless)

### Para o Time

1. **Documente** a configuração padrão esperada
2. **Comunique** mudanças no config.yaml via pull request
3. **Mantenha consistência** entre ambientes dev/staging/prod
4. **Revise** periodicamente se as configurações ainda fazem sentido

## 🆘 Troubleshooting

### Browser não abre mesmo com headless=false
```bash
# Verificar se há override via ENV
echo $HEADLESS  # Bash
echo $env:HEADLESS  # PowerShell

# Remover variável
unset HEADLESS  # Bash
Remove-Item Env:\HEADLESS  # PowerShell
```

### Testes falham apenas em headless
- Provavelmente problema de timing ou tamanho de janela
- Aumente window_size no config.yaml
- Verifique explicit waits nos Page Objects

### Chrome não encontrado no CI
```yaml
# GitHub Actions - instalar Chrome
- name: Install Chrome
  run: |
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install google-chrome-stable
```

## 📖 Referências

- [Behave User Data](https://behave.readthedocs.io/en/latest/api.html#behave.configuration.Configuration.userdata)
- [Selenium Headless Chrome](https://www.selenium.dev/documentation/webdriver/browsers/chrome/#headless)
- [12-Factor App - Config](https://12factor.net/config)
- [GitHub Actions Environment Variables](https://docs.github.com/en/actions/learn-github-actions/variables)
