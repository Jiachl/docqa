import os
from pathlib import Path
import hashlib
import warnings

from utils.file_helper.pdf_helper import PDFHelper
from utils.file_helper.config import CHUNK_SIZE, OVERLAP
import PyPDF2
from langchain.text_splitter import TokenTextSplitter
import re


class DocLoader:
    doc_set = set()
    doc_key_set = set()
    doc_index_list = []
    doc_meta_list = []

    min_doc_length = 10
    @classmethod
    def add_doc(cls, fp, **kwargs):
        file_obj = open(fp, "rb")
        file_hash = hashlib.md5(file_obj.read()).hexdigest()
        if file_hash in cls.doc_set:
            warnings.warn('The file has already been uploaded!')
            return

        cls.doc_set.add(file_hash)
        doc_key = kwargs.get('doc_key', None)
        doc_ref = kwargs.get('doc_ref', None)
        if doc_key is None:
            file_name = os.path.basename(file_obj.name)
            doc_key, doc_ref = file_name, file_name
            if doc_key in cls.doc_set:
                doc_key = str(Path(fp, file_name))
                if doc_key in cls.doc_set:
                    warnings.warn('Rename your file or provide a different file key!')
                    return
                doc_ref = doc_key

        cls.doc_set.add(doc_key)

        chunk = kwargs.get('chunk', CHUNK_SIZE)
        overlap = kwargs.get('overlap', OVERLAP)

        doc_type = kwargs.get('doc_type', 'pdf')
        if doc_type == 'pdf':
            text_split_list, meta_list = PDFHelper.parse_pdf(fp, doc_key=doc_key, doc_ref=doc_ref, chunk=chunk, overlap=overlap)
        else:
            text_split_list, meta_list = [], []  # TODO

        if len(text_split_list) == 0 or len(''.join(text_split_list)) < cls.min_doc_length:
            raise ValueError('This is not a valid document')
        cls.add_content(file_hash, text_split_list, meta_list)

    @classmethod
    def add_content(cls, file_hash, text_split_list, meta_list, **kwargs):
        pass

    @classmethod
    def remove_doc(cls, **kwargs):
        pass

    @classmethod
    def clear_docs(cls, **kwargs):
        pass

    @classmethod
    def load_pdf(cls, fp):
        text_lst = []
        with open(fp, 'rb') as pdf_file:

            pdf_reader = PyPDF2.PdfReader(pdf_file)
            print('file is here', pdf_reader)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page_obj = pdf_reader.pages[page_num]
                page_text = page_obj.extract_text()
                text_lst += [page_text]
                # print(page_text)
        pdf_text = " ".join(text_lst)
        return pdf_text

    @classmethod
    def split_text(cls, text, **kwargs):
        chunk = kwargs.get('chunk', CHUNK_SIZE)
        overlap = kwargs.get('overlap', OVERLAP)
        text_splitter = TokenTextSplitter(chunk_size=chunk, chunk_overlap=overlap)
        text_lst = text_splitter.split_text(text)
        return text_lst


    @classmethod
    def find_bullet_points(cls, text):
        bullet_pattern = re.compile(r'•\s*.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\.')
        matches = bullet_pattern.findall(text)
        bullet_lst = []
        for match in matches:
            bullet_lst += [match]
        return bullet_lst


    @classmethod
    def remove_key_points(cls, text):
        key_points_pattern = re.compile(r'•\s*.*\n*.*\n*.*\n*.*\n*.*\n*.*\n*.*\n*.*\n*.*\.')
        clean_text = re.sub(key_points_pattern, '', text)
        return clean_text


    @classmethod
    def remove_url(cls, text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        clean_text = re.sub(url_pattern, '', text)
        return clean_text


    @classmethod
    def remove_legal_disclaimer(cls, text):
        disclaimer_pattern = re.compile(
            r'IMPORTANT LEGAL INFORMATION.*?all documents referred to herein are written, and you have no need for any document whatsoever to be provided in Spanish or any other language\.?',
            re.DOTALL)
        clean_text = re.sub(disclaimer_pattern, '', text)
        return clean_text


    @classmethod
    def remove_us_disclaimer(cls, text):
        us_disclaimer_pattern = re.compile(r'UNITED STATES:.*?PERSON\.?', re.DOTALL)
        clean_text = re.sub(us_disclaimer_pattern, '', text)
        return clean_text


    @classmethod
    def remove_contact_info(cls, text):
        contact_info_pattern = re.compile(
            r'Please find important legal information at the end of this document.*?ins Format \«lampen\»\!?', re.DOTALL)
        clean_text = re.sub(contact_info_pattern, '', text)
        return clean_text


    @classmethod
    def remove_graph_numbers(cls, text):
        number_pattern = re.compile(r'\n\d+\%')
        clean_text = re.sub(number_pattern, '', text)
        return clean_text


    @classmethod
    def remove_footnote(cls, text):
        footnote_pattern = re.compile(r'\[\d+\]')
        clean_text = re.sub(footnote_pattern, '', text)
        return clean_text



