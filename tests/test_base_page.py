"""Unit tests for BasePage class.

Tests the fundamental Page Object functionality without requiring a browser.
Uses mocks to isolate the logic from Selenium WebDriver.
"""

import ast
from pathlib import Path
from unittest.mock import Mock, call, patch

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class TestBasePageInitialization:
    """Test BasePage initialization and setup."""

    def test_base_page_stores_driver(self):
        """BasePage should store the WebDriver instance."""
        mock_driver = Mock()
        page = BasePage(mock_driver)

        assert page.driver is mock_driver

    def test_base_page_creates_wait_with_default_timeout(self):
        """BasePage should wait on its driver with a 10s timeout by default."""
        mock_driver = Mock()
        with patch("pages.base_page.WebDriverWait") as mock_wait:
            BasePage(mock_driver)

        mock_wait.assert_called_once_with(mock_driver, 10)

    def test_base_page_stores_the_wait(self):
        """BasePage should expose the WebDriverWait it created."""
        with patch("pages.base_page.WebDriverWait") as mock_wait:
            page = BasePage(Mock())

        assert page.wait is mock_wait.return_value


class TestFindElement:
    """Test find_element method."""

    def test_find_element_uses_explicit_wait(self):
        """find_element should use WebDriverWait to locate element."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element

        page = BasePage(mock_driver)
        page.wait = mock_wait

        locator = (By.ID, "test-id")
        result = page.find_element(locator)

        assert result is mock_element
        mock_wait.until.assert_called_once()

    def test_find_element_uses_visibility_condition(self):
        """find_element should wait for element to be visible."""
        mock_driver = Mock()
        page = BasePage(mock_driver)

        locator = (By.ID, "test-id")
        page.wait = Mock()

        with patch("pages.base_page.EC") as mock_ec:
            page.find_element(locator)

            mock_ec.visibility_of_element_located.assert_called_once_with(locator)
            page.wait.until.assert_called_once_with(
                mock_ec.visibility_of_element_located.return_value,
                message="('id', 'test-id') did not become visible",
            )


class TestFindClickableElement:
    """Test find_clickable_element method."""

    def test_find_clickable_element_uses_explicit_wait(self):
        """find_clickable_element should use WebDriverWait."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element

        page = BasePage(mock_driver)
        page.wait = mock_wait

        locator = (By.ID, "button-id")
        result = page.find_clickable_element(locator)

        assert result is mock_element
        mock_wait.until.assert_called_once()

    def test_find_clickable_element_names_locator_and_condition_on_timeout(self):
        """A timeout must say what was awaited, not raise an empty message."""
        page = BasePage(Mock())
        page.wait = Mock()
        locator = (By.ID, "button-id")

        with patch("pages.base_page.EC") as mock_ec:
            page.find_clickable_element(locator)

            mock_ec.element_to_be_clickable.assert_called_once_with(locator)
            page.wait.until.assert_called_once_with(
                mock_ec.element_to_be_clickable.return_value,
                message="('id', 'button-id') did not become clickable",
            )


class TestTypeMethod:
    """Test type method (text input)."""

    def test_type_finds_clickable_element(self):
        """type should find element using find_clickable_element."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(
            page, "find_clickable_element", return_value=mock_element
        ) as mock_find:
            with patch.object(page.driver, "execute_script"):
                with patch.object(page.wait, "until", return_value=mock_element):
                    locator = (By.ID, "input-field")
                    page.type(locator, "test text")

                    mock_find.assert_called_once_with(locator)

    def test_type_scrolls_element_into_view(self):
        """type should scroll element to center of viewport."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(page, "find_clickable_element", return_value=mock_element):
            with patch.object(page.driver, "execute_script") as mock_execute:
                with patch.object(page.wait, "until", return_value=mock_element):
                    locator = (By.ID, "input-field")
                    page.type(locator, "test text")

                    mock_execute.assert_called_once_with(
                        "arguments[0].scrollIntoView({block: 'center'});", mock_element
                    )

    def test_type_re_verifies_element_clickable_after_scroll(self):
        """type should verify element is still clickable after scrolling."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(page, "find_clickable_element", return_value=mock_element):
            with patch.object(page.driver, "execute_script"):
                with patch.object(
                    page.wait, "until", return_value=mock_element
                ) as mock_wait:
                    locator = (By.ID, "input-field")
                    page.type(locator, "test text")

                    # Should be called once for re-verification
                    mock_wait.assert_called_once()
                    assert mock_wait.call_args.kwargs["message"] == (
                        "('id', 'input-field') did not stay clickable after scrolling"
                    )

    def test_type_clears_field_before_typing(self):
        """type should clear existing text before typing new text."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(page, "find_clickable_element", return_value=mock_element):
            with patch.object(page.driver, "execute_script"):
                with patch.object(page.wait, "until", return_value=mock_element):
                    locator = (By.ID, "input-field")
                    page.type(locator, "test text")

                    mock_element.clear.assert_called_once()

    def test_type_sends_text_to_element(self):
        """type should send keys to the element."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(page, "find_clickable_element", return_value=mock_element):
            with patch.object(page.driver, "execute_script"):
                with patch.object(page.wait, "until", return_value=mock_element):
                    locator = (By.ID, "input-field")
                    test_text = "my test input"
                    page.type(locator, test_text)

                    mock_element.send_keys.assert_called_once_with(test_text)

    def test_type_method_sequence_is_correct(self):
        """type should execute operations in correct order."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(page, "find_clickable_element", return_value=mock_element):
            with patch.object(page.driver, "execute_script"):
                with patch.object(page.wait, "until", return_value=mock_element):
                    locator = (By.ID, "input-field")
                    page.type(locator, "text")

                    # Verify key methods were called
                    assert mock_element.clear.called
                    assert mock_element.send_keys.called


class TestClickMethod:
    """Test click method."""

    def test_click_finds_clickable_element(self):
        """click should find element using find_clickable_element."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(
            page, "find_clickable_element", return_value=mock_element
        ) as mock_find:
            locator = (By.ID, "button")
            page.click(locator)

            mock_find.assert_called_once_with(locator)

    def test_click_calls_element_click(self):
        """click should call click() on the element."""
        mock_driver = Mock()
        mock_element = Mock()

        page = BasePage(mock_driver)

        with patch.object(page, "find_clickable_element", return_value=mock_element):
            locator = (By.ID, "button")
            page.click(locator)

            mock_element.click.assert_called_once()


class TestGetTextMethod:
    """Test get_text method."""

    def test_get_text_finds_visible_element(self):
        """get_text should find element using find_element."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.text = "Sample text"

        page = BasePage(mock_driver)

        with patch.object(page, "find_element", return_value=mock_element) as mock_find:
            locator = (By.ID, "label")
            page.get_text(locator)

            mock_find.assert_called_once_with(locator)

    def test_get_text_returns_element_text(self):
        """get_text should return the text property of element."""
        mock_driver = Mock()
        mock_element = Mock()
        expected_text = "Expected text content"
        mock_element.text = expected_text

        page = BasePage(mock_driver)

        with patch.object(page, "find_element", return_value=mock_element):
            locator = (By.ID, "label")
            result = page.get_text(locator)

            assert result == expected_text


class TestIsElementVisibleMethod:
    """Test is_element_visible method."""

    def test_is_element_visible_returns_true_when_found(self):
        """is_element_visible should return True when element becomes visible."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = Mock()  # Element found

        page = BasePage(mock_driver)

        # Mock WebDriverWait creation for custom timeout
        with patch("pages.base_page.WebDriverWait", return_value=mock_wait):
            locator = (By.ID, "existing-element")
            result = page.is_element_visible(locator, timeout=3)

        assert result is True
        mock_wait.until.assert_called_once()

    def test_is_element_visible_uses_visibility_condition(self):
        """is_element_visible should wait for element to be visible."""
        mock_driver = Mock()
        mock_wait = Mock()

        page = BasePage(mock_driver)

        with (
            patch("pages.base_page.WebDriverWait", return_value=mock_wait),
            patch("pages.base_page.EC") as mock_ec,
        ):
            locator = (By.ID, "element")
            page.is_element_visible(locator, timeout=3)

            mock_ec.visibility_of_element_located.assert_called_once_with(locator)
            mock_wait.until.assert_called_once_with(
                mock_ec.visibility_of_element_located.return_value,
                message="('id', 'element') did not become visible",
            )

    def test_is_element_visible_returns_false_on_timeout(self):
        """is_element_visible should return False if element never becomes visible."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_wait.until.side_effect = TimeoutException("Not found")

        page = BasePage(mock_driver)

        with patch("pages.base_page.WebDriverWait", return_value=mock_wait):
            locator = (By.ID, "missing-element")
            result = page.is_element_visible(locator, timeout=3)

        assert result is False

    def test_is_element_visible_uses_custom_timeout(self):
        """is_element_visible should use provided custom timeout."""
        mock_driver = Mock()

        page = BasePage(mock_driver)

        with patch("pages.base_page.WebDriverWait") as mock_wait_class:
            locator = (By.ID, "element")
            custom_timeout = 5
            page.is_element_visible(locator, timeout=custom_timeout)

            # Verify WebDriverWait was created with custom timeout
            mock_wait_class.assert_called_with(mock_driver, custom_timeout)


class _LoadablePage(BasePage):
    """Minimal page with a PAGE_LOADED marker for testing."""

    PAGE_LOADED = (By.ID, "page-marker")


class TestWaitUntilLoaded:
    """Test wait_until_loaded method."""

    def test_wait_until_loaded_waits_for_page_marker_and_returns_self(self):
        """wait_until_loaded should wait for PAGE_LOADED and return the page."""
        page = _LoadablePage(Mock())
        page.wait = Mock()

        with patch("pages.base_page.EC") as mock_ec:
            result = page.wait_until_loaded()

            mock_ec.visibility_of_element_located.assert_called_once_with(
                _LoadablePage.PAGE_LOADED
            )
            page.wait.until.assert_called_once_with(
                mock_ec.visibility_of_element_located.return_value,
                message="_LoadablePage did not render",
            )
            assert result is page


class TestWaitUntilStable:
    """Test wait_until_stable method."""

    LOCATOR = (By.ID, "sliding")

    @staticmethod
    def _element_at(x):
        """Visible element mock whose bounding box starts at x."""
        element = Mock()
        element.rect = {"x": x, "y": 0, "width": 10, "height": 10}
        return element

    def _condition(self, page):
        """Run wait_until_stable and return the condition it waits on."""
        page.wait = Mock()
        page.wait_until_stable(self.LOCATOR)
        page.wait.until.assert_called_once()
        return page.wait.until.call_args.args[0]

    def test_waits_with_a_message_naming_the_locator(self):
        """The timeout message should say which element kept moving."""
        page = BasePage(Mock())
        page.wait = Mock()

        result = page.wait_until_stable(self.LOCATOR)

        assert page.wait.until.call_args.kwargs == {
            "message": f"{self.LOCATOR} did not stop moving"
        }
        assert result is page.wait.until.return_value

    def test_condition_is_met_only_once_the_box_repeats(self):
        """A moving element is not ready; one with the same box twice is."""
        page = BasePage(Mock())
        moving, still, again = (self._element_at(x) for x in (-210, 24, 24))

        with patch("pages.base_page.EC") as mock_ec:
            visible = mock_ec.visibility_of_element_located.return_value
            visible.side_effect = [moving, still, again]
            condition = self._condition(page)

            results = [condition(page.driver) for _ in range(3)]

        mock_ec.visibility_of_element_located.assert_called_with(self.LOCATOR)
        assert results == [False, False, again]

    def test_condition_is_not_met_while_the_element_is_hidden(self):
        """A hidden element is not ready, and no box is remembered for it."""
        page = BasePage(Mock())
        shown = self._element_at(24)

        with patch("pages.base_page.EC") as mock_ec:
            visible = mock_ec.visibility_of_element_located.return_value
            visible.side_effect = [shown, False, shown, shown]
            condition = self._condition(page)

            results = [condition(page.driver) for _ in range(4)]

        assert results == [False, False, False, shown]


class _FormPage(_LoadablePage):
    """Minimal form page with error locators for testing."""

    ERROR_MESSAGE = (By.ID, "form-error")
    ERROR_CLOSE_BUTTON = (By.ID, "form-error-close")
    SUBMIT_BUTTON = (By.ID, "submit")


class TestSubmitAndWaitForOutcome:
    """Test submit_and_wait_for_outcome method."""

    def test_submit_without_leftover_error_clicks_and_waits_for_either_outcome(
        self,
    ):
        """Without an error on screen, it should submit and wait for an outcome."""
        mock_driver = Mock()
        mock_driver.find_elements.return_value = []
        page = _FormPage(mock_driver)
        page.wait = Mock()

        with (
            patch.object(page, "click") as mock_click,
            patch("pages.base_page.EC") as mock_ec,
        ):
            page.submit_and_wait_for_outcome(_FormPage.SUBMIT_BUTTON, _LoadablePage)

            mock_click.assert_called_once_with(_FormPage.SUBMIT_BUTTON)
            mock_ec.visibility_of_element_located.assert_has_calls(
                [call(_LoadablePage.PAGE_LOADED), call(_FormPage.ERROR_MESSAGE)]
            )
            page.wait.until.assert_called_once_with(
                mock_ec.any_of.return_value,
                message="Neither _LoadablePage nor error message rendered",
            )

    def test_submit_dismisses_leftover_error_before_clicking(self):
        """A leftover error must be dismissed, and gone, before submitting."""
        mock_driver = Mock()
        mock_driver.find_elements.return_value = [Mock()]
        page = _FormPage(mock_driver)
        page.wait = Mock()
        calls = Mock()
        calls.attach_mock(page.wait.until, "wait_until")

        with (
            patch.object(page, "click") as mock_click,
            patch("pages.base_page.EC") as mock_ec,
        ):
            calls.attach_mock(mock_click, "click")
            page.submit_and_wait_for_outcome(_FormPage.SUBMIT_BUTTON, _LoadablePage)

            mock_ec.invisibility_of_element_located.assert_called_once_with(
                _FormPage.ERROR_MESSAGE
            )
            assert calls.mock_calls == [
                call.click(_FormPage.ERROR_CLOSE_BUTTON),
                call.wait_until(
                    mock_ec.invisibility_of_element_located.return_value,
                    message="('id', 'form-error') did not disappear",
                ),
                call.click(_FormPage.SUBMIT_BUTTON),
                call.wait_until(
                    mock_ec.any_of.return_value,
                    message="Neither _LoadablePage nor error message rendered",
                ),
            ]


class TestAcceptAlert:
    """Test accept_alert method."""

    def test_accept_alert_waits_for_the_alert(self):
        """accept_alert should wait until an alert is present."""
        page = BasePage(Mock())

        with (
            patch.object(page, "wait") as mock_wait,
            patch("pages.base_page.EC") as mock_ec,
        ):
            page.accept_alert()

        mock_wait.until.assert_called_once_with(
            mock_ec.alert_is_present.return_value, message="No alert opened"
        )

    def test_accept_alert_reads_the_text_before_accepting(self):
        """accept_alert should return the text, read before the alert closes."""
        page = BasePage(Mock())
        events = []
        alert = Mock()
        type(alert).text = property(lambda _: events.append("text") or "Broken!")
        alert.accept.side_effect = lambda: events.append("accept")

        with patch.object(page, "wait") as mock_wait:
            mock_wait.until.return_value = alert
            text = page.accept_alert()

        assert text == "Broken!"
        assert events == ["text", "accept"]


def test_every_wait_in_pages_names_what_it_awaited():
    """A wait without message= times out with an empty message (#109)."""
    unnamed = [
        f"{path.name}:{node.lineno}"
        for path in sorted((Path(__file__).parents[1] / "pages").glob("*.py"))
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "until"
        and not any(keyword.arg == "message" for keyword in node.keywords)
    ]

    assert not unnamed, f"wait.until without message=: {unnamed}"
