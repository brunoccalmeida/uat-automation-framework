# Session Notes - UAT Automation Framework
**Data:** 13/12/2025

## 🎯 Objetivo do Projeto
Criar framework de automação UAT com Python + Behave + Selenium para:
- Portfólio profissional
- Transição CLT → Freelancer (12 meses)
- Demonstrar expertise em testes bancários

## 📋 Decisões Técnicas

### Aplicação Alvo
- **Parabank** (https://parabank.parasoft.com/)
- Sistema bancário demo com Web UI + REST API + SOAP
- **Estratégia Dual:** Web público + Docker local (resiliência)
- Repositório oficial: https://github.com/parasoft/parabank
- Dockerfile disponível para execução local

### Stack Tecnológica
- **Python 3.14.2** (instalado)
- **Poetry** para gestão de dependências
- **Behave** para BDD
- **Selenium** para testes Web
- **Requests/httpx** para testes API
- **Allure** para reports
- **Docker** para Parabank local (a instalar)

### Estrutura de Configuração
```yaml
environments:
  remote:
    base_url: "https://parabank.parasoft.com"
    active: true
  local:
    base_url: "http://localhost:8080/parabank"
    docker_image: "parasoft/parabank"
    active: false
```

## 🛠️ Status de Instalação

### ✅ Instalado
- Python 3.14.2
- Pip 25.3
- Git 2.52.0 (PATH configurado, requer restart do VS Code)

### ❌ Pendente
- Poetry (próximo passo)
- Docker Desktop
- Dependências do projeto (Behave, Selenium, etc)

## 📝 Diretrizes de Desenvolvimento
**Arquivo:** `.copilot-instructions.md`

### Principais Regras
1. **Zen do Python** como filosofia
2. **TDD** para código de produção (flexível para protótipos)
3. **NUNCA** criar/alterar/deletar código sem autorização expressa
4. Verificar estado antes de agir - NUNCA presumir
5. Testar sempre após mudanças
6. Código em **inglês**, comunicação em **português BR**
7. Não ser "yes man" - opiniões fundamentadas
8. Isolamento de testes pode prevalecer sobre DRY

### Ferramentas
- Linters: pylint, flake8, black
- Type hints quando apropriado
- Page Objects para Web
- Conventional Commits (sem prolixidade)
- README atualizado ao final de cada sessão

## 📦 Estrutura Planejada

```
uat-automation-framework/
├── .copilot-instructions.md  ✅ Criado
├── README.md                 ⏳ Pendente
├── pyproject.toml            ⏳ Pendente (Poetry)
├── docker-compose.yml        ⏳ Pendente
├── features/                 ⏳ Behave features
│   └── steps/
├── pages/                    ⏳ Page Objects
├── core/                     ⏳ Framework core
│   ├── config/
│   ├── drivers/
│   └── utils/
├── tests/                    ⏳ Testes unitários
└── reports/                  ⏳ Allure reports
```

## 🔧 Problema Técnico Atual
**Git PATH:** Instalado mas VS Code não reconhece (precisa restart completo)

**Workaround temporário:**
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

## 🎯 Próximos Passos (Ordem)
1. [ ] Reiniciar VS Code (Git no PATH)
2. [ ] Instalar Poetry
3. [ ] Inicializar Git no projeto (`git init`)
4. [ ] Criar estrutura de pastas
5. [ ] Configurar pyproject.toml com dependências
6. [ ] Instalar dependências via Poetry
7. [ ] Criar primeiro teste (TDD)
8. [ ] Configurar Docker Compose para Parabank

## 📊 Contexto Profissional
- Especialista em Automation e UAT
- Experiência: Python, Selenium, Behave, Allure
- Domínio: Sistemas bancários críticos e regulados
- Inglês fluente
- Restrições: Manter neutralidade LinkedIn, evitar conflito de interesse

## 🔍 Histórico Parabank
- **06/11/2025:** Aviso de manutenção
- **13/11/2025:** Offline para upgrade "ParaBank 2.0"
- **13/12/2025:** Reaberto (hoje)
- Motivo: Upgrade planejado, não instabilidade
- Risco: Recém reaberto, sem histórico de estabilidade pós-upgrade
- Solução: Docker local como fallback

## 💡 Decisões de Design
- Testes agnósticos de ambiente (funcionam em qualquer base URL)
- Setup automático: tenta remote, fallback para local
- Demonstra pensamento estratégico e resiliência
- CI/CD ready (containers determinísticos)

---
**Nota:** Este arquivo deve ser atualizado conforme projeto evolui
