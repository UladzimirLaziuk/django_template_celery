import os

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from docxtpl import DocxTemplate

from app.classes_parser.act_pto_parser import ActPTOParse
from app.classes_parser.pass_parser import PassportParse
from app.classes_parser.protocol_efi_parser import ProtocolsEfiParse
from app.classes_parser.protocol_pfl_parser import ProtocolPFLParse
from app.classes_parser.sert_parser import SertDocumentParse
from app.classes_parser.ttn_parser import ProtocolTTNParse
from app.map_template import dict_template_promts, all_template
from app.service_utils import get_qa
from app.utils_parser import ConverterPdfToPng
import shutil
import json


# from dotenv import load_dotenv
#
# load_dotenv(dotenv_path='../.env_dev')

class DeclaritionModelFile(models.Model):
    path_folder = models.CharField(max_length=255, blank=True, null=True)

    # url_file = models.CharField(max_length=255, blank=True, null=True)
    def render_document(self):
        pass

    @property
    def url_file(self):
        return f'/static/{self.pk}/{settings.NAME_RESULT_FILE}'

    def __str__(self):
        return f'Declarition - {self.pk}'


class DocumentsModel(models.Model):
    CHOICES = [
        ('ttn', 'Накладная'),
        ('act_pto', 'Акт ПТО'),
        ('protocol_pfl', 'Протокол ПФЛ'),
        ('protocol_efi', 'Протокол ЭФИ'),
        ('sert', 'Сертификат'),
        ('passport', 'Паспорт'),

    ]
    document_type = models.CharField(max_length=15, choices=CHOICES)
    declaration = models.ForeignKey(DeclaritionModelFile, on_delete=models.CASCADE, related_name='documents')
    path_to_file = models.FileField(upload_to='docs_file')
    date_save_file = models.DateTimeField(auto_now=True)

    def get_text(self):
        list_data = self.text_data.values_list('text_result', flat=True)
        result = filter(lambda x: 'Нет данных о протоколе' not in x, list_data)
        return '\n'.join(result)

    def __str__(self):
        return f'{self.document_type}'


class TextResultModel(models.Model):
    docs_model = models.ForeignKey(DocumentsModel, on_delete=models.CASCADE, related_name='text_data')
    text_result = models.TextField(blank=True, null=True)
    text_ocr = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.docs_model.document_type} : {self.text_result[:120]}'


dict_map_parser_class = {
    'ttn': (ProtocolTTNParse, (0,), ('tn_number_date',)),
    'act_pto': (ActPTOParse, (0,), ('act_pto', 'address_object')),
    'protocol_pfl': (ProtocolPFLParse, (0,), ('protocol_pfl',)),
    'protocol_efi': (ProtocolsEfiParse, '__all__', ("protocol_efi", 'efi_title')),
    'sert': (SertDocumentParse, (0,), ('sert', 'code_tnvd_eac')),
    'passport': (
        PassportParse, (1, 6), ('description_elevator', 'description_address_manufacturer', 'assigned_lifetime')),
}


def test_dict(instance):
    question = instance.get_text()
    dict_data = {}
    for key in ('tn_number_date',):
        val = dict_template_promts.get(key)
        qa = get_qa(temp=all_template.format(val))
        dict_data.update({key: qa.run(question=question)})


@receiver(post_save, sender=DocumentsModel)
def set_document_type(sender, instance, created, **kwargs):
    if True:
        src = os.path.join(settings.BASE_DIR, instance.path_to_file.name)
        path_to_file = instance.document_type + '.' + os.path.basename(instance.path_to_file.name).split('.')[-1]
        dst = os.path.join(instance.declaration.path_folder, path_to_file)
        shutil.copy(src, dst)

        parser, index, list_keys = dict_map_parser_class.get(instance.document_type)
        print(f'New deal with pk: {instance.pk} was created.')
        if os.path.basename(dst).split('.')[-1].lower() in ['pdf']:
            conv = ConverterPdfToPng(dirs_name=f'out_png_{instance.document_type}')
            # full_path = os.path.join(settings.BASE_DIR, instance.path_to_file.name)
            obj_parser = parser(path_file=dst, converter=conv, index_tuple=index)
            data_ocr_list, list_data = obj_parser.run()
            for text_ocr, dt in zip(data_ocr_list, list_data):
                TextResultModel.objects.create(text_result=dt, docs_model=instance, text_ocr=text_ocr)
        else:
            raise ValueError('type file no pdf')

        if instance.declaration.documents.count() == 6:
            # instance.declaration.render_document()
            dict_data = {}
            for obj in DocumentsModel.objects.all():
                _, _, list_keys = dict_map_parser_class.get(obj.document_type)
                question = obj.get_text()
                for key in list_keys:
                    val = dict_template_promts.get(key)
                    if key in (
                    'act_pto', 'code_tnvd_eac', 'sert', 'protocol_efi', 'description_address_manufacturer', 'efi_title',
                    'protocol_pfl', 'description_elevator'):
                        promt_doc = val
                    else:
                        promt_doc = all_template.format(val)

                    qa = get_qa(temp=promt_doc)
                    dt_ai = qa.run(question=question)
                    dt_ai = dt_ai.replace('<end>', '').replace('\n', ' ').replace('{', '').replace('}', '').replace(
                        'Конец шаблона.', '').replace('<', '').replace('>', '')
                    dict_data.update({key: dt_ai})
            print(dict_data)
            file_path = "my_dict.json"

            with open(file_path, "w") as json_file:
                json.dump(dict_data, json_file, ensure_ascii=False, indent=4)

            path_folder = os.path.join(settings.BASE_DIR, 'static', str(instance.declaration.pk))

            os.makedirs(path_folder, exist_ok=True)
            file_res_name = os.path.join(path_folder, settings.NAME_RESULT_FILE)
            template_path = os.path.join(settings.BASE_DIR, 'template.docx')
            doc = DocxTemplate(template_path)
            doc.render(context=dict_data)
            doc.save(filename=file_res_name)


@receiver(post_save, sender=DeclaritionModelFile)
def create_document_declaration(sender, instance, created, **kwargs):
    if created:
        path_folder = os.path.join(settings.BASE_DIR, str(instance.pk))
        os.makedirs(path_folder, exist_ok=True)
        instance.path_folder = path_folder
        instance.save()
