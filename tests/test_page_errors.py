"""Unit tests for watch_page_errors: the page's errors, via BiDi (#180, #183)."""

import json
from unittest.mock import Mock

from selenium.webdriver.common.bidi.log import ConsoleLogEntry, JavascriptLogEntry

from core.page_errors import watch_page_errors

# log.entryAdded payloads as the W3C WebDriver BiDi spec shapes them
CONSOLE_PARAMS = {
    "type": "console",
    "level": "error",
    "text": "early",
    "timestamp": 1,
    "method": "error",
    "args": [{"type": "string", "value": "early"}],
    "source": {"realm": "r1"},
}
JS_PARAMS = {
    "type": "javascript",
    "level": "error",
    "text": "Error: boom",
    "timestamp": 2,
    "source": {"realm": "r1"},
    "stackTrace": {
        "callFrames": [
            {"url": "app.js", "functionName": "", "lineNumber": 1, "columnNumber": 7}
        ]
    },
}


def test_records_console_messages_and_javascript_errors_as_dicts():
    """Both BiDi streams land in one list, ready for json.dumps."""
    driver = Mock()

    errors = watch_page_errors(driver)
    on_console = driver.script.add_console_message_handler.call_args.args[0]
    on_error = driver.script.add_javascript_error_handler.call_args.args[0]
    on_console(ConsoleLogEntry.from_json(CONSOLE_PARAMS))
    on_error(JavascriptLogEntry.from_json(JS_PARAMS))

    assert [(e["type_"], e["text"]) for e in errors] == [
        ("console", "early"),
        ("javascript", "Error: boom"),
    ]
    assert errors[1]["stacktrace"] == JS_PARAMS["stackTrace"]
    json.dumps(errors)
