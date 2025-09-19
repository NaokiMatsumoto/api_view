from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional, Tuple

from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import PreparationTemplateForm
from .models import PreparationTask, PreparationTaskTemplate, PreparationTemplate, PersonalSeminar
from .utils import (
    parse_date_input,
    serialize_task,
)


@dataclass
class TaskPayload:
    name: str
    deadline: date


@dataclass
class TaskTemplatePayload:
    name: str
    relative_days_before: int
    default_assignee: str
    default_notes: str


def _validate_task_payload(post_data: QueryDict) -> Tuple[Optional[TaskPayload], Dict[str, str]]:
    name = (post_data.get("name") or "").strip()
    deadline_raw = (post_data.get("deadline") or "").strip()

    errors: Dict[str, str] = {}
    if not name:
        errors["name"] = "タスク名を入力してください"
    elif len(name) > 200:
        errors["name"] = "タスク名は200文字以内で入力してください"

    deadline = parse_date_input(deadline_raw)
    if deadline is None:
        errors["deadline"] = "有効な日付(YYYY-MM-DD)を入力してください"

    if errors:
        return None, errors

    return TaskPayload(name=name, deadline=deadline), {}  # type: ignore[arg-type]


def _validate_task_template_payload(post_data: QueryDict) -> Tuple[Optional[TaskTemplatePayload], Dict[str, str]]:
    name = (post_data.get("name") or "").strip()
    rdb_raw = (post_data.get("relative_days_before") or "").strip()
    assignee = (post_data.get("default_assignee") or "").strip()
    notes = (post_data.get("default_notes") or "").strip()

    errors: Dict[str, str] = {}
    if not name:
        errors["name"] = "タスク名を入力してください"
    elif len(name) > 200:
        errors["name"] = "タスク名は200文字以内で入力してください"

    relative_days_before: Optional[int]
    if rdb_raw == "":
        relative_days_before = None
    else:
        try:
            relative_days_before = int(rdb_raw)
        except ValueError:
            relative_days_before = None
            errors["relative_days_before"] = "整数で入力してください"

    if relative_days_before is None and "relative_days_before" not in errors:
        errors["relative_days_before"] = "相対日を入力してください"

    if errors:
        return None, errors

    return (
        TaskTemplatePayload(
            name=name,
            relative_days_before=relative_days_before,  # type: ignore[arg-type]
            default_assignee=assignee,
            default_notes=notes,
        ),
        {},
    )


class ToggleTaskAjaxView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        try:
            task = PreparationTask.objects.get(pk=pk)
        except PreparationTask.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found"}, status=404)

        task.is_done = not task.is_done
        task.save()

        serialized = serialize_task(task)
        return JsonResponse({
            "success": True,
            "is_done": serialized["is_done"],
            "is_overdue": serialized["is_overdue"],
        })


class UpdateTaskAjaxView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        try:
            task = PreparationTask.objects.get(pk=pk)
        except PreparationTask.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found"}, status=404)

        payload, errors = _validate_task_payload(request.POST)
        if errors or payload is None:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        task.name = payload.name
        task.deadline = payload.deadline
        task.save()

        serialized = serialize_task(task)
        return JsonResponse({"success": True, **serialized})


class CreateTaskAjaxView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, seminar_id: int) -> JsonResponse:
        try:
            seminar = PersonalSeminar.objects.get(pk=seminar_id)
        except PersonalSeminar.DoesNotExist:
            return JsonResponse({"success": False, "error": "Seminar not found"}, status=404)

        payload, errors = _validate_task_payload(request.POST)
        if errors or payload is None:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        task = PreparationTask.objects.create(
            seminar=seminar,
            name=payload.name,
            deadline=payload.deadline,
        )

        serialized = serialize_task(task)
        return JsonResponse({"success": True, **serialized})



class TemplateListView(LoginRequiredMixin, ListView):
    model = PreparationTemplate
    template_name = "preparation/template_list.html"

class TemplateCreateView(LoginRequiredMixin, CreateView):
    model = PreparationTemplate
    form_class = PreparationTemplateForm
    template_name = "preparation/template_form.html"
    success_url = reverse_lazy("seminar:template_list")


class TemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = PreparationTemplate
    form_class = PreparationTemplateForm
    template_name = "preparation/template_form.html"
    success_url = reverse_lazy("seminar:template_list")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        # 子要素（テンプレ内タスク）一覧を表示用に渡す
        obj = getattr(self, "object", None) or self.get_object()
        tasks = PreparationTaskTemplate.objects.filter(template=obj).order_by("id")
        context["tasks"] = tasks
        return context

    def get_success_url(self) -> str:
        return str(reverse_lazy("seminar:template_update", kwargs={"pk": self.kwargs.get("pk")}))


class TemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = PreparationTemplate
    template_name = "preparation/template_confirm_delete.html"
    success_url = reverse_lazy("seminar:template_list")


class TemplateCopyView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        src = PreparationTemplate.objects.get(pk=pk)
        new = PreparationTemplate.objects.create(
            name=f"{src.name}（複製）",
            description=src.description,
        )
        # タスクも複製（順序は撤廃したため単純コピー）
        for t in src.tasks.all().order_by("id"):  # type: ignore[attr-defined]
            PreparationTaskTemplate.objects.create(
                template=new,
                name=t.name,
                relative_days_before=t.relative_days_before,
                default_assignee=t.default_assignee,
                default_notes=t.default_notes,
            )
        return redirect("seminar:template_update", pk=new.pk)


def _when_display(t: PreparationTaskTemplate) -> str:
    if t.relative_days_before is not None:
        # モデル側の書式に合わせて「開催」を接頭
        return f"開催{t.when_display}"
    return "未設定"


# fixed_date を廃止したため不要


class TaskTemplateCreateAjaxView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, template_id: int) -> JsonResponse:
        try:
            template = PreparationTemplate.objects.get(pk=template_id)
        except PreparationTemplate.DoesNotExist:
            return JsonResponse({"success": False, "error": "Template not found"}, status=404)

        payload, errors = _validate_task_template_payload(request.POST)
        if errors or payload is None:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        task_template = PreparationTaskTemplate.objects.create(
            template=template,
            name=payload.name,
            relative_days_before=payload.relative_days_before,
            default_assignee=payload.default_assignee,
            default_notes=payload.default_notes,
        )
        return JsonResponse({
            "success": True,
            "id": task_template.pk,
            "name": task_template.name,
            "relative_days_before": task_template.relative_days_before,
            "default_assignee": task_template.default_assignee,
            "default_notes": task_template.default_notes,
            "when_display": _when_display(task_template),
        })


class TaskTemplateUpdateAjaxView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        try:
            task_template = PreparationTaskTemplate.objects.get(pk=pk)
        except PreparationTaskTemplate.DoesNotExist:
            return JsonResponse({"success": False, "error": "TaskTemplate not found"}, status=404)

        payload, errors = _validate_task_template_payload(request.POST)
        if errors or payload is None:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        task_template.name = payload.name
        task_template.relative_days_before = payload.relative_days_before
        task_template.default_assignee = payload.default_assignee
        task_template.default_notes = payload.default_notes
        task_template.save()

        return JsonResponse({
            "success": True,
            "id": task_template.pk,
            "name": task_template.name,
            "relative_days_before": task_template.relative_days_before,
            "default_assignee": task_template.default_assignee,
            "default_notes": task_template.default_notes,
            "when_display": _when_display(task_template),
        })


class TaskTemplateDeleteAjaxView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        try:
            task_template = PreparationTaskTemplate.objects.get(pk=pk)
        except PreparationTaskTemplate.DoesNotExist:
            return JsonResponse({"success": False, "error": "TaskTemplate not found"}, status=404)
        task_template.delete()
        return JsonResponse({"success": True})
