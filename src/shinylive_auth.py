from dataclasses import dataclass
from typing import Optional, Protocol

from pydantic import SecretStr
from shiny import Inputs, Outputs, Session, module, reactive, render, ui

DEFAULT_MODULE_ID = "shiny_auth_module"


##########################################################################
##########################################################################
# Protocol for building custom login/session logic around Shinylive Auth
##########################################################################
##########################################################################
class AuthProtocol(Protocol):
    permissions: Optional[list] = None

    async def get_auth(self, username: str, password: SecretStr) -> str:
        """Request Authentication for ShinyLive

        - **Instructions**:
          - If auth is successful, return a session string (i.e. JWT) to be saved to browser local storage
          - If auth is invalid, raise `self.ShinyLiveAuthFailed`
          - If insufficient permissions, raise `self.ShinyLivePermissions`

        Args:
            username (str): Valid username
            password (pydantic.SecretStr): Vaide password
        
        Returns:
            str: session string (i.e. JWT)
              
        Raises:
            ShinyLiveAuthFailed: failed to validate credentials
            ShinyLivePermissions: credentials were validated, but user has insufficient permissions for the page/app
        """
        ...

    async def check_auth(self, token: str) -> str:
        """Check Existing Authentication Session for ShinyLive
        
        - **Instructions**:
          - If existing session is still valide, return a session string (i.e. JWT) to be re-saved to browser local storeage
          - If session is expired, raise `self.ShinyLiveAuthExpired`
          - If insufficient permissions, raise `self.ShinyLivePermissions`
          - ***Options:***
            - **If Session Never Refreshes:** Return the existing token
            - **If Sessoin Refreshes:** Return a different/refreshed token

        Args:
            username (str): Valid username
            password (pydantic.SecretStr): Valid password
        
        Returns:
            str: session string (i.e. JWT)
        
        Raises:
            ShinyLiveAuthExpired: existing session is expired
            ShinyLivePermissions: session is valid, but user has insufficient permissions for the page/app
        """
        ...

    class ShinyLiveAuthFailed(Exception):
        ...

    class ShinyLiveAuthExpired(Exception):
        ...

    class ShinyLivePermissions(Exception):
        ...


##########################################################################
##########################################################################
# Shinylive Auth UI Related
##########################################################################
##########################################################################
def login_popup():
    m = ui.modal(
        ui.input_text("username", "Username"),
        ui.input_password("password", "Password"),
        footer=(ui.input_action_button("submit_btn", "Submit")),
        title="Login",
        size='s'
    )
    ui.modal_show(m)
    return


class ProtectedView(Protocol):  # may use this to try and provide interface for 
    name: str = "main_view"


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


##########################################################################
##########################################################################
# Shinylive Auth Server Module Related
##########################################################################
##########################################################################
@dataclass
class AuthReactiveValues:
    token: reactive.Value[str] = reactive.Value()
    user: reactive.Value[str] = reactive.Value()
    hide_app: reactive.Value[bool] = reactive.Value(True)
    login_prompt: reactive.Value[bool] = reactive.Value()
    logout: reactive.Value[bool] = reactive.Value()


@module.server
def server(
    input: Inputs, output: Outputs, session: Session, 
    session_auth: AuthReactiveValues,
    app_auth: AuthProtocol
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
        session_auth.logout.set(False)
    

    @render.ui
    async def read_token():
        existing_token = str(input.token_hidden())
        # If no token, login
        if existing_token in ("", None):
            session_auth.login_prompt.set(True)
            return
        
        # Use `AuthProtocol.check_auth` to validate the existing session
        try:
            returned_token = await app_auth.check_auth(existing_token)
        except app_auth.ShinyLiveAuthExpired:
            ui.notification_show("Session expired. Please try again.", type="warning")
            session_auth.login_prompt.set(True)
            return
        except app_auth.ShinyLivePermissions:
            ui.notification_show("Insufficient permissions. Check with IT and then try again.", type="warning")
            session_auth.login_prompt.set(True)
            return
        
        # If both checks pass, set the token again
        # - This does two things:
        #   1. Triggers function that changes "hide_app" to False
        #   2. Sets token again, in case part of the verification is to update/refresh token
        session_auth.token.set(returned_token)


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
        password = SecretStr(value=input.password())
        if all([username, password]) is False:
            ui.notification_show("'username' and 'password' fields are both required.", type="warning")
            return
        
        # Use `AuthProtocol.get_auth` to validate provided credentials
        try:
            token = await app_auth.get_auth(username, password)
        except app_auth.ShinyLiveAuthFailed:
            ui.notification_show("Invalid username or password", type="warning")
            return
        except app_auth.ShinyLivePermissions:
            ui.notification_show("Insufficient permissions. Check with IT and then try again.", type="warning")
            session_auth.login_prompt.set(True)
            return

        # Code to return/assign a token here (i.e., an endpoint that produces JWT)
        session_auth.token.set(token)
        # session_auth.login_prompt.freeze()  # not sure if this is requierd

        # Close login popup
        ui.modal_remove()

    @reactive.effect
    async def _():
        if session_auth.logout.is_set():
            if session_auth.logout.get() is True:
                ui.insert_ui(
                    ui.HTML(
                        """
                        <script type="text/javascript">
                        localStorage.removeItem('x-auth-token');
                        </script>
                        """
                    ),
                    selector="#shiny_auth_module-token_hidden",
                    where="afterEnd",
                    immediate=True
                )
                session_auth.hide_app.set(True)
                session_auth.login_prompt.set(True)
