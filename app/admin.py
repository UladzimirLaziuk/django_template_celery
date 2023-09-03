from django.contrib import admin
from django.contrib.admin import TabularInline

# Register your models here.

from app.models import DocumentsModel, DeclaritionModelFile, TextResultModel

class DocsModelAdmin(admin.ModelAdmin):
    pass



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
    exclude = ('path_folder',)

admin.site.register(DocumentsModel, DocsModelAdmin)
admin.site.register(TextResultModel)
admin.site.register(DeclaritionModelFile, DeclarationModelAdmin)