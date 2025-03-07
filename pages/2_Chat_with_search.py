import streamlit as st
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun

# -- Sidebar for API key entry
with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", 
        key="agile_ai_api_key_openai", 
        type="password"
    )
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/pages/2_Chat_with_search.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

# -- App Title
st.title("🤖 AGILE AI - Chat with Search")

"""
AGILE AI is an enhanced AI chatbot that can handle web searches and provide agile, context-driven responses.
Try additional LangChain 🤝 Streamlit Agent examples at:
[github.com/langchain-ai/streamlit-agent](https://github.com/langchain-ai/streamlit-agent).
"""

# -- Initialize chat history if empty
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": "Hi, I'm AGILE AI. I can search the web to help you. Ask me anything!"
        }
    ]

# -- Display existing chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# -- Chat input
user_input = st.chat_input(placeholder="What would you like AGILE AI to do?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # -- Require OpenAI API key
    if not openai_api_key:
        st.info("Please enter your OpenAI API key to proceed.")
        st.stop()

    # -- LLM and Agent setup
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo", 
        openai_api_key=openai_api_key, 
        streaming=True
    )
    search = DuckDuckGoSearchRun(name="Search")
    search_agent = initialize_agent(
        [search], 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
        handle_parsing_errors=True
    )

    # -- Streamlit callback handler for real-time LLM outputs
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
