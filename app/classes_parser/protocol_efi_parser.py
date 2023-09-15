from langchain.prompts import SystemMessagePromptTemplate

from app.utils_parser import ParseDocument

system_template = '''Из следующего запроса выдели данные следующего формата ПРОТОКОЛ № 06/22-01-П-Л/О21-ЭФИ-12
        Ответ должен быть как в примере:
        Запрос:
        выданных отделом технической диагностики Могилевского областного управления Госпромнадзора МЧС РБ, 
        ПРОТОКОЛ № 06/22-01-П-Л/О21-ЭФИ-12
        тел. 8(0222) 76-51-47, 76-51-53
        Ответ:
        Данные протокола: ПРОТОКОЛ № 06/22-01-П-Л/О21-ЭФИ-12
        конец примера
        Если данных в запросе нет то верни такой ответ:
        Данные протокола: Нет данных о протоколе
        конец примера с неподходящими данными
        Ничего не выдумывай и не записывай лишнего отвечай как в примерах.
'''
title_system = '''Из данного текста нужно выделить каким управлением проведена диагностика и его аттестат акредитации.
Вывести нужно по примеру.
Ничего больше не дописывай.Не пропускай в название управления.
Пример:
Отдел технической диагностики
Гомельское областное управление Госпромнадзора
аттестат аккредитации
NeBY/143 31.534
Конец примера.
'''

human_template = """
    Запрос:
    {question}
    Ответ:
    """
from collections import defaultdict

class ProtocolsEfiParse(ParseDocument):
    _name = 'protocol_efi'
    scale_percent = 600
    system_template = system_template
    col_text = 400
    dict_parse_text = defaultdict(set)
    title_system = title_system
    def get_system_prompts(self, index, temp=None, **kwargs):
        if temp:
            return SystemMessagePromptTemplate.from_template(temp)
        return SystemMessagePromptTemplate.from_template(self.system_template)

    def update_step_data(self, dict_data):    #
        self.dict_parse_text[list(dict_data.keys())[0]].update(list(dict_data.values()))
        # print(self.dict_parse_text)

    def get_col_token(self, index, **kwargs):
        return self.col_text

    def run(self):
        self.convert_pdf_and_save()
        list_data = []
        data_ocr_list = []
        for index, doc in enumerate(self.list_png_file):
            text = self.get_ocr_image(doc)
            col_token = self.get_col_token(index)
            text_ai = self.get_chain_run(text[:col_token], index=index)
            if index == 0:
                text_title = self.get_chain_run(text[:col_token], index=index, temp=self.title_system)
                list_data.append(text_title)
            list_data.append(text_ai)
            data_ocr_list.append(text)

        return data_ocr_list, list_data