from django.contrib import admin
from tasksoftheday.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_text', 'is_done', 'created_date', 'due_date')

# Register your models here.
admin.site.register(Task, TaskAdmin)