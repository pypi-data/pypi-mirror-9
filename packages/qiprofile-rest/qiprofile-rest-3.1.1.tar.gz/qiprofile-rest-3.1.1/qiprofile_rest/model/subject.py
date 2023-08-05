"""
The qiprofile subject Mongodb data model.
"""

import re
import mongoengine
from mongoengine import (fields, signals)
from .. import choices
from .imaging import (ScanSet, Session)
from .clinical import (Treatment, Encounter)


class Subject(mongoengine.Document):
    """
    The patient.
    """

    RACE_CHOICES = [('White', 'White'),
                    ('Black', 'Black or African American'),
                    ('Asian', 'Asian'),
                    ('AIAN', 'American Indian or Alaska Native'),
                    ('NHOPI', 'Native Hawaiian or Other Pacific Islander')]
    """The standard FDA race categories, in order of US incidence."""

    ETHNICITY_CHOICES = [('Hispanic' , 'Hispanic or Latino'),
                         ('Non-Hispanic' , 'Not Hispanic or Latino')]
    """The standard FDA ethnicity categories."""

    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]

    meta = dict(collection='qiprofile_subject')

    project = fields.StringField(default='QIN')

    collection = fields.StringField(required=True)

    number = fields.IntField(required=True)

    birth_date = fields.DateTimeField()

    races = fields.ListField(
        fields.StringField(
            max_length=choices.max_length(RACE_CHOICES),
            choices=RACE_CHOICES))

    ethnicity = fields.StringField(
        max_length=choices.max_length(ETHNICITY_CHOICES),
        choices=ETHNICITY_CHOICES)

    gender = fields.StringField(
        max_length=choices.max_length(GENDER_CHOICES),
        choices=GENDER_CHOICES)

    # The weight in kilograms.
    weight = fields.IntField()

    # The {scan type: ScanSet} dictionary.
    scan_sets = fields.DictField(field=fields.EmbeddedDocumentField(ScanSet))

    sessions = fields.ListField(field=fields.EmbeddedDocumentField(Session))

    treatments = fields.ListField(field=fields.EmbeddedDocumentField(Treatment))

    encounters = fields.ListField(field=fields.EmbeddedDocumentField(Encounter))

    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this Subject's sessions."""

        for sess in self.sessions:
            sess.delete()

    def __str__(self):
        return ("%s %s Subject %d" %
                (self.project, self.collection, self.number))

signals.pre_delete.connect(Subject.pre_delete, sender=Subject)
