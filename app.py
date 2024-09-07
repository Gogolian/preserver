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
        # This is the first interaction, so we ask for the username
        return [["What's your name?", None]], ""
    
    if len(history) == 1:
        # This is the second interaction, where we get the username
        username = message
        greeting = f"Hello {message}, let's preserve your knowledge"
        return history + [[message, None], [greeting, None], [get_next_question(message), None]], ""
    
    if message:
        # Save the user's answer
        save_answer(username, history[-1][0], message)
        
        # Get the next question
        question = get_next_question(username)
        if question:
            history.append([message, None])
            history.append([question, None])
        else:
            history.append([message, None])
            history.append(["No more questions. Thank you for your participation!", None])
    
    return history, ""

def initial_message():
    return [["What's your name?", None]]

with gr.Blocks() as app:
    username = gr.State("")
    chatbot = gr.Chatbot(value=initial_message())
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    msg.submit(chat, inputs=[msg, chatbot, username], outputs=[chatbot, msg])
    clear.click(lambda: None, None, chatbot, queue=False)

app.launch()
