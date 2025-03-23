from datetime import datetime, timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from ...models.background_job import BackgroundJob


# Create a concrete class for testing since BackgroundJob is abstract
class ConcreteBackgroundJob(BackgroundJob):
    class Meta:
        app_label = 'common'


class BackgroundJobTest(TestCase):
    def setUp(self):
        # Set up in-memory database for ConcreteBackgroundJob
        from django.db import connection
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(ConcreteBackgroundJob)
    
    def test_model_fields(self):
        """Test the basic fields of the BackgroundJob model"""
        job = ConcreteBackgroundJob.objects.create(
            name="Test Job",
            description="Test description"
        )
        
        self.assertEqual(job.name, "Test Job")
        self.assertEqual(job.description, "Test description")
        self.assertIsNotNone(job.start_run_at)
        self.assertIsNone(job.end_run_at)
        self.assertFalse(job.has_errors)
        self.assertTrue(job.is_failed)  # Default is True
        self.assertEqual(job.logs, [])
    
    def test_execution_time_humanized_with_end_time(self):
        """Test the execution_time_humanized property with an end time"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=2, minutes=30, seconds=15)
        
        job = ConcreteBackgroundJob.objects.create(
            name="Test Job",
            start_run_at=start_time,
            end_run_at=end_time
        )
        
        self.assertEqual(job.execution_time_humanized, "2 hr, 30 min, 15 s")
    
    def test_execution_time_humanized_without_end_time(self):
        """Test the execution_time_humanized property without an end time"""
        start_time = timezone.now()
        
        with mock.patch('apps.common.models.background_job.datetime') as mock_datetime:
            # Set today to be 1 hour, 15 minutes and 30 seconds after start_time
            mock_datetime.today.return_value = start_time + timedelta(hours=1, minutes=15, seconds=30)
            
            job = ConcreteBackgroundJob.objects.create(
                name="Test Job",
                start_run_at=start_time,
                end_run_at=None
            )
            
            self.assertEqual(job.execution_time_humanized, "1 hr, 15 min, 30 s")
    
    def test_execution_time_humanized_minutes_only(self):
        """Test the execution_time_humanized property with only minutes and seconds"""
        start_time = timezone.now()
        end_time = start_time + timedelta(minutes=15, seconds=30)
        
        job = ConcreteBackgroundJob.objects.create(
            name="Test Job",
            start_run_at=start_time,
            end_run_at=end_time
        )
        
        self.assertEqual(job.execution_time_humanized, "15 min, 30 s")
    
    def test_execution_time_humanized_seconds_only(self):
        """Test the execution_time_humanized property with only seconds"""
        start_time = timezone.now()
        end_time = start_time + timedelta(seconds=45)
        
        job = ConcreteBackgroundJob.objects.create(
            name="Test Job",
            start_run_at=start_time,
            end_run_at=end_time
        )
        
        self.assertEqual(job.execution_time_humanized, "45 s")
    
    def test_execution_time_humanized_without_start_time(self):
        """Test the execution_time_humanized property without a start time"""
        job = ConcreteBackgroundJob.objects.create(
            name="Test Job",
            start_run_at=None
        )
        
        self.assertEqual(job.execution_time_humanized, "")