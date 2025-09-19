from __future__ import annotations

import json
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

from .models import ExternalIntegration


def _parse_bool(v: Any, default: bool = True) -> bool:
    if v is None:
        return default
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "on"}


class ExternalIntegrationCreateAjaxView(LoginRequiredMixin, View):
    """Ajaxで作成"""

    def post(self, request):
        try:
            provider = request.POST.get("provider")
            name = request.POST.get("name")
            is_active = _parse_bool(request.POST.get("is_active"), True)
            cfg_raw = request.POST.get("config", "{}")
            try:
                config: Dict[str, Any] = json.loads(cfg_raw) if isinstance(cfg_raw, str) else {}
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "configはJSON文字列で指定してください"}, status=400)

            if not provider or not name:
                return JsonResponse({"success": False, "error": "providerとnameは必須です"}, status=400)

            obj = ExternalIntegration(provider=provider, name=name, is_active=is_active, config=config)
            # モデル側の clean() を通して検証
            obj.full_clean()
            obj.save()
            return JsonResponse({
                "success": True,
                "id": obj.pk,
                "provider": obj.provider,
                "name": obj.name,
                "is_active": obj.is_active,
                "config": obj.config,
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


class ExternalIntegrationUpdateAjaxView(LoginRequiredMixin, View):
    """Ajaxで更新"""

    def post(self, request, pk: int):
        try:
            obj = ExternalIntegration.objects.get(pk=pk)
        except ExternalIntegration.DoesNotExist:
            return JsonResponse({"success": False, "error": "対象が存在しません"}, status=404)

        try:
            provider = request.POST.get("provider")
            name = request.POST.get("name")
            is_active_val = request.POST.get("is_active")
            cfg_raw = request.POST.get("config")

            if provider is not None:
                obj.provider = provider
            if name is not None:
                obj.name = name
            if is_active_val is not None:
                obj.is_active = _parse_bool(is_active_val, obj.is_active)
            if cfg_raw is not None:
                try:
                    obj.config = json.loads(cfg_raw) if isinstance(cfg_raw, str) else {}
                except json.JSONDecodeError:
                    return JsonResponse({"success": False, "error": "configはJSON文字列で指定してください"}, status=400)

            obj.full_clean()
            obj.save()
            return JsonResponse({
                "success": True,
                "id": obj.pk,
                "provider": obj.provider,
                "name": obj.name,
                "is_active": obj.is_active,
                "config": obj.config,
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


class ExternalIntegrationDeleteAjaxView(LoginRequiredMixin, View):
    """Ajaxで削除"""

    def post(self, request, pk: int):
        try:
            obj = ExternalIntegration.objects.get(pk=pk)
            obj.delete()
            return JsonResponse({"success": True})
        except ExternalIntegration.DoesNotExist:
            return JsonResponse({"success": False, "error": "対象が存在しません"}, status=404)

# Create your views here.


class ExternalIntegrationListView(LoginRequiredMixin, ListView):
    model = ExternalIntegration
    template_name = "account/integration_list.html"
    context_object_name = "object_list"
