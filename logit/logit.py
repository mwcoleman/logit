import reflex as rx
from logit.weightsapp import WState
# class State(rx.State):
#     question: str
#     chat_history: list[tuple[str, str]]
    
#     def set_question(self, question: str):
#         self.question = question
    
#     def answer(self):
#         # chatbt here
#         answer = "non lo so"
#         self.chat_history.append((self.question, answer))
#         self.question = ""


def set_row(exercise_number: int, exercise: str, set: int, reps: int, weight: float) -> rx.Component:
    return rx.hstack(
        rx.box(exercise_number),
        rx.box(exercise),
        rx.box(set),
        rx.box(reps),
        rx.box(weight),
        rx.button(
            on_click=lambda: WState.delete_row(exercise_number)
        )
        # margin_y="1em",
    )

def get_exercise_details(ex):
    return rx.tr(
        rx.td(ex.id),
        rx.td(ex.idx),
        rx.td(ex.ename),
        rx.td(ex.enum),
        rx.td(ex.reps),
        rx.td(ex.weight),
        rx.td(
            rx.button(
                "X",
                on_click=lambda: WState.delete_logged_exercise(ex.idx)
            )
        )
    )

def exercise_list() -> rx.Component:

    return rx.vstack(
        rx.heading(("Session Log")),
        rx.table_container(
            rx.table(
                rx.thead(
                    rx.tr(
                        rx.th("ID"),
                        rx.th("Tot#"),
                        rx.th("Exercise"),
                        rx.th("Set"),
                        rx.th("Reps"),
                        rx.th("Kg"),
                        rx.th("Delete")
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
    ) 

def new_exercise_selector() -> rx.Component:
    return rx.hstack(
        
        rx.select(
            WState.exercise_names,
            default_value=WState.current_exercise,
            on_change=WState.set_current_exercise
        ),
        
        rx.number_input(
            on_change=WState.set_reps),
        
        rx.number_input(
            on_change=WState.set_weight),
        
        rx.button(
            on_click=WState.add_logged_exercise
        )
        
    )


def index() -> rx.Component:
    return rx.container(
        new_exercise_selector(),
        exercise_list(),
        rx.text("HI")
        # rx.button(on_click=WState.iterate_logged_exercises)
    )

app = rx.App()
app.add_page(index)
app.compile()