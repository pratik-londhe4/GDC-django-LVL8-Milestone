
from xmlrpc.client import boolean
from django.db import models

from django.contrib.auth.models import User

from django.db.models.signals import pre_save
from django.dispatch import receiver

STATUS_CHOICES = [
    ("P", "PENDING"),
    ("D", "DONE"),
    ("C", "CANCELLED")
]


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    priority = models.SmallIntegerField(default=-1)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return self.title


class History(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    old_status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, null=True)
    new_status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, null=True)


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    reminder_time = models.TimeField()
    last_sent_day = models.DateField(null=True, default=None, blank=True)
    disabled = models.BooleanField(default=True)


@receiver(pre_save, sender=Task)
def task_update_trigger(sender, instance, **kwargs):
    new_task = instance
    id = new_task.id
    try:

        old_task = Task.objects.get(pk=id)
        if(new_task.status != old_task.status):
            History.objects.create(
                task=instance, old_status=old_task.status, new_status=new_task.status)

    except:
        print("no task found")
