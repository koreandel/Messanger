from django.contrib import admin
from . import models


@admin.register(models.Message)
class MassagesAdmin(admin.ModelAdmin):

    raw_id_fields = [
        "thread",
        "sender",
    ]
    list_display = [
        "id",
        "text",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "text",
        "created_at",
        "updated_at",
    ]


@admin.register(models.Thread)
class ThreadAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "participants",
    ]
    list_display = [
        "id",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
    ]
