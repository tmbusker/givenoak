from msilib.schema import Media
from django.contrib import admin
from django.forms import ChoiceField
from cmm.admin.base import CommonBaseTableAminMixin
from cmm.forms import SimpleModelForm
from jinji.models.ido.dkido import Dkido
from mst.models.ido.ido_type import IdoType


class DkidoForm(SimpleModelForm):
    """異動情報入力フォーム"""
    ido_type = ChoiceField(choices=IdoType.objects.all().values_list('code', 'name'))

    class Meta:
        """medel info"""
        model = Dkido
        fields = ['ido_type', 'ido_syumoku', 'cshainno', 'cnamekna', 'cnameknj']
        
    class Media:
        js = ('jinji/js/select_ido_type.js',)
    
class DkidoAdmin(CommonBaseTableAminMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    form = DkidoForm

    fields = [('ido_type', 'ido_syumoku'), ('cshainno', 'cnamekna', 'cnameknj'),]
    list_display = ('ido_syumoku', 'cshainno', 'cnameknj',)

    list_display_links = ['ido_syumoku']
    list_per_page = 100
    
