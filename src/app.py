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


def server(input: Inputs, output: Outputs, session: Session):
    #################################################################################################
    # AUTH MODULE RELATED
    #################################################################################################
    
    session_auth = shiny_auth.AuthReactiveValues
    shiny_auth.server("shiny_auth_module", session_auth)


app = App(app_ui, server)