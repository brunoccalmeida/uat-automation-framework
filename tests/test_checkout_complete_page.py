"""Unit tests for CheckoutCompletePage class.

Only the navigation wait contract. The container, the confirmation reads and
the Back Home button are covered against the DOM by
tests/integration/test_checkout_complete_integration.py and
test_navigation_integration.py (#143, #170).
"""

from unittest.mock import Mock

from pages.checkout_complete_page import CheckoutCompletePage
from tests.helpers.navigation_contract import assert_clicks_then_returns_loaded


class TestClickBackHome:
    """Test click_back_home method."""

    def test_click_back_home_clicks_and_returns_loaded_inventory_page(self):
        """click_back_home clicks the button, returns a loaded InventoryPage."""
        page = CheckoutCompletePage(Mock())

        assert_clicks_then_returns_loaded(
            page,
            page.click_back_home,
            CheckoutCompletePage.BACK_HOME_BUTTON,
            "pages.inventory_page.InventoryPage",
        )
