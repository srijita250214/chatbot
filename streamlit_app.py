import streamlit as st
import pandas as pd
import re
from datetime import datetime
from nltk.corpus import wordnet as wn

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_keywords" not in st.session_state:
    st.session_state.last_keywords = []
if "selected_problem" not in st.session_state:
    st.session_state.selected_problem = None
if "pending_feedback" not in st.session_state:
    st.session_state.pending_feedback = False

# Set up the Streamlit app
st.set_page_config(page_title="HitLit", page_icon="🤖", initial_sidebar_state="expanded")

@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path)

def save_csv(data, file_path):
    data.to_csv(file_path, index=False)

csv_file_path = r"\\kor2fs03\V-V--Testing$\03_Validation_Software\LLBP\VALSW_LL_BP_SPL_V1.1.csv"
csv_data = load_csv(csv_file_path)

def add_to_csv(entries):
    global csv_data
    new_entries = []
    
    for entry in entries:
        keyword, asic_module, problem, root_cause, solution, updater_name, project = entry
        serial_number = csv_data["Sr. No"].max() + 1 if not csv_data.empty else 1
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        new_entry = {
            "Sr. No": serial_number,
            "Year": date,
            "Author": updater_name,
            "Project": project,
            "Keywords(One word)": keyword.strip(),
            "ASIC/Module": asic_module.strip(),
            "Problem": problem.strip(),
            "Root cause": root_cause.strip(),
            "Solution": solution.strip()
        }

        new_entries.append(new_entry)

    new_entries_df = pd.DataFrame(new_entries)
    csv_data.drop(columns=['Updated By', 'Date', 'Serial Number'], errors='ignore', inplace=True)
    csv_data = pd.concat([csv_data, new_entries_df], ignore_index=True)
    
    # Remove unwanted lines from the DataFrame
    unwanted_lines_condition = csv_data.apply(lambda row: row.astype(str).str.contains(r"dlkd'als|fhpiq\[oe\[|oqpoeq-2pw|w219e-=210=|1ue2oqwp", case=False).any(), axis=1)
    csv_data = csv_data[~unwanted_lines_condition]

    save_csv(csv_data, csv_file_path)

def clean_and_split_query(query):
    filler_words = {
        'um', 'like', 'you', 'know', 'so', 'well', 'actually', 'basically', 'a',
        'just', 'really', 'the', 'an', 'is', 'are', 'was', 'were',
        'what', 'who', 'how', 'where', 'when', 'why', 'to', 'would',
        'i', 'me', 'his', 'her', 'ok', 'bye', 'it', 'on', 'and', 'but',
        'with', 'off', 'not', 'does', 'get', 'have', 'had', 'has', 'should',
        'this', 'that', 'these', 'those', 'my', 'your', 'our', 'his', 'her',
        'its', 'they', 'them', 'he', 'she', 'him', 'it', 'which', 'who',
        'whom', 'if', 'as', 'because', 'while', 'until', 'whereas', 'since',
        'for', 'nor', 'or', 'yet', 'so', 'both', 'either', 'neither',
        'not', 'just', 'always', 'often', 'sometimes', 'rarely', 'never'
    }

    cleaned_query = re.sub(r'[^\w\s]', '', query)
    words = cleaned_query.lower().split()
    return [word for word in words if word not in filler_words]


# def clean_and_split_query(query):
#     filler_words = {'um', 'like', 'you', 'know', 'so', 'well', 'actually', 'basically', 'just', 'really'}
#     stop_words = {'is', 'are', 'was', 'were', 'what', 'who', 'how', 'where', 'when', 'why', 'to', 'know', 
#                   'would', 'like', 'i', 'me', 'his', 'her', 'ok', 'bye', 'it', 'on', 'an', 'a', 'the', 
#                   'does', 'con', 'get', 'got', 'have', 'had', 'has', 'should', 'not', 'use', 'mobile', 
#                   'team', 'Verdict', 'no', 'but', 'with', 'off', 'issues', 'is', 'in', 'the', 'are', 'do','for','looking','look'}
    
#     cleaned_query = re.sub(r'[^\w\s]', '', query)
#     words = cleaned_query.lower().split()
#     # Keep only non-filler and non-stop words
#     return [word for word in words if word not in filler_words and word not in stop_words]

def get_problems_by_keyword(keyword):
    search_columns = ['Keywords(One word)', 'ASIC/Module']
    matches = csv_data[csv_data[search_columns].apply(lambda row: row.astype(str).str.contains(rf'\b{keyword}\b', case=False).any(), axis=1)]
    return matches['Problem'].tolist() if not matches.empty else []

def get_root_cause_and_solution(problem):
    problem_row = csv_data[csv_data['Problem'] == problem]
    if not problem_row.empty:
        return problem_row['Root cause'].values[0], problem_row['Solution'].values[0]
    return None, None

def is_adding_data_query(query):
    add_data_phrases = [
        "add data", "i want to add", "please add", "let's add", "adding data",
        "i need to add", "can you add", "add new entry", "new entry",
        "submit data", "want to input", "enter data",
        "i would like to do data entry", "i would like to add", "i want to input data",
        "can you help me add", "how do I add data", "i need to do data entry",
        "need to add information", "i want to submit","can i","can we add"
    ]
    
    return any(phrase in query.lower() for phrase in add_data_phrases)
def is_data_entry_query(query):
    data_entry_phrases = [
        "do a new data entry", "make a new entry", "create a new entry",
        "want to add an entry", "i want to input", "can i add",
        "i need to do data entry", "new data entry"
    ]
    
    return any(phrase in query.lower() for phrase in data_entry_phrases)

def is_deleting_data_query(query):
    delete_data_phrases = [
        "delete data", "remove entry", "can you delete", "please remove",
        "i want to delete", "how do i delete", "remove record"
    ]
    
    return any(phrase in query.lower() for phrase in delete_data_phrases)

def detect_keyword_type(keyword):
    """ Always return 'keyword' since we want to search in the CSV without type restrictions. """
    return "keyword"

def get_response(query):
    greeting_response = detect_greeting(query)
    if greeting_response:
        return greeting_response

    keywords = clean_and_split_query(query)

    if is_data_entry_query(query):
        return "Please provide the information to add a new data entry."

    if len(keywords) == 1:
        keyword = keywords[0]
        problems = get_problems_by_keyword(keyword)
        
        if problems:
            return list(set(problems))  # Return unique problems
        else:
            return "No related problems found for that keyword."

    # Handle multiple keywords
    problems = []
    for keyword in keywords:
        problems += get_problems_by_keyword(keyword)

    if problems:
        return list(set(problems))  # Return unique problems

    if is_adding_data_query(query):
        return "Please provide the information to add new data."

    if is_deleting_data_query(query):
        return "Please specify which entry you want to delete."

    return "What do you want to know about this?"

def detect_greeting(query):
    greetings = {
        "hi": "Hello! How can I assist you today?",
        "good morning": "Good morning! Have a nice day.",
        "good afternoon": "Good afternoon! Have a great day.",
        "good evening": "Good evening! Go and have snacks.",
        "good night": "Good night! Sleep well."
    }
    for key, value in greetings.items():
        if key in query.lower():
            return value
    return None

st.markdown("<h1 style='text-align: center;'> HitLit 🔥 </h1>", unsafe_allow_html=True)

# Add space between the title and the input
# st.markdown("<div style='height: 350px;'></div>", unsafe_allow_html=True)

# Refresh button in the top right corner
# if st.button("Refresh", key="refresh_button", help="Clear chat history", on_click=lambda: st.session_state.clear_chat()):
#     st.session_state.chat_history = []
#     st.success("Chat cleared successfully!")

user_input = st.text_input("Type your message", key="user_input")

if user_input:
    st.session_state.chat_history.append(user_input)
    ai_response = get_response(user_input)

    if is_adding_data_query(user_input):
        entries = []
        num_entries = st.number_input("How many entries do you want to add?", min_value=1, max_value=10, value=1)
        
        for i in range(num_entries):
            st.markdown(f"### Entry {i + 1}")
            updater_name = st.text_input(f"Enter Your Name for Entry {i + 1}:", key=f"name_input_{i}")
            keyword = st.text_input(f"Enter Keyword for Entry {i + 1}:", placeholder="e.g. Error Code 123", key=f"keyword_input_{i}")
            asic_module = st.text_input(f"Enter ASIC/Module for Entry {i + 1}:", placeholder="e.g. Module XYZ", key=f"asic_module_input_{i}")
            problem = st.text_input(f"Enter Problem for Entry {i + 1}:", placeholder="Describe the issue", key=f"problem_input_{i}")
            root_cause = st.text_input(f"Enter Root Cause for Entry {i + 1}:", placeholder="Explain the root cause", key=f"root_cause_input_{i}")
            solution = st.text_input(f"Enter Solution for Entry {i + 1}:", placeholder="Provide the solution", key=f"solution_input_{i}")
            project = st.text_input(f"Enter Project for Entry {i + 1}:", placeholder="e.g. Project ABC", key=f"project_input_{i}")

            if st.button(f"Submit Entry {i + 1}", key=f"submit_entry_{i}"):
                if all([updater_name, keyword, asic_module, problem, root_cause, solution, project]):
                    entries.append((keyword, asic_module, problem, root_cause, solution, updater_name, project))
                    st.success(f"Entry {i + 1} submitted!")
                else:
                    st.error("Please fill in all fields before submitting.")

        if entries:
            add_to_csv(entries)
            st.success("All entries added successfully!")
            for entry in entries:
                st.session_state.chat_history.append(f"Added new data: {entry[0]}, {entry[1]}, {entry[2]}")

    elif is_deleting_data_query(user_input):
        # Implement deletion logic here as needed
        st.write("Deletion feature is not yet implemented.")

    elif isinstance(ai_response, list):
        selected_problem = st.selectbox("Select a problem:", options=ai_response)
        if st.button("Get Root Cause and Solution"):
            root_cause, solution = get_root_cause_and_solution(selected_problem)
            if root_cause and solution:
                st.write(f"**Root Cause:** {root_cause}")
                st.write(f"**Solution:** {solution}")
                st.session_state.chat_history.append(f"Root Cause: {root_cause}\nSolution: {solution}")
            else:
                st.write("No root cause and solution found.")

    else:
        st.session_state.chat_history.append(ai_response)

if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.success("Chat cleared successfully!")

st.markdown("<hr><p style='text-align: center;'><small>Made with ❤️ by Me</small></p>", unsafe_allow_html=True)
