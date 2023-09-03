from langchain.prompts import SystemMessagePromptTemplate

from app.utils_parser import ParseDocument

pfl_sys = """Из следующего запроса выдели данные:
Протокол проверки функционирования лифта
дата протокола 
место подписания
организация которая провела проверку
её название и её вид
"""


class ProtocolPFLParse(ParseDocument):
    _name = 'protocol_pfl'
    scale_percent = 300
    system_template = {
        '0': pfl_sys,

    }
    list_col_text = (1000,)

    def get_system_prompts(self, index, **kwargs):
        return SystemMessagePromptTemplate.from_template(self.system_template.get(str(index)))

    def get_col_token(self, index, **kwargs):
        return self.list_col_text[index]