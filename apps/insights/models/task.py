from django_q.models import Task


class TaskRecord(models.Model):
    """
    Model to record additional information about tasks executed via Django-Q2.
    """

    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    summary = models.ForeignKey(
        Summary, null=True, blank=True, on_delete=models.SET_NULL
    )
    comparison = models.ForeignKey(
        Comparison, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"Task Record for Task ID: {self.task.id}"

    class Meta:
        verbose_name = "Task Record"
        verbose_name_plural = "Task Records"
