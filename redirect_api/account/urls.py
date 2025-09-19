from django.urls import path

from .views import (
    ExternalIntegrationListView,
    ExternalIntegrationCreateAjaxView,
    ExternalIntegrationUpdateAjaxView,
    ExternalIntegrationDeleteAjaxView,
)

app_name = "account"

urlpatterns = [
    path("integrations/", ExternalIntegrationListView.as_view(), name="integration_list"),
    path("integrations/create/", ExternalIntegrationCreateAjaxView.as_view(), name="integration_create"),
    path("integrations/<int:pk>/update/", ExternalIntegrationUpdateAjaxView.as_view(), name="integration_update"),
    path("integrations/<int:pk>/delete/", ExternalIntegrationDeleteAjaxView.as_view(), name="integration_delete"),
]
