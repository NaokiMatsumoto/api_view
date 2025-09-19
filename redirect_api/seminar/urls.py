from django.urls import path
from .seminar_view import (
    PersonalSeminarListView,
    PersonalSeminarDetailView,
    PersonalSeminarCreateView,
    PersonalSeminarUpdateView,
    PersonalSeminarCopyView,
)
from .preparation_view import (
    ToggleTaskAjaxView,
    UpdateTaskAjaxView,
    CreateTaskAjaxView,
    TemplateListView,
    TemplateCreateView,
    TemplateUpdateView,
    TemplateDeleteView,
    TemplateCopyView,
    TaskTemplateCreateAjaxView,
    TaskTemplateUpdateAjaxView,
    TaskTemplateDeleteAjaxView,
)
from .notification_view import (
    NotificationSettingListView,
    NotificationSettingCreateView,
    NotificationSettingUpdateAjaxView,
    NotificationSettingDeleteAjaxView,
)

app_name = "seminar"

urlpatterns = [
    path("", PersonalSeminarListView.as_view(), name="seminar_list"),
    path("<int:pk>/", PersonalSeminarDetailView.as_view(), name="seminar_detail"),
    path("create/", PersonalSeminarCreateView.as_view(), name="seminar_create"),
    path("<int:pk>/update/", PersonalSeminarUpdateView.as_view(), name="seminar_update"),
    path("<int:pk>/copy/", PersonalSeminarCopyView.as_view(), name="copy"),
    path("<int:seminar_id>/tasks/create-ajax/", CreateTaskAjaxView.as_view(), name="create_task_ajax"),
    path("tasks/<int:pk>/toggle-ajax/", ToggleTaskAjaxView.as_view(), name="toggle_task_ajax"),
    path("tasks/<int:pk>/update-ajax/", UpdateTaskAjaxView.as_view(), name="update_task_ajax"),
    path("templates/", TemplateListView.as_view(), name="template_list"),
    path("templates/create/", TemplateCreateView.as_view(), name="template_create"),
    path("templates/<int:pk>/update/", TemplateUpdateView.as_view(), name="template_update"),
    path("templates/<int:pk>/delete/", TemplateDeleteView.as_view(), name="template_delete"),
    path("templates/<int:pk>/copy/", TemplateCopyView.as_view(), name="template_copy"),
    path("templates/<int:template_id>/tasks/create-ajax/", TaskTemplateCreateAjaxView.as_view(), name="task_template_create_ajax"),
    path("templates/tasks/<int:pk>/update-ajax/", TaskTemplateUpdateAjaxView.as_view(), name="task_template_update_ajax"),
    path("templates/tasks/<int:pk>/delete-ajax/", TaskTemplateDeleteAjaxView.as_view(), name="task_template_delete_ajax"),
    path("notifications/", NotificationSettingListView.as_view(), name="notification_list"),
    path("notifications/create/", NotificationSettingCreateView.as_view(), name="notification_create"),
    path("notifications/<int:pk>/update/", NotificationSettingUpdateAjaxView.as_view(), name="notification_update"),
    path("notifications/<int:pk>/delete/", NotificationSettingDeleteAjaxView.as_view(), name="notification_delete"),
]
