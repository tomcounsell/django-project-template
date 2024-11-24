from django.dispatch import receiver
from django_q.signals import post_execute


@receiver(post_execute)
def create_task_record(sender, task, **kwargs):
    TaskRecord.objects.update_or_create(
        task=task,
        defaults={
            "task_name": task.name or task.func,
            "status": "Success" if task.success else "Failed",
            "started_at": task.started,
            "completed_at": task.stopped,
            "result": str(task.result) if task.result else None,
            "error": str(task.result) if not task.success else None,
        },
    )
