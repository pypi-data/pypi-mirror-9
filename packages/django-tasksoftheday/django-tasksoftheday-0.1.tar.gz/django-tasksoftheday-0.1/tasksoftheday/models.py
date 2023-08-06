from django.db import models


class Task(models.Model):
    task_text = models.CharField(max_length=500)
    is_done = models.BooleanField("have we already finished the task?")
    created_date = models.DateTimeField("day the task was created")
    due_date = models.DateTimeField("day the task is due")

    def __str__(self):
        return self.task_text
        