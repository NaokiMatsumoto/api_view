from django import forms
from .models import PreparationTemplate, NotificationSetting


class PreparationTemplateForm(forms.ModelForm):
    class Meta:
        model = PreparationTemplate
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500",
                "placeholder": "例: 新規セミナーテンプレート",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500",
                "placeholder": "テンプレートの用途や注意点を記載（任意）",
                "rows": 4,
            }),
        }


class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ["days_before", "integrations"]
        widgets = {
            "days_before": forms.NumberInput(
                attrs={
                    "class": "w-40 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-300",
                    "min": 0,
                    "step": 1,
                }
            ),
            "integrations": forms.SelectMultiple(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-300",
                    "size": 6,
                }
            ),
        }
