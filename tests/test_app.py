import pytest
from model import LoginPage
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture("../src_dev/app.py")


def test_login_missing_all_inputs(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.login_btn.click()
    expect(page.get_by_text("'username' and 'password' fields are both required.")).to_be_visible()

def test_login_missing_password_input(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.username_input.set("username")
    s.login_btn.click()
    expect(page.get_by_text("'username' and 'password' fields are both required.")).to_be_visible()

def test_login_missing_username_input(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.password_input.set("password")
    s.login_btn.click()
    expect(page.get_by_text("'username' and 'password' fields are both required.")).to_be_visible()

def test_login_invalid_username(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.username_input.set("username_fake")
    s.password_input.set("password")
    s.login_btn.click()
    expect(page.get_by_text("Invalid username or password")).to_be_visible()

def test_login_invalid_password(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.username_input.set("username")
    s.password_input.set("password_fake")
    s.login_btn.click()
    expect(page.get_by_text("Invalid username or password")).to_be_visible()

def test_login_success(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)
    s.setup_login()

    s.check_login()

def test_login_token_created(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)
    
    s.setup_login()
    s.check_login()

    s.storage_d = page.context.storage_state()
    s.check_token_exists()

def test_login_refresh_still_valid(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.setup_login()

    page.reload()
    s.check_login()
    
    
def test_login_insufficient_permissions(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.username_input.set("username2")
    s.password_input.set("password2")
    s.login_btn.click()
    expect(page.get_by_text("Insufficient permissions. Check with IT and then try again.")).to_be_visible()

@pytest.fixture
def context(context):
    context.set_default_timeout(2 * 1000)
    yield context

def test_logout_success(page: Page, app: ShinyAppProc, context):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.setup_login()
    s.check_login()

    s.logout_btn.click()
    s.check_logout()
    page.reload()
    s.check_logout()

def test_logout_still_refresh(page: Page, app: ShinyAppProc, context):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.setup_login()
    s.check_login()
    s.logout_btn.click()
    s.check_logout()

    page.reload()
    s.check_logout()
    page.close()

def test_logout_token_removed(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    s = LoginPage()
    s.init(page)

    s.setup_login()
    s.check_login()
    s.storage_d = page.context.storage_state()
    s.check_token_exists()
    s.logout_btn.click()
    s.check_logout()

    s.storage_d = page.context.storage_state()
    assert len(s.storage_d["origins"]) == 0
    