from langchain.prompts import SystemMessagePromptTemplate

from app.utils_parser import ParseDocument

pto_sys = """Из следующего запроса выдели данные:
акт технического освидетельствования лифта перед вводом его в эксплуатацию его номер и дату
кем оформлен акт-каким управлением МЧС
адрес объекта строительства где установлено оборудование(лифт)
Результат должен быть как в примере
Пример результата:
АКТ № 22 то-л «12» июля 2022 г.
Минского областного  управления Госпромнадзора МЧС 
Многоквартирный жилой дом по проспекту Независимости,д.122  в г. Бресте
конец примера
НИКАКУЮ ДРУГУЮ ИНФОРМАЦИЮ НЕ НУЖНО ПИСАТЬ КРОМЕ ТОЙ ТОЙ КАК В ПРИМЕРЕ.
"""


class ActPTOParse(ParseDocument):
    _name = 'act_pto'
    scale_percent = 800
    system_template = {
        '0': pto_sys,

    }
    list_col_text = (1000,)

    def get_system_prompts(self, index, **kwargs):
        return SystemMessagePromptTemplate.from_template(self.system_template.get(str(index)))

    def get_col_token(self, index, **kwargs):
        return self.list_col_text[index]