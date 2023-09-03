from langchain.prompts import SystemMessagePromptTemplate

from app.utils_parser import ParseDocument

pass_sys = """Из следующего запроса выдели данные следующего формата:
        Предприятие-изготовитель, Модель лифта, назначение лифта Заводской номер, месяц и год изготовления, Назначенный срок службы, лет.
        Ответ должен быть как в примере:
        Предприятие-изготовитель: ОДО "МогилевЛифт"
        Модель лифта: BESTMODEL
        Назначение лифта: Грузовой КЧ 9000-1-4 СЧВ2
        Заводской номер: 0686
        Месяц и год изготовления: декабрь 2020
        Нормативные документы в соответствии с
        которыми изготовлен лифт : ТУ ВY 39080538.004-2022        
        Назначенный срок службы, лет: 19
        конец примера
        """
address_template = """Из следующего запроса выдели данные следующего формата:
            Наименование поставщика, адрес
            Ответ должен быть как в примере:
            Наименование поставщика, адрес: ОДО "МогилевЛифт", город Минск, ул. Руссиянова, 63
            конец примера
            Ничего не придумывай только извлекай текст.
            """


class PassportParse(ParseDocument):
    _name = 'passport'
    system_template = {
        '0': pass_sys,
        '1': address_template,
    }
    list_col_text = [800, 400]

    def get_system_prompts(self, index, **kwargs):
        return SystemMessagePromptTemplate.from_template(self.system_template.get(str(index)))

    def get_col_token(self, index, **kwargs):
        return self.list_col_text[index]