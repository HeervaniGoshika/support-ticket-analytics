import os

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Support Intelligence AI",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #555;
        margin-bottom: 30px;
    }

    .answer-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f5f7fa;
        border-left: 5px solid #ff4b4b;
        margin-top: 20px;
        font-size: 18px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Support Intelligence AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Ask questions about customer support tickets using natural language."
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# BACKEND HEALTH CHECK
# ============================================================

def check_backend():
    """
    Check whether FastAPI backend is available.
    """

    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=5,
        )

        return response

    except requests.RequestException:
        return None


health_response = check_backend()


if health_response is None:

    st.error(
        f"Could not connect to the FastAPI backend at {API_URL}"
    )

else:

    if health_response.status_code == 200:

        st.success(
            "FastAPI backend connected successfully."
        )

    else:

        st.warning(
            f"FastAPI returned HTTP {health_response.status_code}"
        )


st.divider()


# ============================================================
# QUESTION SECTION
# ============================================================

st.header("🔎 Ask a Question")


question = st.text_input(
    "Enter your question",
    placeholder=(
        "Example: How many critical tickets are unresolved?"
    ),
)


# ============================================================
# QUERY FUNCTION
# ============================================================

def ask_backend(question: str):
    """
    Send a natural-language question to FastAPI.
    """

    payload = {
        "question": question,
    }

    try:

        response = requests.post(
            f"{API_URL}/query",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=120,
        )

    except requests.exceptions.ConnectionError as exc:

        st.error(
            "Could not connect to FastAPI.\n\n"
            f"Backend URL: {API_URL}\n\n"
            f"Details: {exc}"
        )

        return None

    except requests.exceptions.Timeout:

        st.error(
            "The FastAPI backend took too long to respond."
        )

        return None

    except requests.exceptions.RequestException as exc:

        st.error(
            f"Request failed: {exc}"
        )

        return None


    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    st.write(
        f"Backend status: `{response.status_code}`"
    )


    # ========================================================
    # HANDLE HTTP ERRORS
    # ========================================================

    if response.status_code != 200:

        st.error(
            f"FastAPI returned HTTP {response.status_code}"
        )

        st.code(
            response.text
            if response.text
            else "[Empty response body]"
        )

        return None


    # ========================================================
    # HANDLE EMPTY RESPONSE
    # ========================================================

    if not response.text.strip():

        st.error(
            "FastAPI returned an empty response."
        )

        return None


    # ========================================================
    # PARSE JSON SAFELY
    # ========================================================

    try:

        return response.json()

    except ValueError:

        st.error(
            "FastAPI returned a response that is not valid JSON."
        )

        st.write("Raw backend response:")

        st.code(
            response.text
        )

        return None


# ============================================================
# ASK AI BUTTON
# ============================================================

if st.button(
    "Ask AI",
    type="primary",
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Analyzing your question..."
        ):

            result = ask_backend(
                question
            )


        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        if result is not None:

            st.success(
                "Query completed successfully."
            )


            # ------------------------------------------------
            # Question
            # ------------------------------------------------

            st.subheader("Question")

            st.write(
                result.get(
                    "question",
                    question,
                )
            )


            # ------------------------------------------------
            # Intent
            # ------------------------------------------------

            if result.get("intent"):

                st.subheader("Detected Intent")

                st.code(
                    result["intent"]
                )


            # ------------------------------------------------
            # Answer
            # ------------------------------------------------

            if result.get("answer"):

                st.subheader("🤖 Answer")

                st.markdown(
                    f"""
                    <div class="answer-box">
                    {result["answer"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


            # ------------------------------------------------
            # Data
            # ------------------------------------------------

            data = result.get(
                "data",
                [],
            )


            if data:

                st.subheader("📊 Data")

                st.dataframe(
                    data,
                    use_container_width=True,
                )


            # ------------------------------------------------
            # Raw response
            # ------------------------------------------------

            with st.expander(
                "View API Response"
            ):

                st.json(
                    result
                )


# ============================================================
# ANOMALIES
# ============================================================

st.divider()

st.header("🚨 Anomaly Detection")


if st.button(
    "Check Anomalies"
):

    try:

        with st.spinner(
            "Checking support ticket anomalies..."
        ):

            response = requests.get(
                f"{API_URL}/anomalies",
                timeout=30,
            )


        if response.status_code != 200:

            st.error(
                f"FastAPI returned HTTP "
                f"{response.status_code}"
            )

            st.code(
                response.text
                if response.text
                else "[Empty response]"
            )

        else:

            if not response.text.strip():

                st.error(
                    "Anomaly endpoint returned an empty response."
                )

            else:

                try:

                    result = response.json()

                    st.success(
                        "Anomaly analysis completed."
                    )

                    st.json(
                        result
                    )

                except ValueError:

                    st.error(
                        "Anomaly endpoint returned "
                        "invalid JSON."
                    )

                    st.code(
                        response.text
                    )

    except requests.RequestException as exc:

        st.error(
            f"Could not connect to FastAPI: {exc}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"Backend: {API_URL}"
)