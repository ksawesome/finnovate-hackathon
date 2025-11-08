"""
AI Assistant Chat UI for Project Aura.

Provides conversational interface for:
- Natural language queries about GL accounts
- Knowledge base search (RAG)
- Financial analytics
- Account assignments
"""

from datetime import datetime

import streamlit as st

from ..agent import create_enhanced_agent, query_agent
from ..rag import RAGPipeline, VectorStoreManager


def initialize_chat_components() -> tuple:
    """
    Initialize RAG pipeline and agent (cached).

    Returns:
        Tuple of (rag_pipeline, agent_executor)
    """
    if "rag_pipeline" not in st.session_state:
        with st.spinner("🔧 Initializing AI components..."):
            # Initialize vector store manager
            manager = VectorStoreManager()

            # Initialize RAG pipeline
            rag_pipeline = RAGPipeline(manager)

            # Create enhanced agent
            agent = create_enhanced_agent(rag_pipeline)

            # Cache in session state
            st.session_state.rag_pipeline = rag_pipeline
            st.session_state.agent = agent

    return st.session_state.rag_pipeline, st.session_state.agent


def get_suggested_questions() -> list[str]:
    """Get list of suggested questions for users."""
    return [
        "What is a trial balance?",
        "Explain variance analysis",
        "What are the SLA deadlines for GL account reviews?",
        "How does Project Aura help with financial reviews?",
        "What is a GL hygiene score?",
        "Show me GL account 10010001 for AEML in Mar-24",
        "Run variance analysis for AEML",
        "What accounts are assigned to me?",
        "Check SLA compliance for all entities",
        "What supporting documents are required for GL accounts?",
    ]


def render_message(role: str, content: str, metadata: dict | None = None):
    """
    Render a chat message with optional metadata.

    Args:
        role: 'user' or 'assistant'
        content: Message content
        metadata: Optional metadata (sources, timing, etc.)
    """
    with st.chat_message(role):
        st.markdown(content)

        # Display metadata if available
        if metadata and role == "assistant":
            # Show sources if available
            if metadata.get("sources"):
                with st.expander("📚 Sources"):
                    for i, source in enumerate(metadata["sources"][:5], 1):
                        st.markdown(f"**{i}. {source.get('source', 'Unknown')}**")
                        st.markdown(f"   - Type: {source.get('doc_type', 'N/A')}")
                        st.markdown(f"   - Relevance: {source.get('relevance_score', 0):.2%}")
                        if "snippet" in source:
                            st.markdown(f"   - Preview: _{source['snippet'][:100]}..._")

            # Show query time if available
            if "query_time" in metadata:
                st.caption(f"⏱️ Response time: {metadata['query_time']:.2f}s")


def render_ai_assistant_page():
    """Render the AI Assistant chat interface."""
    st.title("🤖 AI Assistant")
    st.markdown(
        """
    Ask me anything about GL accounts, financial processes, or Project Aura!

    I can help you with:
    - 📖 **Knowledge**: Explain accounting concepts and processes
    - 🔍 **Account Lookup**: Get GL account details
    - 📊 **Analytics**: Run financial analysis
    - 👥 **Assignments**: Check account assignments
    """
    )

    # Initialize components
    try:
        rag_pipeline, agent = initialize_chat_components()
        st.success("✅ AI Assistant ready!")
    except Exception as e:
        st.error(f"❌ Error initializing AI: {e!s}")
        st.info("💡 Make sure GOOGLE_API_KEY is set in your .env file")
        return

    # Sidebar with suggested questions and settings
    with st.sidebar:
        st.header("💡 Suggested Questions")

        suggested = get_suggested_questions()
        for question in suggested:
            if st.button(question, key=f"suggest_{question[:20]}"):
                # Add to chat history
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()

        st.divider()

        # Chat settings
        st.header("⚙️ Settings")

        mode = st.radio(
            "Response Mode",
            options=["Agent (Multi-tool)", "RAG Only (Knowledge Base)"],
            help="Agent mode uses multiple tools for complex queries. RAG mode only searches documentation.",
        )
        st.session_state.chat_mode = mode

        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        # Stats
        if "messages" in st.session_state:
            st.divider()
            st.metric("Messages", len(st.session_state.messages))
            user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("Questions Asked", user_msgs)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": """👋 Hello! I'm your AI assistant for Project Aura.

I can help you with GL account reviews, financial analysis, and system documentation.

**Try asking:**
- "What is a trial balance?"
- "Show me GL account 10010001 for AEML"
- "Run variance analysis for AEML in Mar-24"

What would you like to know?""",
                "metadata": {},
            }
        )

    # Display chat history
    for message in st.session_state.messages:
        render_message(
            role=message["role"], content=message["content"], metadata=message.get("metadata", {})
        )

    # Chat input
    if prompt := st.chat_input("Ask me anything about GL accounts..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                start_time = datetime.now()

                try:
                    # Choose mode
                    if st.session_state.get("chat_mode") == "RAG Only (Knowledge Base)":
                        # RAG-only mode
                        response_data = rag_pipeline.query(
                            question=prompt, include_sources=True, top_k=3
                        )
                        response_text = response_data["answer"]
                        metadata = {
                            "sources": response_data.get("sources", []),
                            "query_time": (datetime.now() - start_time).total_seconds(),
                        }
                    else:
                        # Agent mode (multi-tool)
                        response_text = query_agent(agent, prompt)
                        metadata = {"query_time": (datetime.now() - start_time).total_seconds()}

                    # Display response
                    st.markdown(response_text)

                    # Display metadata
                    if metadata.get("sources"):
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(metadata["sources"][:5], 1):
                                st.markdown(f"**{i}. {source.get('source', 'Unknown')}**")
                                st.markdown(f"   - Type: {source.get('doc_type', 'N/A')}")
                                st.markdown(
                                    f"   - Relevance: {source.get('relevance_score', 0):.2%}"
                                )

                    if "query_time" in metadata:
                        st.caption(f"⏱️ Response time: {metadata['query_time']:.2f}s")

                    # Add to history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response_text, "metadata": metadata}
                    )

                except Exception as e:
                    error_msg = f"❌ Error generating response: {e!s}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg, "metadata": {}}
                    )

    # Footer with tips
    st.divider()
    st.caption(
        """
    💡 **Tips:**
    - Use specific account codes for detailed lookups (e.g., "10010001")
    - Mention entity names for entity-specific queries (e.g., "AEML", "APSEZ")
    - Ask follow-up questions to dig deeper
    - Switch between Agent and RAG modes in the sidebar
    """
    )


# Standalone execution for testing
if __name__ == "__main__":
    st.set_page_config(page_title="AI Assistant - Project Aura", page_icon="🤖", layout="wide")
    render_ai_assistant_page()
