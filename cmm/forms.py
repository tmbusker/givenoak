from django.forms import ModelChoiceField, ModelForm


class SimpleModelForm(ModelForm):
    """HTML形式のreadonly項目を定義"""
    html_readonly_fields = ()
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if kwargs.get('instance') is not None:
            for _field_name in self.html_readonly_fields:
                _field = self.fields.get(_field_name)
                if isinstance(_field, ModelChoiceField):
                    _field.disabled = True
                else:
                    self.fields[_field_name].widget.attrs.update({'readonly': 'readonly'})
