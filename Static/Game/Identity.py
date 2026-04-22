import js
from pyscript import window

# Reference the browser's document
document = js.document

Quiz_content = [
    {
        "question": "Which teacher gives the MOST infractions?",
        "options": ["A. Mrs.Poce", "B. Mr. Moffat", "C. Mrs. Barnett", "D. Mr. Vervick"],
        "answer": ["A", "B"],
        "feedback": "Both Mrs. Poce and Mr. Moffat give the most infractions."
    },
    {
        "question": "What is the BEST class to sleep in?",
        "options": ["A. Science", "B. Math", "C. English", "D. History"],
        "answer": ["C", "D"],
        "feedback": "English is often considered the best class to sleep in."
    },
    {
        "question": "What is the acceptable skirt length above the knee? Inches.",
        "type": "input",
        "acceptable_lengths": [3, 4, 5, 6],
        "feedback": "The acceptable skirt length is between 3 to 6 inches above the knee."
    }

]

current_index = 0

def update_ui():
    """This function pushes the Python data into the HTML"""
    current_q = Quiz_content[current_index]
    document.querySelector("#question-text").innerText = current_q["question"]
    
    if "options" in current_q:
        document.querySelector("#options-list").innerText = " | ".join(current_q["options"])
    else:
        document.querySelector("#options-list").innerText = "(Type a number above)"

def check_answer(event):
    global current_index
    
    user_input_el = document.querySelector("#user-input")
    user_input = user_input_el.value.strip().upper()
    feedback_el = document.querySelector("#feedback")
    
    current_q = Quiz_content[current_index]
    
    # Simple logic check
    is_correct = False
    if "type" in current_q and current_q["type"] == "input":
        if user_input.isdigit() and int(user_input) in current_q["acceptable_lengths"]:
            is_correct = True
    elif user_input in current_q["answer"]:
        is_correct = True

    if is_correct:
        feedback_el.innerText = current_q["feedback"]
        feedback_el.style.color = "#4ade80"
        current_index += 1
        if current_index < len(Quiz_content):
            user_input_el.value = ""
            update_ui()
        else:
            document.querySelector("#question-text").innerText = "Identity Verified."
            document.querySelector("#options-list").innerText = "Welcome back."
            user_input_el.style.display = "none"
    else:
        feedback_el.innerText = "Access Denied. Try again."
        feedback_el.style.color = "#f87171"

# --- CRITICAL: INITIALIZE THE GAME ---
update_ui()