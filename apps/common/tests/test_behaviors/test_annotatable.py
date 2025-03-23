from unittest import mock

from django.test import TestCase

from apps.common.behaviors.annotatable import Annotatable
from apps.common.models.note import Note
from .test_mixins import BehaviorTestCaseMixin


class AnnotatableModel(Annotatable):
    class Meta:
        app_label = 'test_app'


class AnnotatableTest(BehaviorTestCaseMixin, TestCase):
    @property
    def model(self):
        return AnnotatableModel

    def setUp(self):
        # Create AnnotatableModel object and a Note
        self.obj = self.model.objects.create()
        self.note = Note.objects.create(text="Test note")

    def test_has_notes_property_returns_false_when_no_notes(self):
        # Initially there should be no notes
        self.assertFalse(self.obj.has_notes)

    def test_has_notes_property_returns_true_when_notes_exist(self):
        # Add a note and verify has_notes returns True
        self.obj.notes.add(self.note)
        self.assertTrue(self.obj.has_notes)

    def test_removing_note_updates_has_notes_property(self):
        # Add and then remove a note to verify has_notes returns False again
        self.obj.notes.add(self.note)
        self.assertTrue(self.obj.has_notes)
        
        self.obj.notes.remove(self.note)
        self.assertFalse(self.obj.has_notes)