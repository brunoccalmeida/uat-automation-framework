"""Page Object models.

Navigation methods return the destination page object once it has rendered
(see BasePage.wait_until_loaded). The exception is form submits that may fail
validation (login, checkout continue): their destination depends on the data,
so they wait for either outcome and return None (see
BasePage.submit_and_wait_for_outcome). Navigation is cyclic (e.g. cart <-> checkout),
so page modules import each other as modules (``from pages import cart_page``)
and resolve classes at call time. This is intentional: pylint's cyclic-import
(R0401) warning for this package is expected. Never use ``from pages.x import
X`` between page modules, as it breaks depending on import order.

For the same reason the pages shown after login include the header
(``header_component.HeaderComponent``) in their own ``__init__`` instead of
inheriting it from a shared base: a base that imports the header, which
imports the pages, which subclass the base, is a cycle that fails at class
definition time.
"""
