---
paths:
  - "pages/**/*.py"
  - "features/**/*.py"
  - "tests/**/*.py"
---
<!-- LTeX: language=pt-BR -->
# Selenium e Page Objects

- Interação: `self.wait.until(EC.element_to_be_clickable(locator)).click()`.
- Ler texto ou verificar presença: `self.wait.until(EC.visibility_of_element_located(locator))`.
- Proibido: interagir com elemento obtido por `presence_of_element_located` (pode não estar clicável) e `time.sleep` (não determinístico).
- Navegação em SPA retorna só após o `PAGE_LOADED` do destino (`wait_until_loaded`): a URL muda antes de a página renderizar.
- Formulário com erro: remova o erro antigo antes de reenviar (`submit_and_wait_for_outcome`), senão o erro velho parece o resultado novo.
- Steps usam page objects em variável local (`page = CartPage(context.driver)`), não em atributos de `context`.
