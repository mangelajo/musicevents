import os
import pytest
from playwright.sync_api import sync_playwright, Browser

# Allow Django to run in async context for tests
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }

@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {
        "headless": True,
        "args": ["--no-sandbox"],
    }

@pytest.fixture(scope="session")
def browser() -> Browser:
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox"]
    )
    yield browser
    browser.close()
    playwright.stop()

@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

@pytest.fixture(scope="function")
def live_server_url(live_server):
    return live_server.url