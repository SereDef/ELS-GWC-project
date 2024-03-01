# from shiny import App, render, ui
from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

from shinywidgets import output_widget, render_plotly


import definitions.layout_styles as styles
from definitions.backend_funcs import detect_models, extract_results, compute_overlap, \
    plot_surfmap, plot_overlap

@module.ui
def single_result_ui(start_model='postnatal_stress'):
    model_choice = ui.input_selectize(
        id='select_model',
        label='Choose model',
        choices=detect_models(out_clean=True),
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
            ui.layout_columns(
                model_choice, term_choice, output_choice, surface_choice, resolution_choice,
                col_widths=(3, 3, 2, 2, 2),  # negative numbers for empty spaces
                gap='30px',
                style=styles.SELECTION_PANE),
            update_button,
            col_widths=(11, 1)
        ),
        # Info
        ui.row(
            ui.output_ui('info'),
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
        terms = list(detect_models()[mod].keys())
        return ui.input_selectize(
            id='select_term',
            label="Choose term",
            choices=terms,
            selected=terms[0])  # always switch to first term after intercept

    @render.text
    def info():
        min_beta, max_beta, mean_beta, n_clusters, _, _ = extract_results(model=input.select_model(),
                                                                          term=input.select_term())
        l_nc = int(n_clusters[0])
        r_nc = int(n_clusters[1])

        return ui.markdown(
            f'**{l_nc+r_nc}** clusters identified ({l_nc} in the left and {r_nc} in the right hemishpere).<br />'
            f'Mean beta value [range] = **{mean_beta:.2f}** [{min_beta:.2f}; {max_beta:.2f}]')

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
            ui.output_ui('overlap_info'),
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
                     single_result_ui('result1', start_model='prenatal_stress'),
                     single_result_ui('result2', start_model='postnatal_stress'),
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
        ovlp_info = compute_overlap(model1(), term1(), model2(), term2())[0]

        text = {}
        legend = {}
        for key in [1, 2, 3]:
            text[key] = f'**{ovlp_info[key][1]}%** ({ovlp_info[key][0]} vertices)' if key in ovlp_info.keys() else \
                '**0%** (0 vertices)'
            color = styles.OVLP_COLORS[key-1]
            legend[key] = f'<span style = "background-color: {color}; color: {color}"> oo</span>'

        return ui.markdown(f'There was a {text[3]} {legend[3]} **overlap** between the terms selected:</br>'
                           f'{text[1]} was unique to {legend[1]}  **{term1()}** (from the <ins>{model1()}</ins> model)</br>'
                           f'{text[2]} was unique to {legend[2]}  **{term2()}** (from the <ins>{model2()}</ins> model)')

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

