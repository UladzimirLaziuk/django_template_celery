from langchain.prompts import SystemMessagePromptTemplate

from app.utils_parser import ParseDocument

ttn_sys = """Из следующего запроса выдели данные:
дата товарной накладной
её номер
Пример:
товарная накладная № 23434543 от 15 февраля 2019 г.
конец примера
"""


class ProtocolTTNParse(ParseDocument):
    _name ='ttn'
    scale_percent = 600
    system_template = {
        '0': ttn_sys,

    }
    list_col_text = (600,)

    def get_system_prompts(self, index, **kwargs):
        return SystemMessagePromptTemplate.from_template(self.system_template.get(str(index)))

    def get_col_token(self, index, **kwargs):
        return self.list_col_text[index]