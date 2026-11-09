<!-- LTeX: language=pt-BR -->
# Configuração do Framework

Referência rápida para configuração e execução do framework de testes UAT.

## ⚙️ Variáveis de ambiente

As configurações vêm do ambiente (Twelve-Factor App, fator III) e são validadas uma única vez, na largada, por `Settings` em `core/config.py`. Variável ausente ou inválida interrompe a execução antes de abrir o navegador, com um erro que a nomeia e nunca mostra o valor (*fail fast*).

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `BASE_URL` | Sim | | URL http(s) da aplicação sob teste |
| `TEST_USER_PASSWORD` | Sim | | Senha comum aos usuários de teste |
| `BROWSER` | Não | `chrome` | `chrome` ou `firefox` |
| `HEADLESS` | Não | `true` | Execução sem interface gráfica |
| `WINDOW_SIZE` | Não | `1920,1080` | Largura e altura da janela |
| `SELENIUM_REMOTE_URL` | Não | | URL do Selenium Grid; vazia usa navegador local |

**Na sua máquina:** copie `.env.example` para `.env` (ignorado pelo Git) uma vez e preencha a senha, que na Sauce Demo é pública e aparece na tela de login. Valor vazio conta como ausente.

**No CI:** os valores ficam no bloco `env` de `.github/workflows/tests.yml`. Ali a senha é literal de propósito: é pública, e PRs do Dependabot ou de forks não recebem segredos do Actions. Para uma aplicação real, mova a senha para o `env` dos jobs que abrem navegador, como `${{ secrets.TEST_USER_PASSWORD }}` (no bloco do workflow, ela chegaria a todos os jobs, inclusive os que rodam ferramentas de terceiros); execuções do Dependabot precisam do segredo cadastrado também em "Dependabot secrets".

## 🎯 Modo Headless

O framework suporta execução em modo headless (sem interface gráfica do browser) através de quatro níveis de configuração com prioridade bem definida.

### Hierarquia de Configuração

**Ordem de Prioridade** (do maior para o menor):

1. **Parâmetro CLI** - Override imediato via linha de comando
2. **Variável de Ambiente** - Configuração do ambiente (ideal para CI/CD)
3. **Arquivo `.env`** - Valores da sua máquina (ignorado pelo Git)
4. **Padrão** - Definido em `Settings` (`core/config.py`)

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

#### 3. Arquivo `.env` (Prioridade Baixa)

Edite seu `.env`:
```bash
HEADLESS=false
```

**Quando usar:**
- ✅ Preferências da sua máquina, sem repetir a variável em cada comando

### Cenários Práticos

#### Desenvolvimento Local
```bash
# Headless (padrão do projeto)
poetry run behave

# Browser visível pontualmente
poetry run behave -Dheadless=false
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
   print(context.settings)  # a senha aparece mascarada
   ```

### Valores Aceitos

Sem diferenciar maiúsculas de minúsculas:

- **Verdadeiro:** `true`, `1`, `yes`, `y`, `on`, `t`
- **Falso:** `false`, `0`, `no`, `n`, `off`, `f`

Qualquer outro valor interrompe a execução com erro, em vez de virar `false` em silêncio.

## 🔧 Outras Configurações

### Window Size

Configurado pela variável `WINDOW_SIZE` (largura,altura; padrão `1920,1080`).

### Browser Type

O framework suporta **Chrome** e **Firefox**. A configuração segue a mesma hierarquia (CLI > ENV > `.env` > padrão).

#### Hierarquia de Configuração (Browser)

**Ordem de Prioridade** (do maior para o menor):

1. **Parâmetro CLI**: `-Dbrowser=firefox`
2. **Variável de Ambiente**: `BROWSER=firefox`
3. **Arquivo `.env`**: `BROWSER=firefox`
4. **Padrão**: `chrome`

A mesma hierarquia vale para os testes de integração (pytest), exceto o CLI, que não existe no pytest: `BROWSER=firefox poetry run pytest tests/integration/`. Contra o Grid do Firefox, suba `docker compose up --wait firefox` e use `SELENIUM_REMOTE_URL=http://localhost:4445`. O CI roda as integrações no Chrome (job `test`) e no Firefox (job `integration-matrix`).

#### Exemplos de Uso

**CLI (Prioridade máxima):**
```bash
# Forçar Firefox
poetry run behave -Dbrowser=firefox

# Forçar Chrome
poetry run behave -Dbrowser=chrome
```

**Variável de ambiente (Prioridade média):**

PowerShell (Windows):
```powershell
$env:BROWSER="firefox"
poetry run behave
```

Bash/Zsh (Linux/Mac):
```bash
export BROWSER=firefox
poetry run behave
```

**Arquivo `.env` (Prioridade baixa):**
```bash
BROWSER=firefox
```

### Selenium Grid (navegador remoto)

Com uma URL de Selenium Grid configurada, a sessão abre no Grid (`webdriver.Remote`) com as **mesmas options** do navegador local; sem URL, o navegador é local (padrão). O CI usa o Grid do [compose.yaml](compose.yaml) (docker-selenium), e rodar localmente contra ele dá o mesmo build de navegador do CI (paridade dev/prod, #116). Passo a passo no README, seção "Same browser as CI".

**Ordem de Prioridade** (do maior para o menor; valor vazio conta como ausente):

1. **Parâmetro CLI** (Behave): `-Dremote_url=http://localhost:4444`
2. **Variável de Ambiente**: `SELENIUM_REMOTE_URL=http://localhost:4444` (vale também para os testes de integração)
3. **Arquivo `.env`**: `SELENIUM_REMOTE_URL=http://localhost:4444`
4. **Padrão**: nenhuma URL (navegador local)

| Serviço do `compose.yaml` | URL |
|---|---|
| `chrome` | `http://localhost:4444` |
| `firefox` | `http://localhost:4445` |

### Esperas (timeouts)

Não há variável de timeout. Os Page Objects usam só esperas explícitas (`WebDriverWait`, padrão de 10 s em `BasePage`), e o projeto não usa *implicit wait*, de propósito: a documentação do Selenium avisa para não misturar os dois tipos ("Do not mix implicit and explicit waits"), porque a combinação gera tempos de espera imprevisíveis.

### Credenciais dos usuários de teste

A senha comum aos usuários da Sauce Demo vem da variável `TEST_USER_PASSWORD` e é lida como `SecretStr`, que a mascara em logs e relatórios (o valor só sai com `get_secret_value()`). Os cenários dizem só quem entra (`When I log in as "standard_user"`); senha literal no cenário, apenas quando ela é o dado sob teste (ex.: `login_negative.feature`). `tests/test_config.py` barra a senha literal em código (`.py` e `.feature`).

## 📚 Boas Práticas

### Para Desenvolvedores

1. **Desenvolvimento**: Use `HEADLESS=false` no seu `.env` se preferir ver o browser
2. **Debug**: Use `-Dheadless=false` para forçar browser visível
3. **Pre-commit**: Teste com `-Dheadless=true` antes de fazer push
4. **Não commite** variáveis de ambiente locais

### Para CI/CD

1. **Use variável de ambiente** `HEADLESS=true`
2. **Não dependa** de CLI parameters em pipelines
3. **Salve screenshots** em caso de falha (mesmo em headless)

### Para o Time

1. **Documente** a configuração padrão esperada
2. **Comunique** variáveis novas atualizando o `.env.example` via pull request
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
- Aumente `WINDOW_SIZE`
- Verifique explicit waits nos Page Objects

### Grid não responde ou sessão não abre
```bash
docker compose ps                      # o serviço deve estar "(healthy)"
curl -s http://localhost:4444/status   # "ready": true quando aceita sessões
docker compose logs chrome             # erro do Grid ou do navegador
```
`Connection refused` em `localhost:4444`: o Grid não está de pé (`docker compose up --wait chrome`). Sessões que demoram a abrir com `pytest -n auto`: o Grid tem menos sessões que workers; suba com `SE_NODE_MAX_SESSIONS` igual ao número de CPUs. No CI, o step "Show Selenium Grid logs on failure" imprime esses logs quando algo falha.

## 📖 Referências

- [Behave User Data](https://behave.readthedocs.io/en/latest/api.html#behave.configuration.Configuration.userdata)
- [Selenium Headless Chrome](https://www.selenium.dev/documentation/webdriver/browsers/chrome/#headless)
- [12-Factor App - Config](https://12factor.net/config)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [docker-selenium](https://github.com/SeleniumHQ/docker-selenium)
- [12-Factor App - Dev/prod parity](https://12factor.net/dev-prod-parity)
- [GitHub Actions Environment Variables](https://docs.github.com/en/actions/learn-github-actions/variables)
