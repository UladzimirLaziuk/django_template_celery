from django.conf import settings
from django.contrib import admin
from django.contrib.admin import TabularInline, StackedInline
from django.utils.html import format_html

# Register your models here.

from app.models import DocumentsModel, DeclaritionModelFile, TextResultModel


class TextResultInline(TabularInline):
    model = TextResultModel
    extra = 0
    # max_num = 6

class DocsModelAdmin(admin.ModelAdmin):
    inlines = [TextResultInline, ]



class DocsModelInline(TabularInline):
    model = DocumentsModel
    extra = 6
    max_num = 6


class DeclarationModelAdmin(admin.ModelAdmin):
    inlines = [DocsModelInline, ]
    # filter_dict = {'resolution_value': 'is_admin_customer'}
    # fields = ('email', 'password', 'first_name', 'last_name', 'phone', 'name_company', 'user_position', 'discount')
    # list_display = ("email", "first_name", "name_company", "phone", "user_position", "discount")
    # list_filter = ("name_company", "discount")
    exclude = ('path_folder','url_file')
    list_display = ('my_model', 'my_url_field')


    def my_model(self, obj):
        return obj

    def my_url_field(self, obj):
        if obj.url_file:
            return format_html('<a target="_blank" href="%s">%s</a>' % (obj.url_file, 'down url'))
        return '-'

    my_url_field.allow_tags = True
    my_url_field.short_description = 'url file'

admin.site.register(DocumentsModel, DocsModelAdmin)
admin.site.register(DeclaritionModelFile, DeclarationModelAdmin)