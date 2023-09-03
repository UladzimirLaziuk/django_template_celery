from langchain.prompts import SystemMessagePromptTemplate

from app.utils_parser import ParseDocument

sert_sys = """Из следующего запроса выдели данные:
Номер сертификата и его код как в примере
Пример:
Запрос:
ЕВРАЗИИСКИИ ЭКОНОМИЧЕСКИЙ с о ю з
СЕРТИФИКАТ СООТВЕТСТВИЯ
№ ЕАЭС RU C-BY.ЛX34.B.00012/23 от 15.05.2023
КОД ТН ВЭД ЕАЭС
3412 11 400 30
СООТВЕТСТВУЕТ ТРЕБОВАНИЯМ
ТР ТС 011/2011 «Безопасность лифтов»
Ответ:
ДАННЫЕ ПО СЕРТИФИКАТУ СООТВЕТСВИЯ: № ЕАЭС RU C-BY.ЛX34.B.00012/23 от 15.05.2023
КОД ТН ВЭД: ЕАЭС 3412 11 400 30
Запрос:
i д ы в + ‚ В. ы
ЕВРАЗИЙСКИЙ ЭКОНОМИЧЕСКИЙ СОЮЗ
СЕРТИФИКАТ СООТВЕТСТВИЯ
№ ЕАЭС BY/105 04.45. 023 03154
Серия ВУ № 0011250
ОРГАН ПО СЕРТИФИКАЦИИ
КОДТН ВЭД ЕАЭС
8445 12 2202
СООТВЕТСТВУЕТ ТРЕБОВАНИЯМ
ТР ТС 011/2011 «Безопасность лифтов»
Ответ:
ДАННЫЕ ПО СЕРТИФИКАТУ СООТВЕТСВИЯ: № ЕАЭС BY/105 04.45. 023 03154
КОД ТНВЭД ЕАЭС: 8445 12 2202
конец примеров
Ничего не придумывай и не дописывай возвращай как в примере.
Запрос:
"""


class SertDocumentParse(ParseDocument):
    _name = 'sert'
    scale_percent = 600
    system_template = {
        '0': sert_sys,

    }
    list_col_text = (-1,)

    def get_system_prompts(self, index, **kwargs):
        return SystemMessagePromptTemplate.from_template(self.system_template.get(str(index)))

    def get_col_token(self, index, **kwargs):
        return self.list_col_text[index]