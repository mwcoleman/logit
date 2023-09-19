import reflex as rx
import plotly.express as px
from logit.weightsapp import WState
import pandas as pd
# from weightsapp import LoggedExercise


# def set_row(exercise_number: int, exercise: str, set: int, reps: int, weight: float) -> rx.Component:
#     return rx.hstack(
#         rx.box(exercise_number),
#         rx.box(exercise),
#         rx.box(set),
#         rx.box(reps),
#         rx.box(weight),
#         rx.button(
#             on_click=lambda: WState.delete_row(exercise_number)
#         )
#         # margin_y="1em",
#     )

def get_exercise_details(ex):
    return rx.tr(
        # rx.td(ex.id),
        # rx.td(ex.idx),
        rx.td(ex.created_datetime),
        rx.td(ex.ename),
        rx.td(ex.enum),
        rx.td(ex.reps),
        rx.td(ex.weight),
        rx.td(
            rx.button(
                "X",
                on_click=lambda: WState.delete_logged_exercise(ex.id)
            )
        )
    )

def exercise_list() -> rx.Component:

    return rx.vstack(
        rx.heading(("")),
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
                        rx.th("")
                    )
                ),
                rx.tbody(
                    rx.foreach(
                        # WState.logged_exercises,
                        WState.iterate_logged_exercises,
                        lambda ex: get_exercise_details(ex)
                    )
                )
            )   
        )
    , width="100%") 

def new_exercise_selector(row_id: int) -> rx.Component:
    return rx.hstack(
        
        rx.select(
            WState.exercise_names,
            default_value=WState.exercise_names[0],
            on_change=lambda exercise: WState.set_current_exercise(row_id, exercise)
        ),
        
        rx.number_input(
            default_value=5,
            on_change=lambda reps: WState.set_reps(row_id, reps)),
        
        rx.number_input(
            default_value=70,
            on_change=lambda weight: WState.set_weight(row_id, weight)),
        
        rx.button(
            "+",
            on_click=lambda: WState.add_logged_exercise(row_id)
        ),


        
        )

# def get_figure():
#     with rx.session() as session:
#         ex_list = session.query(LoggedExercise).all()

#     ex_list = [ex._li() for ex in ex_list]  

#     data_columns = ["date", "ename", "enum", "reps", "kg"]
#     data_types = {'ename':str, 'enum': int, 'reps': int, 'kg': float}

#     df = pd.DataFrame(
#         ex_list,
#         columns=data_columns
#     ).astype(data_types)

#     df = df[df.ename == 'Scan']
#     df['date'] = df.date.apply(lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
#     df['load'] = df.reps * df.kg

#     grpby = df.groupby('date').aggregate(
#         vol=("reps", np.sum),
#         intensity=("kg", np.max),
#         load=("load",np.sum)
#     )

#     fig = go.Figure( data = [
#         go.Line(name="Weight", x=grpby.index, y=df['vol'])]
#     )
#     return fig

# def 


# def day_trend_plot():
#     df = WState._log_as_dataframe()
#     fig = px.line(df.groupby("date").sum(), x='date', y='weight')
#     return rx.Plotly(data=fig, height="400px")
#     return rx.Plotly(data=figure, height=height)

## TODO: Figure this out.. to have a button increment the number of pickers on screen
# def exercise_selectors() -> rx.Component:
    
#     selectors = rx.foreach(
#         WState.get_selector_count_range,
#         lambda i: rx.grid_item(
#                     new_exercise_selector(row_id=i), row_span=1, col_span=1, align_self="center"
#         )
#     )

#     return selectors


def index() -> rx.Component:
    # return rx.container(
    #     new_exercise_selector(),
    #     # new_exercise_selector(),
    #     exercise_list()

    # )

    return rx.container(
        rx.center(
            rx.grid(
                # *exercise_selectors(),

                rx.grid_item(
                    new_exercise_selector(row_id=1), row_span=1, col_span=1, align_self="center"
                ),
                rx.grid_item(
                    new_exercise_selector(row_id=2), row_span=1, col_span=1, align_self="center"
                ),

                rx.grid_item(
                    exercise_list(), row_span=1, col_span=1, align_self="center"
                ),
                # template_columns="repeat(4, 1fr)",
                # rx.grid_item(
                #     rx.data_table(
                #         data=WState.log_as_dataframe
                #     )
                # ),
                # rx.button(on_click=WState._day_stats),
                # rx.plotly(WState._day_stats)
            )
        )
    )

app = rx.App()
app.add_page(index)
app.compile()