from tasks.models import Task
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from datetime import datetime, date

from tasks.models import Report


from task_manager.celery import app


@app.task(name="send_email_report")
def send_email_report():
    print("Starting to process Emails")
    now = datetime.now().strftime('%H:%M')
    today = date.today()
    print("time is now " + now)
    print("date is now ", today)

    for report in Report.objects.filter(reminder_time__lte=now,  disabled=False).filter(~Q(last_sent_day=today)):
        user = User.objects.get(id=report.user.id)
        all_tasks = Task.objects.filter(deleted=False, user=user)

        pending_count = all_tasks.filter(status="P").count()
        done_count = all_tasks.filter(status="D").count()
        cancelled_count = all_tasks.filter(status="C").count()

        content = f"you have | {pending_count} pending tasks |\n" + \
            f" |{done_count} Completed Tasks |\n" + \
            f"and |{cancelled_count} Cancelled tasks|"
        send_mail("Email repost", content,
                  "task@taskmanager.org", [user.email])

        print("Email sent!")
        report.last_sent_day = today
        report.save()
        print(
            f"Completed Processing User {user.id} to user email: {user.email}")


app.conf.beat_schedule = {
    'send-every-10-seconds': {
        'task': 'send_email_report',
        'schedule': 5.0
    },
}
