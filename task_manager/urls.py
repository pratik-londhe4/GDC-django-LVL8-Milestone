
from rest_framework.routers import SimpleRouter
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path

from tasks.apiviews import TaskApiViewSet, TaskHistoryApiViewset


def indexRedirect(req):
    return HttpResponseRedirect("tasks/")


router = SimpleRouter()

router.register("api/tasks", TaskApiViewSet, basename='tasks')
router.register("api/history", TaskHistoryApiViewset, basename='history')


urlpatterns = [
    path("admin/", admin.site.urls),
    path('user/', include("user.urls")),
    path('tasks/', include("tasks.urls")),
    path('', indexRedirect)
] + router.urls
