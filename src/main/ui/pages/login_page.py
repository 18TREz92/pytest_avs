from playwright.sync_api import Page
from src.main.ui.utils.constans import Urls

class LoginPage:
    def open(self):
        self.page.goto(f"{Urls.BASE}/")

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.get_by_placeholder("Username")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.locator("#login-button")
        self.error_message = page.locator("h3[data-test='error']")


    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error_text(self) -> str:
        return self.error_message.inner_text()