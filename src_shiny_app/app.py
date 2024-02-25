# from shiny import App, render, ui
from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

from shinywidgets import output_widget, render_plotly


import definitions.layout_styles as styles
from definitions.backend_funcs import detect_models, detect_terms, extract_results, plot_surfmap, plot_overlap

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

    resolution_choice = ui.input_selectize(
        id='select_resolution',
        label='Resolution',
        choices={'fsaverage': 'High (164k nodes)', 'fsaverage6': 'Medium (50k nodes)', 'fsaverage5': 'Low (10k modes)'},
        selected='fsaverage6')

    update_button = ui.div(ui.input_action_button(id='update_button',
                                                  label='UPDATE',
                                                  class_='btn btn-dark action-button'),
                           style='padding-top: 15px')

    return ui.div(
        # Selection pane
        ui.layout_columns(
            model_choice, term_choice, output_choice, surface_choice, resolution_choice, update_button,
            col_widths=(2, 2, 2, 2, 2, 2),  # negative numbers for empty spaces
            gap='30px',
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

    @reactive.Calc
    @reactive.event(input.update_button, ignore_none=False)
    def brain3D():
        return plot_surfmap(model=input.select_model(),
                            term=input.select_term(),
                            surf=input.select_surface(),
                            resol=input.select_resolution(),
                            output=input.select_output())
    @render_plotly
    @reactive.event(input.update_button, ignore_none=False)
    def brain_left():
        brain = brain3D()
        return brain['left']

    @render_plotly
    @reactive.event(input.update_button, ignore_none=False)
    def brain_right():
        brain = brain3D()
        return brain['right']

    return input.select_model, input.select_term


# ------------------------------------------------------------------------------
overlap_page = ui.div(
        # Selection pane
        ui.layout_columns(
            ui.input_selectize(
                id='overlap_select_surface',
                label='Surface type',
                choices={'pial': 'Pial', 'infl': 'Inflated', 'flat': 'Flat'},
                selected='pial'),
            ui.input_selectize(
                id='overlap_select_resolution',
                label='Resolution',
                choices={'fsaverage': 'High (164k nodes)', 'fsaverage6': 'Medium (50k nodes)', 'fsaverage5': 'Low (10k modes)'},
                selected='fsaverage6'),

            ui.div(' ', style='padding-top: 80px'),

            col_widths=(3, 3, 2),  # negative numbers for empty spaces
            gap='30px',
            style=styles.SELECTION_PANE
        ),
        # Info
        ui.row(
            ui.output_text('overlap_info'),
            style=styles.INFO_MESSAGE
        ),
        # Brain plots
        ui.layout_columns(
            ui.card('Left hemisphere',
                    output_widget('overlap_brain_left'),
                    full_screen=True),  # expand icon appears when hovering over the card body
            ui.card('Right hemisphere',
                    output_widget('overlap_brain_right'),
                    full_screen=True)
        ))
# ------------------------------------------------------------------------------

app_ui = ui.page_fillable(
    ui.page_navbar(
        ui.nav_spacer(),
        ui.nav_panel('Main results',
                     'Welcome to BrainMApp',  # Spacer - fix with padding later or also never
                     single_result_ui('result1', start_model='els_global'),
                     single_result_ui('result2', start_model='pre_els_global'),
                     ' ',  # Spacer
                     value='tab1'
                     ),
        ui.nav_panel('Overlap',
                     'Welcome to BrainMApp',  # Spacer - fix with padding later or also never
                     overlap_page,
                     ' ',  # spacer
                     value='tab2'
                     ),
        title="BrainMApp: early-life stress and intra-cortical myelination",
        selected='tab1',
        position='fixed-top',
        fillable=True,
        bg='white',
        window_title='BrainMApp',
        id='navbar'),

    padding=styles.PAGE_PADDING,
    gap=styles.PAGE_GAP,
)


def server(input, output, session):
    model1, term1 = update_single_result('result1')
    model2, term2 = update_single_result('result2')

    @output
    @render.text
    def overlap_info():
        return f'You selected {term1()} (from {model1()} model) and {term2()} (from {model2()} model).'

    @reactive.Calc
    def overlap_brain3D():
        return plot_overlap(model1=model1(),
                            term1=term1(),
                            model2=model2(),
                            term2=term2(),
                            surf=input.overlap_select_surface(),
                            resol=input.overlap_select_resolution())

    @render_plotly
    def overlap_brain_left():
        brain = overlap_brain3D()
        return brain['left']

    @render_plotly
    def overlap_brain_right():
        brain = overlap_brain3D()
        return brain['right']


app = App(app_ui, server)

