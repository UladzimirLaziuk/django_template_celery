import os
from typing import List

import pytesseract
import cv2
from docxtpl import DocxTemplate
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from abc import ABC, abstractmethod
from app.service_utils import convert_pdf_to_png_file


class ConverterPdfToPng:
    def __init__(self, dirs_name=None):
        self.dirs_name = dirs_name
    def load(self, path_file, index_tuple='__all__', dpi=100):
        dir_path = os.path.dirname(path_file)
        path_dir_png = os.path.join(dir_path, self.dirs_name)
        os.makedirs(path_dir_png, exist_ok=True)
        list_png_file = []
        for index, el in enumerate(convert_pdf_to_png_file(path_file, dpi=dpi)):
            if isinstance(index_tuple, str) or index in index_tuple:
                file_name = os.path.join(path_dir_png, f'{self.dirs_name}_{index}.png')
                el.save(file_name)
                list_png_file.append(file_name)
        return list_png_file


# system_template = ''
human_template = """
    Вопрос:
    {question}
    Ответ:
    """


class ParseDocument(ABC):
    _name = ''
    system_template = ''
    human_template = human_template
    path_template = "templates/template.docx"
    path_out = 'generated_docs/generated_doc.docx'
    dict_parse_text = {}
    scale_percent = 100

    def __init__(self, path_file, converter, index_tuple=(1,6), llm=None):
        self.converter = converter
        self.path_file = path_file
        self.index_tuple = index_tuple
        self.list_png_file = []
        self.llm = llm or ChatOpenAI(temperature=0)

    def convert_pdf_and_save(self):
        self.list_png_file.extend(self.converter.load(self.path_file, self.index_tuple))

    def get_ocr_image(self, path: str):
        img_cv = cv2.imread(path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # scale_percent = 300  # percent of original size
        if self.scale_percent > 100:

            width = int(img_rgb.shape[1] * self.scale_percent / 100)
            height = int(img_rgb.shape[0] * self.scale_percent / 100)
            dim = (width, height)
            h, w, c = img_cv.shape
            img_rgb = cv2.resize(img_rgb, dim, interpolation=cv2.INTER_AREA)

        text = pytesseract.image_to_string(img_rgb, lang='rus+eng')
        return text

    def get_chat_promts(self, **kwargs):
        system_message_prompt = self.get_system_prompts(**kwargs)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        return chat_prompt

    @abstractmethod
    def get_system_prompts(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_col_token(self, index, **kwargs):
        raise NotImplementedError()


    def get_chain_run(self, text, **kwargs):
        chat_prompt = self.get_chat_promts(**kwargs)
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        return chain.run(text)

    def parse_text(self, text: str) -> dict:
        dict_parse = {}
        for chunk in text.split('\n'):
            keys, val = chunk.split(':')
            dict_parse.update({keys.strip(): val.strip()})
        return dict_parse

    def get_schema(self) -> dict:
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
            'list_protocols': [],
            'issued_by_whom_certificate': None,
            'assigned_lifetime': None,
            'data_is_valid': None,
        }
        return schema

    def map_dict_data(self, dict_data):
        dict_for_write = {}
        text_for_description = 'лифт пассажирский ' + ' '.join(dict_data.get('Назначение лифта').split()[1:])
        text_for_description += f' модель {dict_data.get("Модель лифта")}'
        text_for_description += ', ' + f'заводской номер  {dict_data.get("Заводской номер")}'
        dict_for_write.update({'description_elevator': text_for_description})
        description_manufacturer = f'изготовленный {dict_data.get("Предприятие-изготовитель")}'
        dict_for_write.update({'description_manufacturer': description_manufacturer})
        assigned_lifetime = f'Назначенный срок службы {dict_data.get("Назначенный срок службы, лет")}'
        dict_for_write.update({'assigned_lifetime': assigned_lifetime})
        # Наименование поставщика, адрес
        address = f'Место нахождения: Республика Беларусь, #индекс, {dict_data.get("Наименование поставщика, адрес")}'
        dict_for_write.update({'assigned_lifetime': assigned_lifetime})
        dict_for_write.update({'address_manufacturer': address})
        "{{ technical_specifications }} {{ technical_specifications_description}}"
        'по ТУ BY 490850538.004-2019 Лифты электрические'
        tu_specifications = dict_data.get("Нормативные документы в соответствии с которыми изготовлен лифт").split(',')[
            -1]
        technical_specifications = f'Место нахождения: Республика Беларусь, #индекс, {tu_specifications}'

        dict_for_write.update({'technical_specifications': technical_specifications})
        dict_for_write.update({'technical_specifications_description': "Лифты электрические"})

        list_protocols = f'протоколов №№ {dict_data.get("Данные протокола")}'
        dict_for_write.update({'list_protocols': list_protocols})
        # {'Предприятие-изготовитель': '000 «ЛюксЛифт»', 'Модель лифта': 'MODERN',
        #  'Назначение лифта': 'Пассажирский ЛП 1000-1-4 УХЛ4',
        #  'Заводской номер': '0686', 'Месяц и год изготовления': 'декабрь 2022',
        #  'Назначенный срок службы, лет': '25'}
        # Нормативные документы в соответствии с которыми изготовлен лифт

        # dt = 'лифт пассажирский ' + dict_data.get('Назначение лифта').split()[1:].strip()

        return dict_for_write


    def get_render_template_doc(self) -> None:
        doc = DocxTemplate(self.path_template)
        doc.render(context=self.dict_for_write)
        doc.save(filename=self.path_out)

    def update_step_data(self, dict_data):
        self.dict_parse_text.update(dict_data)


    def run(self):
        self.convert_pdf_and_save()
        list_data = []
        data_ocr_list = []
        for index, doc in enumerate(self.list_png_file):
            text = self.get_ocr_image(doc)
            col_token = self.get_col_token(index)
            text_ai = self.get_chain_run(text[:col_token], index=index)
            # self.update_step_data(self.parse_text(text_ai))
            list_data.append(text_ai)
            data_ocr_list.append(text)

        return data_ocr_list, list_data#{self._name :list_data}