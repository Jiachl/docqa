import pypdf
import pdfplumber
import streamlit as st
import base64


def show_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    print(base64_pdf)
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    return None

pdf_container = st.container()
with pdf_container:
    uploaded_file = st.file_uploader("Upload documents", accept_multiple_files=True)
    file_map = {}
    if uploaded_file is not None:
        for i in range(len(uploaded_file)):
            # head, sep, tail = str(uploaded_file[i].name).partition(".")
            # st.write("file name：" + str(head))
            # st.write("file type：" + str(tail))
            st.write(uploaded_file[i])  # list of your files that you uploaded
            file_map[uploaded_file[i].name] = uploaded_file[i]


    file_selector = st.sidebar.radio("Choose a file:", (file_name for file_name in file_map))
    if len(file_map) > 0:
        st.write(file_selector)
        show_pdf(file_map[file_selector])
        st.write(file_map)

# with pdf_container:
#     uploaded_file = st.file_uploader("Upload documents", accept_multiple_files=False)
#     show_pdf(uploaded_file)
