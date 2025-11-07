"""Feedback handler module."""

import streamlit as st


def handle_feedback(feedback: str):
    """
    Handle user feedback.

    Args:
        feedback: User feedback string.
    """
    # Placeholder: log or process feedback
    st.write(f"Feedback received: {feedback}")


def collect_feedback():
    """Collect feedback in Streamlit app."""
    feedback = st.text_area("Provide feedback:")
    if st.button("Submit"):
        handle_feedback(feedback)
