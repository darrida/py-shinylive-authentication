from contextlib import contextmanager
from dataclasses import dataclass

from playwright.sync_api import Locator, Page, Playwright
from shiny.playwright import controller


@contextmanager
def browser_session(pw: Playwright, url: str):
    browser = pw.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    yield page
    context.close()
    browser.close()


@dataclass
class LoginPage2:
    login_modal: Locator
    username: Locator
    password: Locator
    login_btn: Locator
    logout_btn: Locator
    main_page: Locator
    storage_d: dict = None

    @staticmethod
    def init(page: Page) -> "LoginPage2":
        return LoginPage2(
            login_modal = page.frame_locator("iframe").get_by_role("heading", name="Login"),
            username = page.frame_locator("iframe").get_by_label("Username"),
            password = page.frame_locator("iframe").get_by_label("Password"),
            login_btn = page.frame_locator("iframe").get_by_role("button", name="Submit"),
            logout_btn = page.frame_locator("iframe").get_by_role("button", name="Logout"),
            main_page = page.frame_locator("iframe").get_by_label("Search for:"),
        )

    def setup_login(self):
        self.login_modal.wait_for(state="attached")
        self.username.click()
        self.username.fill("username")
        self.username.press("Tab")
        self.password.fill("password")
        self.login_btn.click()
        self.login_modal.wait_for(state="detached")

    def check_login(self):
        assert self.username.is_visible() is False
        assert self.password.is_visible() is False
        assert self.main_page.is_visible()  

    def check_logout(self):
        self.login_modal.wait_for(state="attached")
        assert self.login_modal.is_visible()
        assert self.username.is_visible()
        assert self.password.is_visible()

    # def check_token_exists(self):
    #     local_storage = self.storage_d["origins"][0]["localStorage"]
    #     assert local_storage[0]["name"] == "x-auth-token"
    #     assert len(local_storage[0]["value"]) > 0


# @dataclass
# class LoginPage:
#     username_input: controller.InputText = None
#     password_input: controller.InputPassword = None
#     login_btn: controller.InputActionButton = None
#     search_btn: controller.InputActionButton = None
#     logout_btn: controller.InputActionButton = None 
#     storage_d: dict = None

#     def init(self, page: Page) -> "LoginPage":
#         self.username_input = controller.InputText(page, "shiny_auth_module-username")
#         self.password_input = controller.InputPassword(page, "shiny_auth_module-password")
#         self.login_btn = controller.InputActionButton(page, "shiny_auth_module-submit_btn")
#         self.search_btn = controller.InputActionButton(page, "search_btn")
#         self.logout_btn = controller.InputActionButton(page, "shiny_auth_module-logout_btn")
#         self.storage_d: dict = None

#     def setup_login(self):
#         self.username_input.set("username")
#         self.password_input.set("password")
#         self.login_btn.expect.to_be_visible()
#         self.login_btn.click()
#         self.search_btn.expect.to_be_visible()
#         self.logout_btn.expect.to_be_visible()

#     def check_login(self):
#         self.logout_btn.expect_label("Logout")
#         self.logout_btn.expect.to_be_visible()
#         self.username_input.expect.not_to_be_visible()
#         self.password_input.expect.not_to_be_visible()
#         self.login_btn.expect.not_to_be_visible()

#     def check_logout(self):
#         self.username_input.expect.to_be_visible()
#         self.username_input.expect_label("Username")
#         self.password_input.expect.to_be_visible()
#         self.password_input.expect_label("Password")
#         self.login_btn.expect.to_be_visible()
#         self.login_btn.expect_label("Submit")
#         self.logout_btn.expect.not_to_be_focused()

#     def check_token_exists(self):
#         local_storage = self.storage_d["origins"][0]["localStorage"]
#         assert local_storage[0]["name"] == "x-auth-token"
#         assert len(local_storage[0]["value"]) > 0


 