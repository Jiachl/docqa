FROM python:3.10-bullseye

WORKDIR /usr/src/app

COPY . .
RUN pip install flask openai
RUN pip install langchain
RUN pip install google-search-results


EXPOSE 8888

CMD ["streamlit", "run", "app.py", "--port", "8888", "--host", "0000"]

# CMD [ "flask", "run", "--port", "8888", "--host", "0000" ]
