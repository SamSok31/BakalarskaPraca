import ast
import threading
from datetime import datetime
from langchain_core.messages import HumanMessage
from plantuml import PlantUML
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from dotenv import load_dotenv
load_dotenv()

from ui_events import EVENT_QUEUE, RESPONSE_QUEUE
from gitHub.ingestion import GitHubExplorer
from orchestration.graph import build_graph
from utils.extraction import extract_plantuml


@st.cache_data(show_spinner=False)
def render_plantuml_cached(code):
    if not code:
        return None

    server = PlantUML(url='http://www.plantuml.com/plantuml/img/')
    
    try:
        return server.processes(code)
    except Exception as e:
        print("PlantUML error:", e)
        return None


def split_python_code(code: str):
    try:
        tree = ast.parse(code)
    except Exception:
        return {
            "imports": code,
            "classes": "",
            "main": "",
            "others": "" }

    lines = code.splitlines()

    def get_source(node):
        return "\n".join(lines[node.lineno - 1: node.end_lineno])

    imports = []
    classes = []
    main_parts = []
    others = []

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(get_source(node))

        elif isinstance(node, ast.ClassDef):
            classes.append(get_source(node))

        elif isinstance(node, ast.If):
            if (isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"):

                main_parts.append(get_source(node))
            else:
                others.append(get_source(node))

        elif isinstance(node, ast.FunctionDef) and node.name == "main":
            main_parts.append(get_source(node))

        else:
            others.append(get_source(node))

    return {
        "imports": "\n\n".join(imports),
        "classes": classes,
        "main": "\n\n".join(main_parts),
        "others": "\n\n".join(others) }


def init_state():
    if "user_input_task" not in st.session_state:
        st.session_state.user_input_task = ""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "status" not in st.session_state:
        st.session_state.status = {
            "use_case": "pending",
            "architecture": "pending",
            "methods": "pending",
            "assembly": "pending",
            "diagram": "pending" }

    if "github_logs" not in st.session_state:
        st.session_state.github_logs = []

    if "running" not in st.session_state:
        st.session_state.running = False

    if "explorer_started" not in st.session_state:
        st.session_state.explorer_started = False

    if "waiting_feedback" not in st.session_state:
        st.session_state.waiting_feedback = False

    if "waiting_persist" not in st.session_state:
        st.session_state.waiting_persist = False


def start_explorer():
    if not st.session_state.explorer_started:
        explorer = GitHubExplorer()

        thread = threading.Thread(target=explorer.start, daemon=True)
        thread.start()

        st.session_state.explorer_started = True


def process_events():
    while not EVENT_QUEUE.empty():
        event = EVENT_QUEUE.get()

        if event["type"] == "status":
            stage = event["stage"]

            found = False
            for key in st.session_state.status:
                if stage == "done":
                    st.session_state.status[key] = "done"
                    continue

                if key == stage:
                    st.session_state.status[key] = "running"
                    found = True
                elif not found:
                    st.session_state.status[key] = "done"
                else:
                    st.session_state.status[key] = "pending"


        elif event["type"] == "github_reset":
            current_time = datetime.now().strftime("%H:%M")

            st.session_state.github_logs = [f"Checking repository at {current_time}"]


        elif event["type"] == "github":
            st.session_state.github_logs.append(event["message"])


        elif event["type"] == "chat":
            st.session_state.messages.append({
                "role": event["role"],
                "content": event["content"] })
            

        elif event["type"] == "output":
            program = event.get("program", "")
            diagram = event.get("diagram", "")

            parts = split_python_code(program)

            if parts["imports"]:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "### 📦 Imports\n```python\n" + parts["imports"] + "\n```" })

            if parts["classes"]:
                for i, cls_code in enumerate(parts["classes"], 1):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"### 🧱 Class {i}\n```python\n{cls_code}\n```" })

            if parts["main"]:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "### ▶️ Main\n```python\n" + parts["main"] + "\n```" })

            if parts["others"]:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "### ⚙️ Others\n```python\n" + parts["others"] + "\n```" })

            st.session_state.messages.append({
                "role": "assistant",
                "type": "diagram",
                "content": diagram })
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Enter your feedback (or enter \"OK\" if you don't have any)" })
            
            st.session_state.waiting_feedback = True


        elif event["type"] == "persist":
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Do you want to add the generated functions to GraphRAG? (yes/no)" })
            st.session_state.waiting_persist = True


        elif event["type"] == "done":
            st.session_state.running = False


def set_sidebar():
    def render_status(label, key):
        state = st.session_state.status[key]

        if state == "done":
            st.sidebar.markdown(f"🟢 {label}")
        elif state == "running":
            st.sidebar.markdown(f"🟡 {label}")
        else:
            st.sidebar.markdown(f"⚪ {label}")


    st.sidebar.title("Agentic Code Generator")
    st.sidebar.markdown("---")
    st.sidebar.title("⚙️ System Status")

    render_status("Use Case", "use_case")
    render_status("Architecture", "architecture")
    render_status("Methods", "methods")
    render_status("Assembly", "assembly")
    render_status("Activity Diagram", "diagram")

    st.sidebar.markdown("---")
    st.sidebar.title("📦 GitHub Explorer")

    for log in st.session_state.github_logs[-15:]:
        st.sidebar.text(log)


def set_chat():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):

            if msg.get("type", "") == "diagram":
                code = extract_plantuml(msg["content"])
                img_url = render_plantuml_cached(code)

                if img_url:
                    st.image(img_url)
                else:
                    st.error("❌ Diagram rendering failed")

                with st.expander("Show source"):
                    st.code(code, language="text")

            else:
                st.markdown(msg["content"])


def set_input():
    if st.session_state.waiting_feedback:
        feedback = st.chat_input("Enter your feedback...")

        if feedback:
            RESPONSE_QUEUE.put({
                "type": "feedback",
                "message": feedback })
            
            st.session_state.messages.append({
                "role": "user",
                "content": feedback })
            st.session_state.waiting_feedback = False


    elif st.session_state.waiting_persist:
        answer = st.chat_input("Enter your answer...")

        if answer:
            RESPONSE_QUEUE.put({
                "type": "persist",
                "message": answer })
            
            st.session_state.messages.append({
                "role": "user",
                "content": answer })
            st.session_state.waiting_persist = False
            EVENT_QUEUE.put({"type": "done" })

    elif not st.session_state.running:
        user_input = st.chat_input("Enter your task...")
        if user_input:
            st.session_state.user_input_task = user_input
            starting_trigger()

    elif st.session_state.running:
        st.chat_input("System running...", disabled=True)

    else:
        st.chat_input("Job done...", disabled=True)


def run_pipeline(user_input):
    history = [HumanMessage(content=user_input)]
    agent = build_graph()

    try:
        agent.invoke({"messagesHistory": history}, {"recursion_limit": 200})

    except Exception as e:
        EVENT_QUEUE.put({
            "type": "chat",
            "role": "assistant",
            "content": f"❌ Error: {str(e)}" })
        
        EVENT_QUEUE.put({"type": "done" })
        
    finally:
        EVENT_QUEUE.put({"type": "done"})


def starting_trigger():
    task = st.session_state.user_input_task

    if not task or st.session_state.running:
        return
    
    st.session_state.running = True
    st.session_state.user_input_task = ""

    st.session_state.messages.append({
        "role": "user",
        "content": task })

    thread = threading.Thread(
        target=run_pipeline,
        args=(task,),
        daemon=True )
    thread.start()



st.set_page_config(layout="wide")

init_state()
start_explorer()
process_events()
set_sidebar()
set_chat()
set_input()

st_autorefresh(interval=3000, key="refresh")
