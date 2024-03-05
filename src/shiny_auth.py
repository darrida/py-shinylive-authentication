from dataclasses import dataclass
from typing import List, Protocol

from shiny import Inputs, Outputs, Session, module, reactive, render, ui
from shiny_api_calls import get_url

DEFAULT_MODULE_ID = "shiny_auth_module"


def login_popup():
    m = ui.modal(
        ui.input_text("username", "Username"),
        ui.input_password("password", "Password"),
        footer=(ui.input_action_button("submit_btn", "Submit"))
    )
    ui.modal_show(m)
    return


@dataclass
class AuthReactiveValues:
    token: reactive.Value[str] = reactive.Value()
    user: reactive.Value[str] = reactive.Value()
    hide_app: reactive.Value[bool] = reactive.Value(True)
    login_prompt: reactive.Value[bool] = reactive.Value()
    permissions: List[str] = None


class ProtectedView(Protocol):  # may use this to try and provide interface for 
    name: str = "main_view"


class AuthProtocol(Protocol):
    def get_auth():
        ...

    def check_auth():
        ...


@module.ui
def view():
    return ui.row(
        ui.navset_hidden(
            ui.nav_panel(
                ui.input_text(id="token_hidden", label="t", value=""),
                ui.HTML(
                    """
                    <script type="text/javascript">
                    var x_auth_token = localStorage.getItem('x-auth-token');
                    document.getElementById('shiny_auth_module-token_hidden').value = x_auth_token;
                    </script>
                    """
                ),
                ui.output_ui("read_token"),
            ),
        ),
    )


@module.server
def server(
    input: Inputs, output: Outputs, session: Session, 
    session_auth: AuthReactiveValues = AuthReactiveValues(),
    app_auth: AuthProtocol = None
):
    @reactive.effect
    def _():
        token = session_auth.token.get()
        ui.insert_ui(
            ui.HTML(
                f"""
                <script type="text/javascript">
                localStorage.setItem('x-auth-token', "{token}");
                </script>
                """
            ),
            selector="#shiny_auth_module-token_hidden",
            where="afterEnd",
            immediate=True
        )
        session_auth.hide_app.set(False)
    
    @render.ui
    async def read_token():
        x_auth_token = input.token_hidden()
        # If no token, login
        if x_auth_token in ("", None):
            session_auth.login_prompt.set(True)
            return
        
        # Code to verify validity; if fails, login
        if x_auth_token != "123456789":
            ui.notification_show("Session expired. Login again", type="warning")
            session_auth.login_prompt.set(True)
            return
        
        # If both checks pass, set the token again
        # - This does two things:
        #   1. Triggers function change changes "hide_app" to False
        #   2. Sets token again, in case part of the verification is to update/refresh token
        session_auth.token.set(x_auth_token)


    @reactive.effect
    def _():
        # Only triggered when login_prompt is set; login_prompt is freeze/unset after launching login popup
        if session_auth.login_prompt.is_set():
            if session_auth.login_prompt.get() is True:
                login_popup()
                session_auth.login_prompt.freeze()


    @reactive.effect
    @reactive.event(input.submit_btn, ignore_none=True)
    async def _():
        username = input.username()
        password = input.password()
        
        # Code to evaluate credentials here
        if username != "test" or password != "test":
            ui.notification_show("Invalud username or password", type="warning")
            return
        
        # Code to return/assign a token here (i.e., an endpoint that produces JWT)
        x_auth_token = "123456789"
        session_auth.token.set(x_auth_token)
        # session_auth.login_prompt.freeze()  # not sure if this is requierd

        # Close login popup
        ui.modal_remove()
