from langchain.prompts import SystemMessagePromptTemplate

from app.utils_parser import ParseDocument

ttn_sys = """Из следующего запроса выдели данные:
дата товарной накладной
её номер
Пример:
дата товарной накладной: 25 июля 2019 г.
номер товарной накладной: 2228321
конец примера
Пример:
дата товарной накладной: 05 сентября 2022 г.
номер товарной накладной: Нет данных
конец примера
Если данных подходящего формата нет то так и напиши-НЕТ ДАННЫХ
Ничего не придумывай.
"""


class ProtocolTTNParse(ParseDocument):
    _name ='ttn'
    scale_percent = 600
    system_template = {
        '0': ttn_sys,

    }
    list_col_text = (-1,)

    def get_system_prompts(self, index, **kwargs):
        return SystemMessagePromptTemplate.from_template(self.system_template.get(str(index)))

    def get_col_token(self, index, **kwargs):
        return self.list_col_text[index]