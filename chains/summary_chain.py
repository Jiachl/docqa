from utils.file_helper.doc_loader import DocLoader
from langchain.prompts import PromptTemplate
from langchain import LLMChain
import pypdf
import os
from langchain.llms import OpenAI
from experiments.config import OPENAI_KEY


class SummaryChain:
    llm = OpenAI(model_name='gpt-3.5-turbo', temperature=0, openai_api_key=OPENAI_KEY)
    doc_dict = dict()
    bullet_prompt = """
    {text}

    Summarize 5-8 key points in bullet from the above text. 
    Each bullet point contains only 10-20 words. 
    Stick strictly to the facts in the text and do not invent new facts.
    """

    combine_prompt = """
    Combine the below key points into one paragraph. 
    Stick strictly to the facts in the provided text and do not invent new facts. The text to be summarized is:
    {text}
    """

    @classmethod
    def add_doc(cls, fp, **kwargs):
        file_name = kwargs.get('file_name', None)
        file_obj = open(fp, "rb")
        text_split = ''
        reader = pypdf.PdfReader(file_obj)
        if file_name is None:
            file_name = os.path.basename(file_obj.name)

        for page, content in enumerate(reader.pages):
            text_split += content.extract_text()
        cls.doc_dict[file_name] = text_split

    @classmethod
    def load_doc(cls, fp, **kwargs):
        doc_type = kwargs.get('doc_type', 'pdf')
        if doc_type == 'pdf':
            text = DocLoader.load_pdf(fp)
            clean_text = DocLoader.remove_key_points(text)
            clean_text = DocLoader.remove_url(clean_text)
            clean_text = DocLoader.remove_legal_disclaimer(clean_text)
            clean_text = DocLoader.remove_us_disclaimer(clean_text)
            clean_text = DocLoader.remove_contact_info(clean_text)
            clean_text = DocLoader.remove_footnote(clean_text)
            clean_text = DocLoader.remove_graph_numbers(clean_text)

            text_list = DocLoader.split_text(clean_text)
            return text_list
        else:
            return None

    @classmethod
    def get_bullets(cls, text_list, **kwargs):
        prompt_template = kwargs.get('prompt_template', cls.bullet_prompt)

        summary_lst = []
        for text in text_list:
            prompt = PromptTemplate(input_variables=["text"], template=prompt_template)
            chain = LLMChain(llm=cls.llm, prompt=prompt, verbose=False)
            bullets = chain.run(text)
            summary_lst += [bullets]
        return summary_lst

    @classmethod
    def combine_bullets(cls, text_list, **kwargs):
        prompt_template = kwargs.get('prompt_template', cls.combine_prompt)
        text = '\n'.join(text_list)
        prompt = PromptTemplate(input_variables=["text"], template=prompt_template)
        chain = LLMChain(llm=cls.llm, prompt=prompt, verbose=False)
        final_bullets = chain.run(text)
        return final_bullets

    @classmethod
    def summarize(cls, text_list, **kwargs):
        # text_list = self.load_doc(fp, **kwargs)
        summary_lst = cls.get_bullets(text_list, **kwargs)
        final_bullets = cls.combine_bullets(summary_lst, **kwargs)
        return final_bullets
