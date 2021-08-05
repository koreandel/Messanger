from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from . import views

app_name = "dialogs"

urlpatterns = [
    path("create_thread/", views.CreateThreadView.as_view(), name="create_thread"),
    path("threads_list/", views.GetThreadListView.as_view(), name="threads_list"),
    path("thread/<int:pk>/", views.GetSingleObjectView.as_view(), name="single_thread"),
    path(
        "update_thread/<int:pk>/",
        views.UpdateThreadView.as_view(),
        name="update_thread",
    ),
    path(
        "messages_list/<int:pk>/",
        views.MessageViewSet.as_view({"get": "list"}),
        name="messages_list",
    ),
    path(
        "edit_message_or_status/<int:pk>/",
        views.MessageViewSet.as_view({"patch": "partial_update"}),
        name="edit_message_or_status",
    ),
    path(
        "create_message/",
        views.MessageViewSet.as_view({"post": "create"}),
        name="create_message",
    ),
    path(
        "delete_message/<int:pk>/",
        views.MessageViewSet.as_view({"delete": "destroy"}),
        name="delete_message",
    ),
    path("api-token-auth/", obtain_jwt_token, name="api-token-auth"),
    path("api-token-refresh/", refresh_jwt_token),
]
