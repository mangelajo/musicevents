import pytest
from playwright.sync_api import expect, Page

def test_language_switch_maintains_page(page: Page, live_server_url: str):
    # Start with the home page in English
    page.goto(f"{live_server_url}/")
    
    # Verify initial English content
    expect(page.get_by_role("link", name="Events", exact=True).first).to_be_visible()
    expect(page.get_by_role("link", name="Artists", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Venues", exact=True)).to_be_visible()
    
    # Switch to Spanish
    with page.expect_navigation():
        page.select_option("select[name='language']", "es")
    
    # Verify Spanish content
    expect(page.get_by_role("link", name="Eventos", exact=True).first).to_be_visible()
    expect(page.get_by_role("link", name="Artistas", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Locales", exact=True)).to_be_visible()
    
    # Switch back to English
    with page.expect_navigation():
        page.select_option("select[name='language']", "en")
    
    # Verify English content again
    expect(page.get_by_role("link", name="Events", exact=True).first).to_be_visible()
    expect(page.get_by_role("link", name="Artists", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Venues", exact=True)).to_be_visible()

def test_language_switch_on_event_list(page: Page, live_server_url: str):
    # Start with the events page in English
    page.goto(f"{live_server_url}/events/")
    
    # Switch to Spanish
    with page.expect_navigation():
        page.select_option("select[name='language']", "es")
    
    # Verify we're still on the events page but in Spanish
    expect(page).to_have_url(f"{live_server_url}/es/events/")
    expect(page.get_by_role("heading", name="Eventos", exact=True)).to_be_visible()
    
    # Switch back to English
    with page.expect_navigation():
        page.select_option("select[name='language']", "en")
    
    # Verify we're back on the English events page
    expect(page).to_have_url(f"{live_server_url}/events/")
    expect(page.get_by_role("heading", name="Events", exact=True)).to_be_visible()

def test_language_switch_preserves_cookie_consent(page: Page, live_server_url: str):
    # Start with the home page
    page.goto(f"{live_server_url}/")
    
    # Verify cookie consent is visible in English
    expect(page.get_by_text("Cookie Consent Required")).to_be_visible()
    
    # Accept cookies
    page.click("button.btn-accept")
    
    # Switch to Spanish
    with page.expect_navigation():
        page.select_option("select[name='language']", "es")
    
    # Verify cookie consent remains accepted (not visible)
    expect(page.get_by_text("Se Requiere Consentimiento de Cookies")).not_to_be_visible()
    
    # Switch back to English
    with page.expect_navigation():
        page.select_option("select[name='language']", "en")
    
    # Verify cookie consent remains accepted
    expect(page.get_by_text("Cookie Consent Required")).not_to_be_visible()

def test_language_switch_with_query_params(page: Page, live_server_url: str):
    # Start with the events page with a search query
    page.goto(f"{live_server_url}/events/?search=test")
    
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