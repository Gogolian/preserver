import gradio as gr
import os
import difflib

QUESTIONS_DIR = "questions"
ANSWERS_DIR_TEMPLATE = "answers-{}"

def get_next_question(username):
    for root, _, files in os.walk(QUESTIONS_DIR):
        for file in files:
            if file.endswith(".txt"):
                question_path = os.path.join(root, file)
                answer_path = os.path.join(ANSWERS_DIR_TEMPLATE.format(username), os.path.relpath(question_path, QUESTIONS_DIR))
                
                if not os.path.exists(answer_path):
                    with open(question_path, "r") as f:
                        return f.read().strip()
    return None

def save_answer(username, question, answer):
    for root, _, files in os.walk(QUESTIONS_DIR):
        for file in files:
            if file.endswith(".txt"):
                question_path = os.path.join(root, file)
                with open(question_path, "r") as f:
                    if f.read().strip() == question:
                        answer_dir = os.path.join(ANSWERS_DIR_TEMPLATE.format(username), os.path.relpath(os.path.dirname(question_path), QUESTIONS_DIR))
                        os.makedirs(answer_dir, exist_ok=True)
                        answer_path = os.path.join(answer_dir, file)
                        with open(answer_path, "w") as f:
                            f.write(f"<USER>\n{question}\n<ANSWER>\n{answer}\n")
                        return

def chat(message, history, username):
    if not history:
        return [["What's your name?", None]], "", username

    if len(history) == 1:
        username = message
        next_question = get_next_question(username)
        if next_question:
            greeting = f"Hello {username}, let's preserve your knowledge"
            return history + [[message, None], [greeting, None], [next_question, None]], "", username
        else:
            completed_message = f"Hello {username}, you've already answered all of the questions available for now. Thank you, your knowledge is preserved"
            return history + [[message, None], [completed_message, None]], "", username

    if message:
        save_answer(username, history[-1][0], message)
        
        question = get_next_question(username)
        if question:
            history.append([message, None])
            history.append([question, None])
        else:
            history.append([message, None])
            history.append(["No more questions. Thank you for your participation!", None])
    
    return history, "", username

def initial_message():
    return [["What's your name?", None]]

with gr.Blocks() as app:
    username = gr.State("")
    chatbot = gr.Chatbot(value=initial_message())
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    msg.submit(chat, inputs=[msg, chatbot, username], outputs=[chatbot, msg, username])
    clear.click(lambda: None, None, chatbot, queue=False)

app.launch()
