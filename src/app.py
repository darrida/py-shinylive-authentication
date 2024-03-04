import shiny_auth
import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

PERMISSIONS_REQUIRED=["general"]


app_ui = ui.page_sidebar(
        ui.sidebar(
            ui.output_ui("main_view"), 
            width="200px"
        ),
        shiny_auth.view("shiny_auth_module"),
        ui.output_ui("results"),
        shinyswatch.theme.darkly(),
        title="Test Utility",
        window_title="Shiny Auth",
        bg="#0062cc",
        inverse=True,
        id="navbar_id",
        # footer=footer(),
    )


def app_view():
    return ui.div(
        ui.input_text("test_box", "Test Box"),
        ui.input_action_button("click_me", "Click Me", width="100px")
    )


def server(input: Inputs, output: Outputs, session: Session):
    #################################################################################################
    # AUTH MODULE RELATED
    #################################################################################################
    
    session_auth = shiny_auth.AuthReactiveValues
    shiny_auth.server("shiny_auth_module", session_auth)

    @render.ui
    def main_view():
        if session_auth.hide_app.get() is True:
            return
        return app_view()


app = App(app_ui, server)