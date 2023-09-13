import reflex as rx

class State(rx.State):
    question: str
    chat_history: list[tuple[str, str]]
    
    def set_question(self, question: str):
        self.question = question
    
    def answer(self):
        # chatbt here
        answer = "non lo so"
        self.chat_history.append((self.question, answer))
        self.question = ""


def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        rx.box(question, text_align="right"),
        rx.box(answer, text_align="left"),
        margin_y="1em",
    )


def chat() -> rx.Component:
    # Returns a box, of QA pair boxes, given qa_pair strings below

    return rx.box(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1])
        )
    )

def action_bar() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=State.question,
            placeholder="Ask ye question",
            on_change=State.set_question),
        rx.button(
            "Ask it",
            on_click=State.answer),
    )


def index() -> rx.Component:
    return rx.container(
        chat(),
        action_bar())

app = rx.App()
app.add_page(index)
app.compile()