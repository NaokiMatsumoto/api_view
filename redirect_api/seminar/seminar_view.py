from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Tuple

from django.forms import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    PreparationTask,
    PreparationTemplate,
    PersonalSeminar,
    PersonalSeminarDate,
)
from .utils import create_tasks_from_template, describe_relative_days, parse_date_input


class PersonalSeminarListView(LoginRequiredMixin, ListView):
    model = PersonalSeminar
    template_name = "seminar/personal_seminar_list.html"


class PersonalSeminarDetailView(LoginRequiredMixin, DetailView):
    model = PersonalSeminar
    template_name = "seminar/personal_seminar_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        seminar: PersonalSeminar = context["object"]

        tasks: List[PreparationTask] = list(
            PreparationTask.objects.filter(seminar=seminar).order_by("deadline", "id")
        )

        task_grouped_by_dates: Dict[date, List[PreparationTask]] = defaultdict(list)
        for task in tasks:
            task_grouped_by_dates[task.deadline].append(task)

        date_summaries: Dict[date, Dict[str, int]] = {}
        for task_date, related_tasks in task_grouped_by_dates.items():
            total = len(related_tasks)
            completed = sum(1 for item in related_tasks if item.is_done)
            overdue = sum(1 for item in related_tasks if item.is_overdue)
            percent = round(completed * 100 / total) if total else 0
            date_summaries[task_date] = {
                "total": total,
                "completed": completed,
                "overdue": overdue,
                "percent": percent,
            }

        overdue_count = sum(1 for task in tasks if task.is_overdue)
        today = date.today()
        sorted_grouped_items: List[Tuple[date, List[PreparationTask]]] = sorted(
            task_grouped_by_dates.items(), key=lambda kv: kv[0]
        )

        tasks_grouped = []
        calendar_events: List[Dict[str, Any]] = []
        for grouped_date, related_tasks in sorted_grouped_items:
            ordered_tasks = sorted(related_tasks, key=lambda item: (item.deadline, item.id))  # type: ignore[attr-defined]
            summary = date_summaries[grouped_date]
            tasks_grouped.append(
                {
                    "date": grouped_date,
                    "tasks": ordered_tasks,
                    "summary": summary,
                    "date_key": grouped_date.isoformat(),
                    "relative_text": describe_relative_days(grouped_date, today),
                }
            )

            calendar_events.append(
                {
                    "date": grouped_date.isoformat(),
                    "total": summary["total"],
                    "completed": summary["completed"],
                    "overdue": summary["overdue"],
                    "tasks": [
                        {
                            "id": task.id,  # type: ignore[attr-defined]
                            "name": task.name,
                            "isDone": task.is_done,
                            "isOverdue": task.is_overdue,
                            "deadline": task.deadline.isoformat(),
                        }
                        for task in ordered_tasks
                    ],
                }
            )

        context.update(
            {
                "tasks_by_date": {k: v for k, v in sorted_grouped_items},
                "tasks_grouped": tasks_grouped,
                "date_summaries": date_summaries,
                "overdue_count": overdue_count,
                "pending_count": max(
                    0,
                    seminar.total_tasks_count
                    - seminar.completed_tasks_count
                    - overdue_count,
                ),
                "calendar_events": calendar_events,
            }
        )
        return context


class PersonalSeminarFormMixin:
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)  # type: ignore[call-arg]
        context["preparation_templates"] = PreparationTemplate.objects.all()
        return context

    def validate_posted_dates(self) -> Tuple[List[date], List[str]]:
        posted = [value for value in self.request.POST.getlist("dates[]") if value]  # type: ignore[attr-defined]
        errors: List[str] = []
        valid_dates: List[date] = []
        seen: set[date] = set()
        today = date.today()

        for raw in posted:
            parsed = parse_date_input(raw)
            if parsed is None:
                errors.append(f"不正な日付形式です: {raw}")
                continue
            if parsed < today:
                errors.append(f"過去日付は指定できません: {parsed}")
                continue
            if parsed in seen:
                errors.append(f"重複した日付があります: {parsed}")
                continue
            seen.add(parsed)
            valid_dates.append(parsed)

        return valid_dates, errors

    def handle_template_tasks(self, seminar: PersonalSeminar) -> None:
        template_id = self.request.POST.get("template_id")  # type: ignore[attr-defined]
        if not template_id:
            return
        try:
            template = PreparationTemplate.objects.get(id=template_id)
        except PreparationTemplate.DoesNotExist:
            return
        create_tasks_from_template(seminar, template)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        valid_dates, errors = self.validate_posted_dates()
        if errors:
            for message in errors:
                form.add_error(None, message)
            context = self.get_context_data(form=form)
            return self.render_to_response(context)  # type: ignore[attr-defined]

        self.object = form.save()

        is_update = isinstance(self, UpdateView)
        if is_update:
            self.object.dates.all().delete()
        for valid_date in valid_dates:
            PersonalSeminarDate.objects.create(seminar=self.object, date=valid_date)

        if not is_update:
            self.handle_template_tasks(self.object)

        return HttpResponseRedirect(self.get_success_url())  # type: ignore[attr-defined]


class PersonalSeminarCreateView(LoginRequiredMixin, PersonalSeminarFormMixin, CreateView):
    model = PersonalSeminar
    fields = ["title", "description", "location", "capacity", "price", "format"]
    template_name = "seminar/personal_seminar_form.html"
    success_url = reverse_lazy("seminar:seminar_list")


class PersonalSeminarUpdateView(LoginRequiredMixin, PersonalSeminarFormMixin, UpdateView):
    model = PersonalSeminar
    fields = ["title", "description", "location", "capacity", "price", "format"]
    template_name = "seminar/personal_seminar_form.html"
    success_url = reverse_lazy("seminar:seminar_list")


class PersonalSeminarCopyView(PersonalSeminarCreateView):
    def get_initial(self) -> Dict[str, Any]:
        initial: Dict[str, Any] = super().get_initial()
        pk_value = int(self.kwargs["pk"])
        original_seminar = PersonalSeminar.objects.get(pk=pk_value)
        initial.update(
            {
                "title": f"{original_seminar.title}（複製）",
                "description": original_seminar.description,
                "location": original_seminar.location,
                "capacity": original_seminar.capacity,
                "price": original_seminar.price,
                "format": original_seminar.format,
            }
        )
        return initial
