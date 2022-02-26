
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
    ChoiceFilter,
    BooleanFilter,
    ModelChoiceFilter,
    DateFromToRangeFilter,
    DateTimeFilter,
)
from django.contrib.auth.models import User


from tasks.models import Task, History


from rest_framework.serializers import ModelSerializer

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from rest_framework.permissions import IsAuthenticated

from rest_framework import mixins


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class TaskSerializer(ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["id",  "title", "description", "completed", "user", "status"]


STATUS_CHOICES = [
    ("P", "PENDING"),
    ("D", "DONE"),
    ("C", "CANCELLED")
]


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)
    completed = BooleanFilter()
    created_date = DateTimeFilter()


class TaskApiViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HistorySerializer(ModelSerializer):

    class Meta:
        model = History
        fields = "__all__"


class HistoryFilter(FilterSet):
    task = ModelChoiceFilter(queryset=Task.objects.filter(deleted=False))
    timestamp = DateFromToRangeFilter()
    old_status = ChoiceFilter(choices=STATUS_CHOICES)
    new_status = ChoiceFilter(choices=STATUS_CHOICES)


class TaskHistoryApiViewset(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = HistorySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = HistoryFilter

    def get_queryset(self):
        return History.objects.filter(task__user=self.request.user)
