
from re import template
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.core.exceptions import ValidationError

from tasks.models import Task

from .forms import TaskCreateForm, EmailReportForm


def get_pending_tasks(user, priority=-1):
    if priority == -1:
        return Task.objects.filter(deleted=False, completed=False, user=user)
    return Task.objects.filter(deleted=False, completed=False, user=user, priority=priority)


def get_completed_tasks(user):
    return Task.objects.filter(deleted=False, completed=True, user=user)


def get_all_tasks(user):
    return Task.objects.filter(deleted=False,  user=user)


def cascade_Tasks(user, priority):
    tasks_to_update = []
    all_tasks = Task.objects.select_for_update().filter(deleted=False, completed=False,
                                                        user=user, priority__gte=priority).order_by('priority')
    if(all_tasks.filter(priority=priority)).exists():

        with transaction.atomic():
            for task in all_tasks:
                if task.priority == priority:
                    task.priority += 1
                    priority += 1
                    tasks_to_update.append(task)
            Task.objects.bulk_update(tasks_to_update, ['priority'])


def save_Task(self, form):
    self.object = form.save()
    self.object.user = self.request.user
    self.object.save()


class AuthorizedTasksView(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False).filter(completed=False, user=self.request.user)


class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        priority = form.cleaned_data["priority"]
        user = self.request.user
        cascade_Tasks(user, priority)
        save_Task(self, form)
        return HttpResponseRedirect("/tasks")


class GenereicPendingTaskView(AuthorizedTasksView,  ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 3

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        tasks = get_pending_tasks(self.request.user)
        if search_item:
            tasks = tasks.filter(title__icontains=search_item)

        return tasks


class GenereicAllTaskView(AuthorizedTasksView,  ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "all_tasks.html"
    context_object_name = "tasks"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        return {'tasks': get_all_tasks(self.request.user),
                'all': get_all_tasks(self.request.user).count(),
                'completed': get_completed_tasks(self.request.user).count()}


class GenereicCompletedTaskView(AuthorizedTasksView,  ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "completed_tasks.html"
    context_object_name = "tasks"
    paginate_by = 3

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        tasks = get_completed_tasks(self.request.user)
        if search_item:
            tasks = tasks.filter(title__icontains=search_item)

        return tasks


class GenericTaskUpdateView(AuthorizedTasksView,  UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

    def form_valid(self, form):
        priority = form.cleaned_data["priority"]
        user = self.request.user

        if('priority' in form.changed_data):
            cascade_Tasks(user, priority)

        if('status' in form.changed_data):
            print("do stuff")

        save_Task(self, form)

        return HttpResponseRedirect("/tasks")


class GenericTaskDetailView(AuthorizedTasksView, DetailView):
    model = Task
    template_name = "task_detail.html"


class GenericTaskDeleteView(AuthorizedTasksView, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


def complete_Task(req, pk):
    Task.objects.filter(id=pk).update(completed=True)
    return HttpResponseRedirect("/tasks")


class GenericTaskEmailReportView(LoginRequiredMixin, CreateView):
    form_class = EmailReportForm
    template_name = "set_reminder.html"
    success_url = "/tasks"

    def form_valid(self, form):
        user = self.request.user
        self.object = form.save()
        self.object.user = user
        self.object.save()
        return HttpResponseRedirect("/tasks")
