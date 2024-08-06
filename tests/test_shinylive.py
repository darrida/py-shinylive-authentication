from model import LoginPage2, browser_session
from playwright.sync_api import Playwright, sync_playwright

test_url = "http://localhost:8008/"


def test_basic_login(playwright: Playwright) -> None:
    with browser_session(playwright, test_url) as page:
        s = LoginPage2.init(page)
        # test
        s.setup_login()
        s.check_login()


def test_basic_logout(playwright: Playwright) -> None:
    with browser_session(playwright, test_url) as page:
        s = LoginPage2.init(page)
        s.setup_login()
        # test
        page.frame_locator("iframe").get_by_role("button", name="Logout").click()
        s.check_logout()


def test_missing_login_inputs_all(playwright: Playwright):
    with browser_session(playwright, test_url) as page:
        s = LoginPage2.init(page)
        # assign
        notification = page.frame_locator("iframe").get_by_text("'username' and 'password'")
        # test
        s.login_btn.click()
        notification.wait_for(state="attached")
        assert "'username' and 'password' fields are both required." in notification.all_text_contents()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        test_basic_login(playwright)
        test_basic_logout(playwright)
        test_missing_login_inputs_all(playwright)
