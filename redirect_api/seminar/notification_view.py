from django.views.generic import ListView, CreateView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import NotificationSetting
from account.models import ExternalIntegration
from .forms import NotificationSettingForm


class NotificationSettingListView(LoginRequiredMixin, ListView):
    model = NotificationSetting
    template_name = "notification/notification_list.html"
    context_object_name = "settings"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["integrations"] = ExternalIntegration.objects.filter(is_active=True).order_by("provider", "name")
        return ctx


class NotificationSettingCreateView(LoginRequiredMixin, CreateView):
    model = NotificationSetting
    form_class = NotificationSettingForm
    template_name = "notification/notification_form.html"
    success_url = reverse_lazy("seminar:notification_list")


class NotificationSettingUpdateAjaxView(LoginRequiredMixin, View):
    """Ajaxで更新"""

    def post(self, request, pk):
        try:
            obj = NotificationSetting.objects.get(pk=pk)
            # days_before の更新
            new_days = request.POST.get("days_before")
            if new_days is not None:
                obj.days_before = int(new_days)
                obj.save()

            # integrations (M2M) の更新: integration_ids="1,2,3"
            ids_csv = request.POST.get("integration_ids")
            if ids_csv is not None:
                try:
                    ids = [int(x) for x in ids_csv.split(",") if x.strip()]
                except ValueError:
                    return JsonResponse({"success": False, "error": "integration_idsはカンマ区切りの数値IDで指定してください"}, status=400)
                # 指定されたIDに置き換え（存在しないIDは無視）
                qs = ExternalIntegration.objects.filter(pk__in=ids, is_active=True)
                obj.integrations.set(qs)
                obj.save()

            return JsonResponse({"success": True, "days_before": obj.days_before})
        except NotificationSetting.DoesNotExist:
            return JsonResponse({"success": False, "error": "対象が存在しません"}, status=404)


class NotificationSettingDeleteAjaxView(LoginRequiredMixin, View):
    """Ajaxで削除"""

    def post(self, request, pk):
        try:
            obj = NotificationSetting.objects.get(pk=pk)
            obj.delete()
            return JsonResponse({"success": True})
        except NotificationSetting.DoesNotExist:
            return JsonResponse({"success": False, "error": "対象が存在しません"}, status=404)
