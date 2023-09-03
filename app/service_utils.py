from pdf2image import convert_from_path
import pytesseract
import cv2
from langchain import LLMChain
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import VectorStore, FAISS
from langchain.chat_models import ChatOpenAI

# from callback import StreamingLLMCallbackHandler
#
# from schemas import ChatResponse

from dotenv import load_dotenv

load_dotenv(dotenv_path='.env_dev')
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)

def get_schema() -> dict:
    schema = {
        'description_elevator': None,
        'address_object': None,
        'description_manufacturer': None,
        'address_manufacturer': None,
        'technical_specifications': None,
        'technical_specifications_description': None,
        'code_tnvd_eac': None,
        'tn_number_date': None,
        'eac_number': None,
        'protocol_pfl_sao': None,
        'act_tech_elevator_gospromnadzor': None,
        'list_protocols': None,
        'issued_by_whom_certificate': None,
        'assigned_lifetime': None,
        'data_is_valid': None,
    }
    return schema


def convert_pdf_to_png_file(path: str, dpi=500):
    return convert_from_path(path, dpi=dpi)


def get_ocr_image(path: str):
    img_cv = cv2.imread(path)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb, lang='rus+eng')
    return text


def get_qa(callback=None, temp=None):
    h_p = HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['question'], template='{question}'))
    messages = [SystemMessagePromptTemplate.from_template(temp), h_p]
    # md_3_5_t_16 = "gpt-3.5-turbo-16k"
    prompt = ChatPromptTemplate(messages=messages)
    embedding_function = OpenAIEmbeddings()
    # vectorstore = FAISS.load_local('faiss_index_open_ai', embeddings=embedding_function)
    # llm = ChatOpenAI(temperature=0, callbacks=[callback], streaming=True, model_name=md_3_5_t_16)
    chain = LLMChain(
        llm=ChatOpenAI(temperature=0),
        prompt=prompt,
    )

    return chain