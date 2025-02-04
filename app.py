import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime, timedelta
import random

# Configure Gemini API using secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# Sample problems with intentional bugs
PROBLEMS = {
    "Even-Odd Checker": {
        "buggy_code": """
def check_even_odd(num)
    if num / 2 == 0:
        return "Even"
    else
        return "Odd"
        
# Test the function
print(check_even_odd(4))
""",
        "hints": [
            "Check the function definition syntax",
            "Division vs Modulo operator",
            "Missing colon in else statement"
        ],
        "solution": """
def check_even_odd(num):
    if num % 2 == 0:
        return "Even"
    else:
        return "Odd"
        
# Test the function
print(check_even_odd(4))
"""
    },
    "Binary Search": {
        "buggy_code": """
def binary_search(arr, target):
    left = 0
    right = len(arr)
    
    while left <= right:
        mid = (left + right) / 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Test the function
arr = [1, 2, 3, 4, 5]
print(binary_search(arr, 3))
""",
        "hints": [
            "Check the right pointer initialization",
            "Integer division vs float division",
            "Array index out of bounds possible"
        ],
        "solution": """
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Test the function
arr = [1, 2, 3, 4, 5]
print(binary_search(arr, 3))
"""
    },
    "List Reversal": {
        "buggy_code": """
def reverse_list(lst):
    for i in range(len(lst)):
        lst[i], lst[len(lst) - i] = lst[len(lst) - i], lst[i]
    return lst

# Test the function
test_list = [1, 2, 3, 4, 5]
print(reverse_list(test_list))
""",
        "hints": [
            "Think about the list indexing",
            "Consider how many swaps you really need",
            "Watch out for the index out of range error"
        ],
        "solution": """
def reverse_list(lst):
    for i in range(len(lst) // 2):
        lst[i], lst[len(lst) - 1 - i] = lst[len(lst) - 1 - i], lst[i]
    return lst

# Test the function
test_list = [1, 2, 3, 4, 5]
print(reverse_list(test_list))
"""
    },
    "Fibonacci Sequence": {
        "buggy_code": """
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    while len(sequence) <= n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

# Test the function
print(fibonacci(5))
""",
        "hints": [
            "Check the loop condition",
            "Think about the sequence length vs n",
            "Consider the expected output length"
        ],
        "solution": """
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

# Test the function
print(fibonacci(5))
"""
    },
    "Palindrome Check": {
        "buggy_code": """
def is_palindrome(text):
    text = text.lower()
    return text == text[::-1]

# Test the function
print(is_palindrome("A man, a plan, a canal: Panama"))
""",
        "hints": [
            "What about spaces and punctuation?",
            "Consider string cleaning",
            "Think about special characters"
        ],
        "solution": """
def is_palindrome(text):
    text = ''.join(char.lower() for char in text if char.isalnum())
    return text == text[::-1]

# Test the function
print(is_palindrome("A man, a plan, a canal: Panama"))
"""
    },
    "Find Missing Number": {
        "buggy_code": """
def find_missing(arr):
    n = len(arr)
    expected_sum = n * (n + 1) / 2
    actual_sum = sum(arr)
    return expected_sum - actual_sum

# Test the function
print(find_missing([0, 1, 3, 4, 5]))
""",
        "hints": [
            "Check the formula for sum of n numbers",
            "Think about the array length vs range",
            "Consider the actual range of numbers"
        ],
        "solution": """
def find_missing(arr):
    n = len(arr) + 1
    expected_sum = n * (n - 1) // 2
    actual_sum = sum(arr)
    return expected_sum - actual_sum

# Test the function
print(find_missing([0, 1, 3, 4, 5]))
"""
    }
}

# AI Assistant prompt template
AI_PROMPT_TEMPLATE = """
You are a debugging assistant for a programming game. Your goal is to help users find bugs in their code, but you should not directly give away the answers. Instead:

1. First try: Give a very vague hint about the general area of the bug
2. Second try: Give a more specific hint about what concept might be wrong
3. Third try: Give a detailed hint that almost reveals the solution
4. Fourth try: Finally reveal the solution

Current try number: {try_number}
Problem: {problem}
Buggy code:
{code}

Provide an appropriate hint based on the try number.
"""

def show_landing_page():
    # Remove any default margins/padding and center the content
    st.markdown("""
        <style>
        .main {
            padding-top: 0rem;
        }
        .landing-page {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            width: 100%;
            max-width: 800px;
        }
        div[data-testid="element-container"] div[data-testid="stHorizontalBlock"] {
            justify-content: center;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px auto;
            cursor: pointer;
            border-radius: 4px;
            border: none;
            transition-duration: 0.4s;
            width: 200px;
        }
        .stButton>button:hover {
            background-color: #45a049;
            color: white;
        }
        div.stButton {
            text-align: center;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # Center the content
    st.markdown('<div class="landing-page">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>ISA Python Debug Challenge 🐍 Level 2</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; margin: 20px 0;'>Test your debugging skills and learn from our AI assistant!</p>", unsafe_allow_html=True)
    
    if st.button("Start Game", key="start_game"):
        st.session_state.game_started = True
        st.session_state.game_active = True
        st.session_state.start_time = datetime.now()
        st.session_state.end_time = st.session_state.start_time + timedelta(seconds=180)
        st.session_state.current_problem = random.choice(list(PROBLEMS.keys()))
        st.session_state.messages = []
        st.session_state.try_count = 0
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_game_interface():
    st.markdown("""
        <style>
        .stTextArea textarea {
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            line-height: 1.5;
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 5px;
        }
        .stButton>button {
            width: 100%;
            padding: 10px 20px;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Debug Challenge 🐛")
    
    current_problem = st.session_state.current_problem
    
    # Calculate remaining time
    if st.session_state.game_active:
        current_time = datetime.now()
        time_remaining = st.session_state.end_time - current_time
        remaining_seconds = int(time_remaining.total_seconds())
        
        if remaining_seconds <= 0:
            st.session_state.game_active = False
            st.error("Time's up!")
            return

    # Timer placeholder at the top
    timer_placeholder = st.empty()
    
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.header("Debug Challenge")
        
        # Current problem display
        st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                <h3 style='margin: 0; color: #0e1117;'>Current Problem: {current_problem}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Problem display
        st.code(PROBLEMS[current_problem]["buggy_code"], language="python")
        
        # Code editor
        tabs = st.tabs(["Code Editor"])
        with tabs[0]:
            user_code = st.text_area(
                "Your Solution",
                value=PROBLEMS[current_problem]["buggy_code"],
                height=400,
                key="code_editor"
            )
        
        # Submit button
        if st.button("Submit Solution", key="submit"):
            if user_code.strip() == PROBLEMS[current_problem]["solution"].strip():
                st.success("🎉 Correct! You've fixed all the bugs!")
                st.session_state.game_active = False
                
                if st.button("Try Another Challenge", key="new_challenge"):
                    st.session_state.game_active = True
                    st.session_state.start_time = datetime.now()
                    st.session_state.end_time = st.session_state.start_time + timedelta(seconds=180)
                    st.session_state.current_problem = random.choice(list(PROBLEMS.keys()))
                    st.session_state.messages = []
                    st.session_state.try_count = 0
                    st.rerun()
            else:
                st.error("❌ Some bugs still remain. Keep trying!")

    with col2:
        st.header("AI Assistant")
        
        chat_container = st.container()
        
        with chat_container:
            # Initial greeting
            if len(st.session_state.messages) == 0:
                with st.chat_message("assistant"):
                    st.write("Hello! I'm your AI assistant made by ISA. I'm here to help you debug your code. Feel free to ask questions! I do have context about your code, so you don't need to give me the code. You can just directly chat with me.")
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask for help..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            st.session_state.try_count += 1
            ai_prompt = AI_PROMPT_TEMPLATE.format(
                try_number=st.session_state.try_count,
                problem=current_problem,
                code=PROBLEMS[current_problem]["buggy_code"]
            )
            
            response = model.generate_content([ai_prompt, prompt])
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()

    # Update timer display after rendering everything else
    if st.session_state.game_active:
        current_time = datetime.now()
        time_remaining = st.session_state.end_time - current_time
        remaining_seconds = int(time_remaining.total_seconds())
        remaining_minutes = remaining_seconds // 60
        remaining_seconds = remaining_seconds % 60
        
        timer_placeholder.markdown(f"""
            <div style='background-color: #e1f5fe; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                <h3 style='margin: 0; color: #0277bd; text-align: center;'>
                    Time Remaining: {remaining_minutes:02d}:{remaining_seconds:02d}
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Add small delay and rerun at the end
        time.sleep(0.1)  # Reduced sleep time for better responsiveness
        st.rerun()
def main():
    st.set_page_config(layout="wide", page_title="Debug Challenge")
    
    # Initialize session states
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if "game_active" not in st.session_state:
        st.session_state.game_active = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "try_count" not in st.session_state:
        st.session_state.try_count = 0
    if "current_problem" not in st.session_state:
        st.session_state.current_problem = random.choice(list(PROBLEMS.keys()))
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "end_time" not in st.session_state:
        st.session_state.end_time = None

    if not st.session_state.game_started:
        show_landing_page()
    else:
        show_game_interface()

if __name__ == "__main__":
    main()