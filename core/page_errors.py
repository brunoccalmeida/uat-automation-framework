"""The page's console messages and JavaScript errors, heard over BiDi (#180).

A blank page has two leading causes: the app bundle never loaded, or a
script threw before rendering. The screenshot cannot tell them apart; the
errors the page threw can. Every session opens WebDriver BiDi (DriverManager
enables it), so listening costs nothing.

Both test layers record them: the integration driver fixture saves them to
<test>.console.json, the Behave hooks attach them to the Allure result
(#183). Hence this module lives in core, which both layers import, and not in
tests/helpers, which pulls in pytest.
"""

from dataclasses import asdict


def watch_page_errors(driver) -> list[dict]:
    """Record the page's console messages and JavaScript errors from now on.

    Needs a session with WebDriver BiDi (DriverManager enables it). Call it
    before the first navigation: an app bundle that throws does so while
    driver.get loads the page.

    Args:
        driver: WebDriver whose pages to listen to.

    Returns:
        The list the BiDi handlers fill, one dict per log entry (text, level,
        timestamp and, for JavaScript errors, the stack trace).
    """
    entries: list[dict] = []
    driver.script.add_console_message_handler(lambda e: entries.append(asdict(e)))
    driver.script.add_javascript_error_handler(lambda e: entries.append(asdict(e)))
    return entries
