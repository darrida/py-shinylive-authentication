from dataclasses import dataclass

from playwright.sync_api import Page
from shiny.playwright import controller


@dataclass
class LoginPage:
    username_input: controller.InputText = None
    password_input: controller.InputPassword = None
    login_btn: controller.InputActionButton = None
    search_btn: controller.InputActionButton = None
    logout_btn: controller.InputActionButton = None 
    storage_d: dict = None

    def init(self, page: Page) -> "LoginPage":
        self.username_input = controller.InputText(page, "shiny_auth_module-username")
        self.password_input = controller.InputPassword(page, "shiny_auth_module-password")
        self.login_btn = controller.InputActionButton(page, "shiny_auth_module-submit_btn")
        self.search_btn = controller.InputActionButton(page, "search_btn")
        self.logout_btn = controller.InputActionButton(page, "shiny_auth_module-logout_btn")
        self.storage_d: dict = None

    def setup_login(self):
        self.username_input.set("username")
        self.password_input.set("password")
        self.login_btn.expect.to_be_visible()
        self.login_btn.click()
        self.search_btn.expect.to_be_visible()
        self.logout_btn.expect.to_be_visible()

    def check_login(self):
        self.logout_btn.expect_label("Logout")
        self.logout_btn.expect.to_be_visible()
        self.username_input.expect.not_to_be_visible()
        self.password_input.expect.not_to_be_visible()
        self.login_btn.expect.not_to_be_visible()

    def check_logout(self):
        self.username_input.expect.to_be_visible()
        self.username_input.expect_label("Username")
        self.password_input.expect.to_be_visible()
        self.password_input.expect_label("Password")
        self.login_btn.expect.to_be_visible()
        self.login_btn.expect_label("Submit")
        self.logout_btn.expect.not_to_be_focused()

    def check_token_exists(self):
        local_storage = self.storage_d["origins"][0]["localStorage"]
        assert local_storage[0]["name"] == "x-auth-token"
        assert len(local_storage[0]["value"]) > 0