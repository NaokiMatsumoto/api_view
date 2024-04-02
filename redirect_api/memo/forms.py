from django import forms
from .models import Memo

class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
      super(MemoForm, self).__init__(*args, **kwargs)
      self.fields["content"].required = False