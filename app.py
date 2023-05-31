import streamlit as st
from streamlit_chat import message

import tempfile

import openai
from langchain import ConversationChain, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from paperqa import Docs
from chains.summary_chain import SummaryChain
from utils.file_helper.pdf_helper import PDFHelper
import os
from utils.file_helper.doc_loader import DocLoader
from experiments.config import OPENAI_KEY



os.environ["OPENAI_API_KEY"] = OPENAI_KEY

template = """Sophie is a work assistant from Launchpad at Bank Julius Baer.

Sophie is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Sophie is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Sophie is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Sophie is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Sophie is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Sophie is here to assist.

{history}
Human: {human_input}
Sophie:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"],
    template=template)

chatgpt_chain = LLMChain(
    llm=ChatOpenAI(temperature=0),
    prompt=prompt,
    verbose=False,
    memory=ConversationBufferWindowMemory(k=5),
)

qa_chain = Docs(llm='gpt-3.5-turbo')
summary_chain = SummaryChain()

st.set_page_config(page_title="Launchpad Sophie", page_icon="static/favicon.png")
st.markdown("<h1 style='text-align: center;'>Meet Sophie, your work assistant</h1>", unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": f"{template}"}
    ]

st.sidebar.title('Sophie from Launchpad')
counter_placeholder = st.sidebar.empty()
clear_button = st.sidebar.button("Clear Conversation", key="clear")
upload_files = st.sidebar.file_uploader("Upload Documents", accept_multiple_files=True)
file_list = ['None']
if len(upload_files) > 0:
    file_list = []
    for upload_file in upload_files:
        with tempfile.NamedTemporaryFile(suffix='.pdf', prefix=os.path.basename(__file__)) as tf:
            tf_directory = os.path.dirname(tf.name)
            tf.write(upload_file.read())
            qa_chain.add(tf.name, citation=upload_file.name, key=upload_file.name)
            summary_chain.add_doc(tf.name, file_name=upload_file.name)
            file_list.append(upload_file.name)

summarize_select = st.sidebar.selectbox('Select the document to summarize', file_list)
summarize_button = st.sidebar.button("Summarize", key="summarize")
if summarize_button and summarize_select != 'None' and summarize_select in summary_chain.doc_dict:
    clean_text = DocLoader.remove_key_points(summary_chain.doc_dict[summarize_select])
    clean_text = DocLoader.remove_url(clean_text)
    clean_text = DocLoader.remove_legal_disclaimer(clean_text)
    clean_text = DocLoader.remove_us_disclaimer(clean_text)
    clean_text = DocLoader.remove_contact_info(clean_text)
    clean_text = DocLoader.remove_footnote(clean_text)
    clean_text = DocLoader.remove_graph_numbers(clean_text)
    text_list = DocLoader.split_text(clean_text)
    summary_result = summary_chain.summarize(text_list)
    summary_input = f"""Summarize document {summarize_select}"""
    st.session_state['past'].append(summary_input)
    st.session_state['generated'].append(summary_result)

if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [{"role": "system", "content": f"{template}"}]
    chatgpt_chain = LLMChain(llm=ChatOpenAI(temperature=0), prompt=prompt, verbose=False,
                             memory=ConversationBufferWindowMemory(k=5))
    qa_chain = Docs(llm='gpt-3.5-turbo')

def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    try:
        response = chatgpt_chain.predict(human_input=user_input)
    except:
        response = "Sorry I am not able to understand your question. Please rephrase your question."
    st.session_state['messages'].append({"role": "assistant", "content": response})
    return response

# container for chat history
history_container = st.container()
# container for text box
container = st.container()

ask_in_doc = False
with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)

        left, mid, right = st.columns(3)
        submit_button = left.form_submit_button(label='Send')
        chat_in_doc = right.checkbox(label='Ask about the docs', value=ask_in_doc)

    if submit_button and user_input:
        if chat_in_doc:
            if len(upload_files) == 0:
                warning = 'Sorry I am not able to answer your question without any document provided. Please upload your documents first.'
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(warning)
                st.session_state['messages'].append({"role": "assistant", "content": warning})
                ask_in_doc = False
            else:
                output = qa_chain.query(user_input)
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output.answer)
                ask_in_doc = True
        else:
            output = generate_response(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
            ask_in_doc = False
if st.session_state['generated']:
    with history_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
