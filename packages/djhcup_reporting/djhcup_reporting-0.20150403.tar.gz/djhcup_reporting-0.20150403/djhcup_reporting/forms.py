from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _


from djhcup_reporting.models import DataSet


class PublicDataSetForm(ModelForm):
    class Meta:
        model = DataSet
        fields = ['name', 'description']#, 'void']
        help_texts = {
            #'name': _('A short name or label. This is purely cosmetic, but can be helpful for sifting through your requests.'),
            #'description': _('A more verbose description. Use this for notes or a more full label for the DataSet.'),
            #'void': _('Check this box to indicate that the DataSet is no longer needed and can be safely deleted by the system. Be careful, as the data will be unrecoverable once the system has deleted it. If you mark a DataSet as Void before it has finished extracting, the extraction will be canceled.')
        }