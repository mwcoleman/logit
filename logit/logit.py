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


def set_row(total_set_number: int, exercise: str, set: int, reps: int, weight: float) -> rx.Component:
    return rx.hstack(
        rx.box(total_set_number),
        rx.box(exercise),
        rx.box(set),
        rx.box(reps),
        rx.box(weight),
        rx.button(
            on_click=lambda: WState.delete_row(total_set_number)
        )
        # margin_y="1em",
    )


def exercise_list() -> rx.Component:
    # Returns a box, of QA pair boxes, given qa_pair strings below

    return rx.hstack(
        rx.box(
            rx.foreach(
                WState.session_history,
                lambda row: set_row(row[0], row[1], row[2], row[3], row[4])
            ) 
        ),

    )

def log_exercise() -> rx.Component:
    return rx.hstack(
        
        rx.select(
            WState.exercises,
            default_value=WState.exercises[0],
            on_change=WState.current_exercise
        ),
        
        rx.number_input(
            on_change=WState.set_reps),
        
        rx.number_input(
            on_change=WState.set_weight),
        
        rx.button(
            on_click=WState.add_set
        )
        
    )


def index() -> rx.Component:
    return rx.container(
        log_exercise(),
        exercise_list(),
    )

app = rx.App()
app.add_page(index)
app.compile()