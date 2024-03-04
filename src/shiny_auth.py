from dataclasses import dataclass
from typing import List

from shiny import Inputs, Outputs, Session, module, reactive, render, ui
from shiny_api_calls import get_url


def login_popup():
    m = ui.modal(
        ui.input_text("username", "Username"),
        ui.input_password("password", "Password"),
        footer=(ui.input_action_button("submit_btn", "Submit"))
    )
    ui.modal_show(m)
    return


@module.ui
def view():
    return ui.row(
        ui.output_ui("read_token"),
    )


@dataclass
class AuthReactiveValues:
    token: reactive.Value[str] = reactive.Value()
    user: reactive.Value[str] = reactive.Value()
    hide_app: reactive.Value[bool] = reactive.Value(True)
    login_prompt: reactive.Value[bool] = reactive.Value(True)
    permissions_required: List[str] = None


@module.server
def server(
    input: Inputs, output: Outputs, session: Session, 
    session_auth: AuthReactiveValues = AuthReactiveValues()
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
            selector="#manage_token-token_hidden",
            where="afterEnd",
            immediate=True
        )
        session_auth.hide_app.set(False)
    
    @render.ui
    async def read_token():
        # print("read_token() function")
        ui.insert_ui(
            ui.navset_hidden(
                ui.nav_panel(
                    ui.input_text(id="token_hidden", label="t", value=""),
                    ui.HTML(
                        """
                        <script type="text/javascript">
                        var x_auth_token = localStorage.getItem('x-auth-token');
                        console.log("token in js");
                        console.log(x_auth_token);
                        document.getElementById('manage_token-token_hidden').value = x_auth_token;
                        </script>
                        """
                    ),
                ),
            ),
            selector="#manage_token-read_token",
            where="BeforeEnd",
            immediate=True
        )
        x_auth_token = input.token_hidden()
        if not x_auth_token:
            session_auth.login_prompt.set(True)
            return
        results = await get_url(
            url="http://localhost:8000/auth/login-check",
            headers={"Content-Type": "application/json"},
            body={"token": x_auth_token, "groups_needed": session_auth.permissions_required},
            type="json",
            clone=True,
            method="POST"
        )
        if int(results.status) in (204, 401):
            session_auth.login_prompt.set(True)
            return
        if int(results.status) != 200:
            ui.notification_show(f"Authentication check failed (Auth response code: {results.status})")
            return
        if int(results.status) == 403:
            ui.notification_show(results.status)
            ui.notification_show(str(results.data))
            ui.notification_show("Insufficient permissions.")
            return
        session_auth.user.set(results.data.get("username"))
        x_auth_token = results.data["token"]
        session_auth.token.set(x_auth_token)

    @reactive.effect
    def _():
        if session_auth.login_prompt.is_set():
            session_auth.login_prompt.get()
            login_popup()
            session_auth.login_prompt.freeze()

    @reactive.effect
    @reactive.event(input.submit_btn)
    async def _():
        username = input.username()
        password = input.password()
        results = await get_url(
            url="http://localhost:8000/auth/login-auth",
            headers={"Content-Type": "application/json"},
            body={"username": username, "password": password, "groups_needed": session_auth.permissions_required},
            type="json",
            clone=True,
            method="POST"
        )
        # if int(results.status) != 200:
        #     ui.notification_show(f"Authentication failed (Auth response code: {results.status})")
        #     return
        if int(results.status) == 401: 
            ui.notification_show(results.data)
            # if and "Insufficient permissions" in results.data.get("message"):
            # ui.notification_show(results.data.get("message"))
            return
        print(results.status)
        print(results.data)
        session_auth.user.set(results.data.get("username"))
        x_auth_token = results.data["token"]
        session_auth.token.set(x_auth_token)
        ui.modal_remove()