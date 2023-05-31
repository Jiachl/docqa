import os
import pypdf
from utils.file_helper.config import CHUNK_SIZE, OVERLAP


class PDFHelper:

    @classmethod
    def parse_pdf(cls, fp, **kwargs):
        chunk = kwargs.get('chunk', CHUNK_SIZE)
        overlap = kwargs.get('overlap', OVERLAP)
        doc_key = kwargs.get('doc_key', None)
        doc_ref = kwargs.get('doc_ref', None)

        file_obj = open(fp, "rb")
        reader = pypdf.PdfReader(file_obj)
        if doc_key is None:
            file_name = os.path.basename(file_obj.name)
            doc_key, doc_ref = file_name, file_name

        text_split = ''
        text_split_list = []
        meta_list = []
        page_range = []

        for page, content in enumerate(reader.pages):
            text_split += content.extract_text()
            page_range.append(str(page + 1))

            while len(text_split) > chunk:
                text_split_list.append(text_split[:chunk])
                meta_list.append(cls.get_meta(doc_key, doc_ref, page_range[0], page_range[-1]))
                text_split = text_split[chunk - overlap:]
                page_range = [str(page + 1)]

        if len(text_split) > overlap:
            text_split_list.append(text_split[:chunk])
            meta_list.append(cls.get_meta(doc_key, doc_ref, page_range[0], page_range[-1]))

        file_obj.close()
        return text_split_list, meta_list
    @classmethod
    def get_meta(cls, doc_key, doc_ref, start_page, end_page):
        meta_data = dict(doc_key=doc_key, doc_ref=doc_ref, pages=f"{doc_key} pp. {start_page}-{end_page}")
        return meta_data



