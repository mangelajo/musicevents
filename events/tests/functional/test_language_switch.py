import pytest
from playwright.sync_api import expect, Page

def test_language_switch_maintains_page(page: Page, live_server_url: str):
    # Start with the home page in English
    page.goto(f"{live_server_url}/")
    
    # Accept cookies to ensure navigation works
    page.click("button.btn-accept")
    
    # Verify initial English content
    expect(page.locator("a.nav-link", has_text="Events")).to_be_visible()
    expect(page.locator("a.nav-link", has_text="Artists")).to_be_visible()
    expect(page.locator("a.nav-link", has_text="Venues")).to_be_visible()
    
    # Switch to Spanish
    with page.expect_navigation():
        page.select_option("select[name='language']", "es")
    
    # Verify Spanish content
    expect(page.locator("a.nav-link", has_text="Eventos")).to_be_visible()
    expect(page.locator("a.nav-link", has_text="Artistas")).to_be_visible()
    expect(page.locator("a.nav-link", has_text="Locales")).to_be_visible()
    
    # Switch back to English
    with page.expect_navigation():
        page.select_option("select[name='language']", "en")
    
    # Verify English content again
    expect(page.locator("a.nav-link", has_text="Events")).to_be_visible()
    expect(page.locator("a.nav-link", has_text="Artists")).to_be_visible()
    expect(page.locator("a.nav-link", has_text="Venues")).to_be_visible()

def test_language_switch_on_event_list(page: Page, live_server_url: str):
    # Start with the events page in English
    page.goto(f"{live_server_url}/events/")
    
    # Accept cookies to ensure navigation works
    page.click("button.btn-accept")
    
    # Switch to Spanish
    with page.expect_navigation():
        page.select_option("select[name='language']", "es")
    
    # Verify we're still on the events page but in Spanish
    expect(page).to_have_url(f"{live_server_url}/es/events/")
    expect(page.locator("h1", has_text="Eventos")).to_be_visible()
    
    # Switch back to English
    with page.expect_navigation():
        page.select_option("select[name='language']", "en")
    
    # Verify we're back on the English events page
    expect(page).to_have_url(f"{live_server_url}/events/")
    expect(page.locator("h1", has_text="Events")).to_be_visible()

def test_language_switch_preserves_cookie_consent(page: Page, live_server_url: str):
    # Start with the home page
    page.goto(f"{live_server_url}/")
    
    # Verify cookie consent is visible in English
    expect(page.locator("#cookie-consent-modal .modal-title", has_text="Cookie Consent Required")).to_be_visible()
    
    # Accept cookies
    page.click("button.btn-accept")
    
    # Switch to Spanish
    with page.expect_navigation():
        page.select_option("select[name='language']", "es")
    
    # Verify cookie consent remains accepted (not visible)
    expect(page.locator("#cookie-consent-modal")).not_to_be_visible()
    
    # Switch back to English
    with page.expect_navigation():
        page.select_option("select[name='language']", "en")
    
    # Verify cookie consent remains accepted
    expect(page.locator("#cookie-consent-modal")).not_to_be_visible()

def test_language_switch_with_query_params(page: Page, live_server_url: str):
    # Start with the events page with a search query
    page.goto(f"{live_server_url}/events/?search=test")
    
    # Accept cookies to ensure navigation works
    page.click("button.btn-accept")
    
    # Switch to Spanish
    with page.expect_navigation():
        page.select_option("select[name='language']", "es")
    
    # Verify URL maintains search parameter
    expect(page).to_have_url(f"{live_server_url}/es/events/?search=test")
    
    # Switch back to English
    with page.expect_navigation():
        page.select_option("select[name='language']", "en")
    
    # Verify URL still has search parameter
    expect(page).to_have_url(f"{live_server_url}/events/?search=test")