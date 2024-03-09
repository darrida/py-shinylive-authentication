import shiny_auth as auth
import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    auth.view(auth.DEFAULT_MODULE_ID),  # <---- AUTH SETUP HERE
    ui.output_ui("init_main_view"),  # <---- AUTH SETUP HERE
    shinyswatch.theme.darkly(),
    title="Test Auth Page",
)


def app_view():  # <---- AUTH SETUP HERE
    return ui.page_sidebar(
        ui.sidebar(
            ui.input_text("search_box", "Search for:"),
            ui.input_action_button("search_btn", "Submit")
        ),
        ui.output_ui("search_results_area")
    )


def server(input: Inputs, output: Outputs, session: Session):
    #################################################################################################
    # AUTH SETUP HERE
    session_auth = auth.AuthReactiveValues()
    auth.server(auth.DEFAULT_MODULE_ID, session_auth)
    
    @render.ui
    def init_main_view():
        if session_auth.hide_app.get() is True:
            return
        return app_view()
    #################################################################################################

    @reactive.effect
    @reactive.event(input.search_btn)
    def _():
        search = str(input.search_box())
        ui.insert_ui(
            ui.card(
                ui.markdown(f"Search for '**{search}**' would appear here!"),
                ui.input_action_button("clear_btn", "Clear", width="100px"),
                id="search_results_list"
            ),
            selector="#search_results_area",
            where="beforeEnd"
        )

    @reactive.effect
    @reactive.event(input.clear_btn)
    def _():
        ui.remove_ui("#search_results_list")


app = App(app_ui, server)