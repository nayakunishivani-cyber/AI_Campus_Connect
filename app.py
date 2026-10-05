import streamlit as st
from huggingface_hub import InferenceClient

from database import (
    init_db,
    create_user,
    authenticate
)


# =====================================================
# INITIALIZE DATABASE
# =====================================================

init_db()


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Campus Connect",
    page_icon="🎓",
    layout="wide"
)


# =====================================================
# SESSION STATE
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Login"


# =====================================================
# REGISTER PAGE
# =====================================================

def register_page():

    st.title("🎓 AI Campus Connect")

    st.subheader("📝 Create Account")

    st.write("Register to access the AI Campus Assistant.")

    with st.form("register_form"):

        name = st.text_input(
            "Full Name"
        )

        email = st.text_input(
            "Email Address"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        department = st.selectbox(
            "Department",
            [
                "Computer Science",
                "Information Technology",
                "Electronics and Communication",
                "Electrical Engineering",
                "Mechanical Engineering",
                "Civil Engineering",
                "Other"
            ]
        )

        register = st.form_submit_button(
            "📝 Register",
            use_container_width=True
        )

    if register:

        # Check fields

        if not name or not email or not password:

            st.error(
                "❌ Please fill all required fields."
            )

        elif password != confirm_password:

            st.error(
                "❌ Passwords do not match."
            )

        elif len(password) < 6:

            st.error(
                "❌ Password must contain at least 6 characters."
            )

        else:

            success, message = create_user(
                name=name,
                email=email,
                password=password,
                role="student",
                department=department
            )

            if success:

                st.success(
                    "✅ Account created successfully!"
                )

                st.info(
                    "Please go to Login and sign in."
                )

                if st.button("➡️ Go to Login"):

                    st.session_state.auth_page = "Login"

                    st.rerun()

            else:

                st.error(
                    f"❌ {message}"
                )

    st.divider()

    if st.button(
        "⬅️ Already have an account? Login"
    ):

        st.session_state.auth_page = "Login"

        st.rerun()


# =====================================================
# LOGIN PAGE
# =====================================================

def login_page():

    st.title("🎓 AI Campus Connect")

    st.subheader("🔐 Login")

    email = st.text_input(
        "Email Address"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "🔐 Login",
        use_container_width=True
    ):

        user = authenticate(
            email=email,
            password=password
        )

        if user:

            st.session_state.logged_in = True

            st.session_state.user = user

            st.success(
                "✅ Login successful!"
            )

            st.rerun()

        else:

            st.error(
                "❌ Invalid email or password."
            )

    st.divider()

    st.write(
        "Don't have an account?"
    )

    if st.button(
        "📝 Create New Account",
        use_container_width=True
    ):

        st.session_state.auth_page = "Register"

        st.rerun()


# =====================================================
# SHOW LOGIN / REGISTER
# =====================================================

if not st.session_state.logged_in:

    if st.session_state.auth_page == "Register":

        register_page()

    else:

        login_page()

    st.stop()


# =====================================================
# LOGGED-IN USER
# =====================================================

user = st.session_state.user


# =====================================================
# HUGGING FACE TOKEN
# =====================================================

try:

    hf_token = st.secrets["HF_TOKEN"]

except Exception:

    hf_token = None


if not hf_token:

    st.error(
        "❌ Hugging Face API token is not configured."
    )

    st.info(
        "Add HF_TOKEN to .streamlit/secrets.toml"
    )

    st.stop()


# =====================================================
# HUGGING FACE CLIENT
# =====================================================

client = InferenceClient(
    api_key=hf_token,
    provider="auto"
)


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🎓 AI Campus Connect")

    st.write(
        f"👤 **Name:** {user['name']}"
    )

    st.write(
        f"📧 **Email:** {user['email']}"
    )

    st.write(
        f"🏫 **Department:** {user['department']}"
    )

    st.write(
        f"🔑 **Role:** {user['role']}"
    )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user = None

        st.session_state.auth_page = "Login"

        st.rerun()


# =====================================================
# AI ASSISTANT
# =====================================================

st.title("🤖 AI Campus Assistant")

st.write(
    f"Welcome, **{user['name']}**! 👋"
)

st.write(
    "Ask questions about programming, academics, "
    "projects, exams and more."
)


# =====================================================
# CHAT HISTORY
# =====================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# =====================================================
# CHAT INPUT
# =====================================================

question = st.chat_input(
    "Ask your question..."
)


# =====================================================
# AI RESPONSE
# =====================================================

if question:

    # Show user question

    with st.chat_message("user"):

        st.write(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # Generate response

    with st.chat_message("assistant"):

        with st.spinner("🤖 Thinking..."):

            try:

                response = client.chat.completions.create(

                    model="openai/gpt-oss-120b",

                    messages=[
                        {
                            "role": "system",
                            "content": """
You are AI Campus Connect,
a helpful college AI assistant.

Help students with:
- Academic questions
- Python
- Java
- Data Structures
- Software Engineering
- Projects
- Exam preparation
- Study planning
- Career guidance

Give simple and clear answers.
Use examples when useful.
"""
                        },
                        *st.session_state.messages
                    ],

                    max_tokens=1024,

                    temperature=0.7
                )


                answer = response.choices[0].message.content


                st.write(answer)


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


            except Exception as e:

                st.error(
                    f"❌ Hugging Face Error: {e}"
                )