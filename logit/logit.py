import reflex as rx
from sqlmodel import select
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List
import numpy as np
import pandas as pd
import os, datetime

try:
    from logit.weightsapp import WState
    from logit.weightsapp import LoggedExercise
    from logit.data_analysis import load_intensity_figure
except:
    from weightsapp import WState, LoggedExercise # for notebook debug

def get_exercise_details(ex, with_delete=True, benchmarks=False):
    
    if with_delete:
        delete_button = rx.button(
                        "X",
                        on_click=lambda: WState.delete_logged_exercise(ex.id, benchmarks)
                        )
    else:
        delete_button = rx.text("")

    return rx.tr(
        # rx.td(ex.id),
        # rx.td(ex.idx),
        rx.td(ex.created_datetime),
        rx.td(ex.ename),
        rx.td(ex.enum),
        rx.td(ex.reps),
        rx.td(ex.weight),
        rx.td(ex.rpe),
        rx.td(delete_button)
    )

def exercise_list(body_elements, heading="") -> rx.Component:
    if body_elements is None:
        return rx.text("No data")
    return rx.vstack(
        rx.heading((heading)),
        rx.table_container(
            rx.table(
                rx.thead(
                    rx.tr(
                        # rx.th("ID"),
                        rx.th("Date"),
                        rx.th("Exercise"),
                        rx.th("Set"),
                        rx.th("Reps"),
                        rx.th("Kg"),
                        rx.th("RPE"),
                        rx.th("")
                    )
                ),
                rx.tbody(
                    body_elements
                )
            )   
        )
    , width="100%") 

def date_benchmark_selector(spacings=[2,2,3]) -> List[rx.Component]:
    
    # def timer_component() -> rx.Component:
    #     return rx.card(
    #         rx.vstack(
    #             rx.hstack(
    #                 rx.number_input(
    #                     default_value=180,
    #                     on_change=WState.set_timer_start_val
    #                 ),
    #                 rx.button("Go", on_click=WState.start_timer)
    #             ),
    #             rx.text(WState.timer_count)
    #         )
    #     )
    
    return [
        rx.grid_item(
            rx.card(
                rx.select(
                    WState.date_range,
                    default_value=WState.date_range[0],
                    on_change=lambda d: WState.set_log_date(d)
                ),
                header=rx.heading("Date", size="sm"),
                size="sm"
            ),
            col_span=spacings[0],
            row_span=2,
        ),
        rx.grid_item(
            rx.card(
                rx.checkbox(
                    size="lg",
                    on_change=lambda c: WState.set_is_benchmark(c)),
                    header=rx.heading("Benchmark", size="sm"),
                    size="sm"
            ),
            col_span=spacings[1],
            row_span=2
        ),
        rx.grid_item(

        
            rx.card(
                timer(),
                header=rx.heading("Timer", size="sm"), size="sm"
            ),
            col_span=spacings[2],
            row_span=2
        )
    ]

def exercise_selector_heading(spacings=[3, 1, 1, 1, 1]) -> List[rx.Component]:
    return [
        rx.grid_item(
            rx.heading("Name", size="sm"),
            col_span=spacings[0],
            row_span=1
        ),

        rx.grid_item(
            rx.heading("Reps", size="sm"),
            col_span=spacings[1],
            row_span=1
        ),
        rx.grid_item(
            rx.heading("Kg", size="sm"),
            col_span=spacings[2],
            row_span=1
        ),
        rx.grid_item(
            rx.heading("RPE", size="sm"),
            col_span=spacings[3],
            row_span=1
        ),
        rx.grid_item(
            rx.heading("", size="sm"),
            col_span=spacings[4],
            row_span=1
        ),

    ]

def new_exercise_selector(row_id: int, spacings=[3, 1, 1, 1, 1]) -> List[rx.Component]:
    """Return list of grid items for one row, used with grid element in main page"""

    return [
        rx.grid_item(
            rx.select(
                WState.exercise_names,
                default_value=WState.exercise_names[0],
                on_change=lambda exercise: WState.set_current_exercise(row_id, exercise)
            ), 
            col_span=spacings[0],
            row_span=1
        ),

        rx.grid_item(
            rx.number_input(
                default_value=5,
                on_change=lambda reps: WState.set_reps(row_id, reps)
            ),
            col_span=spacings[1],
            row_span=1
        ),

        rx.grid_item(
            rx.number_input(
                default_value=70,
                on_change=lambda weight: WState.set_weight(row_id, weight)
            ),
            col_span=spacings[2],
            row_span=1
        ),

        rx.grid_item(
            rx.number_input(
                default_value=8,
                on_change=lambda weight: WState.set_rpe(row_id, weight)
            ),
            col_span=spacings[3],
            row_span=1
        ),

        rx.grid_item(
            rx.button(
            "+",
            on_click=lambda: WState.add_logged_exercise(row_id)
            ),
            col_span=spacings[4],
            row_span=1      
        )

    ]

#####
# TODO: These can be moved to a processing script
def log_as_df() -> pd.DataFrame:
    with rx.session() as session:
        ex_list = session.query(LoggedExercise).all()

    ex_list = [ex._li() for ex in ex_list]  

    data_columns = ["date", "ename", "enum", "reps", "kg", "rpe"]
    data_types = {'ename':str, 'enum': int, 'reps': int, 'kg': float, 'rpe':int}

    df = pd.DataFrame(
        ex_list,
        columns=data_columns
    ).astype(data_types)

    return df

def get_stats() -> pd.DataFrame:
    # This needs to/should be(?) be done outside of state otherwise 
    # we can't use it to generate the figure (with current knowledge..)

    df = log_as_df()

    df['date'] = df.date.apply(lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
    df['load'] = df.reps * df.kg

    grpby = df.groupby(['date','ename'], as_index=False).aggregate(
        vol=("reps", 'sum'),
        intensity=("kg", 'max'),
        load=("load",'sum')
    )

    return grpby







######


def strength_figure(df: pd.DataFrame, ename: str) -> go.Figure:
    # df.columns= ['date', 'ename', 'vol', 'intensity', 'load']
    metrics = ['load', 'intensity']

    data = df[df.ename==ename]
    # fig = px.line(data, x='date', y='intensity', title='intensity')
    # return fig
    y_label = ['Total Kg Moved', 'Max Kg Moved']

    fig = make_subplots(specs=[[{'secondary_y':True}]])

    # Add traces
    for i,metric in enumerate(metrics):
        fig.add_trace(
            go.Scatter(
                x=data['date'].values, y=data[metric], name=metric, #mode='lines'
            ),
            secondary_y=i==1
        )
        
        fig.update_yaxes(title_text=y_label[i], secondary_y=(i==1))

    # fig.update_layout(title_text=ename)
    fig.update_xaxes(title_text='Date')
    return fig

def last_exercise_dashboard() -> rx.Component:
    ex_list = WState.last_logged_exercise_max

    table = exercise_list(
        body_elements=
            rx.foreach(
                ex_list,
                lambda ex: get_exercise_details(ex, with_delete=False)
            ),
            heading="Last Max"
    )

  
    return table


def analysis() -> rx.Component:
    '''Here goes visualisations etc for logbook'''
    figure_load_intensity = load_intensity_figure('deadlift', log_as_df())
    layout_load_intensity = figure_load_intensity.to_dict()['layout']
    
    return rx.plotly(
                        data=figure_load_intensity,
                        height='400px',
                        layout=layout_load_intensity      
                    )
    
def timer() -> rx.Component:
    return rx.heading(
        WState.timer_count,
        on_click=WState.start_timer,
        _hover={"cursor":"pointer"}
    )


def index() -> rx.Component:
    # return rx.container(
    #     new_exercise_selector(),
    #     # new_exercise_selector(),
    #     exercise_list()

    # )
    # data = strength_figure(get_stats(), ename='benchpress')
    return rx.container(
        rx.center(
            rx.grid(
                # rx.grid_item(
                #     timer()
                # ),
                # rx.grid_item(
                #     date_benchmark_selector(), col_span=7, row_span=1
                # ),
                *date_benchmark_selector(),
                rx.grid_item(rx.spacer(), col_span=7, row_span=1),
                *exercise_selector_heading(),
                *new_exercise_selector(1),
                *new_exercise_selector(2),
                
                rx.grid_item(
                    last_exercise_dashboard(),
                    col_span=7, row_span=3
                ),
               ## TODO: Either of these work, but neither able to choose based on current_exercise. 
                # rx.grid_item(
                #     rx.plotly(
                #         data=load_intensity_figure('deadlift', log_as_df()),
                #         height='400px',
                #         layout=data.to_dict()['layout']       
                #     ),
                #     row_span=1, col_span=1, align_self='center'
                # ),
                # rx.grid_item(
                #     rx.plotly(
                #         data=data,
                #         height='400px',
                #         layout=data.to_dict()['layout']       
                #     ),
                #     row_span=1, col_span=1, align_self='center'
                # ),

                # Show a typical 8 week progression in +kg
                
                rx.grid_item(

                    rx.plotly(
                        data=WState.projected_progression_figure,
                        height="400px"
                        ),
                    row_span=3, col_span=7, align_self='center'
                ),

                rx.grid_item(
                    exercise_list(
                        body_elements=rx.foreach(
                            WState.iterate_logged_exercises,
                            lambda ex: get_exercise_details(ex)
                        ),
                        heading="Log",
                    ), 
                    row_span=3, 
                    col_span=7, 
                    align_self="center"
                ),
                rx.grid_item(
                    exercise_list(
                        body_elements=rx.foreach(
                            WState.iterate_logged_benchmarks,
                            lambda ex: get_exercise_details(ex, benchmarks=True)
                        ),
                        heading="Benchmark Log",
                    ), 
                    row_span=3, 
                    col_span=7, 
                    align_self="center"
                ),
                template_colums="repeat(7,1fr)",
                template_rows="repeat(14,fr)",
                gap=4
            ),
        )
    )

app = rx.App()
app.add_page(index)
app.compile()