# from shiny import App, render, ui
from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

from shinywidgets import output_widget, render_widget, render_plotly


import definitions.layout_styles as styles
from definitions.backend_funcs import detect_models, detect_terms, extract_results, plot_surfmap

@module.ui
def single_result_ui(start_model='els_global'):
    model_choice = ui.input_selectize(
        id='select_model',
        label='Choose model',
        choices=detect_models(),
        selected=start_model)

    term_choice = ui.output_ui('term_ui')

    output_choice = ui.input_selectize(
        id='select_output',
        label='Display',
        choices={'betas': 'Beta values', 'clusters': 'Clusters'},
        selected='betas')

    surface_choice = ui.input_selectize(
        id='select_surface',
        label='Surface type',
        choices={'pial': 'Pial', 'infl': 'Inflated', 'flat': 'Flat'},
        selected='pial')

    return ui.div(
        # Selection pane
        ui.row(
            ui.column(3, model_choice),
            ui.column(3, term_choice),
            ui.column(3, output_choice),
            ui.column(3, surface_choice),
            style=styles.SELECTION_PANE
        ),
        # Info
        ui.row(
            ui.output_text('info'),
            style=styles.INFO_MESSAGE
        ),
        # Brain plots
        ui.layout_columns(
            ui.card('Left hemisphere',
                    output_widget('brain_left'),
                    full_screen=True),  # expand icon appears when hovering over the card body
            ui.card('Right hemisphere',
                    output_widget('brain_right'),
                    full_screen=True)
        ))

@module.server
def update_single_result(input: Inputs, output: Outputs, session: Session) -> tuple:

    @output
    @render.ui
    def term_ui():
        mod = input.select_model()
        return ui.input_selectize(
            id='select_term',
            label="Choose term",
            choices=detect_terms(mod),
            selected=detect_terms(mod)[0])  # always switch to first term after intercept

    @render.text
    def info():
        min_beta, max_beta, mean_beta, _, _ = extract_results(model=input.select_model(),
                                                              term=input.select_term())
        return f'Mean beta value [range] = {mean_beta:.2f} [{min_beta:.2f}; {max_beta:.2f}]'

    @reactive.calc
    def brain3D():
        return plot_surfmap(model=input.select_model(),
                            term=input.select_term(),
                            surf=input.select_surface(),
                            output=input.select_output())
    @render_plotly
    def brain_left():
        brain = brain3D()
        return brain['left']

    @render_plotly
    def brain_right():
        brain = brain3D()
        return brain['right']

    return input.select_model, input.select_term


# ------------------------------------------------------------------------------

app_ui = ui.page_fillable(
    ui.panel_title("BrainMApp: early-life stress and intra-cortical myelination"),
    single_result_ui('result1', start_model='els_global'),
    single_result_ui('result2', start_model='pre_els_global'),

    ui.output_text('value1'),
    # ui.row(
    #     ui.column(3, ui.input_selectize(id='select_overlap_surface',
    #                                     label='Surface type',
    #                                     choices={'pial': 'Pial', 'infl': 'Inflated', 'flat': 'Flat'},
    #                                     selected='pial')),
    #     style=styles.SELECTION_PANE
    # ),
    # brain_plots('plots3'),

    padding=styles.PAGE_PADDING,
    gap=styles.PAGE_GAP,
)


def server(input, output, session):
    model1, term1 = update_single_result('result1')
    model2, term2 = update_single_result('result2')

    @output
    @render.text
    def value1():
        return f'You selected {term1()} from {model1()}.'


app = App(app_ui, server)

