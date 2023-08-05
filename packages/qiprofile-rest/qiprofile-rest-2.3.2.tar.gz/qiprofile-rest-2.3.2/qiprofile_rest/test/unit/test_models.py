from nose.tools import (assert_true, assert_false, assert_equal, assert_raises)
from datetime import datetime
import pytz
from mongoengine import (connect, ValidationError)
from mongoengine.connection import get_db
from qiprofile_rest.models import *

class TestModel(object):
    def setup(self):
        connect(db='qiprofile_test')
        self.db = get_db()
        self.db.connection.drop_database('qiprofile_test')
    
    def tearDown(self):
      self.db.connection.drop_database('qiprofile_test')

    def test_subject(self):
        subject = Subject(number=1)
        assert_equal(subject.project, 'QIN',
                     "Subject project is not set to the default -"
                     " expected %s, found %s" % ('QIN', subject.project))
        
        # The subject must have a collection.
        with assert_raises(ValidationError):
            subject.save()
        
        subject.collection='Breast'
        subject.save()

    def test_race(self):
        detail = SubjectDetail(collection='Breast', number=1)
        detail.races = ['White', 'Black', 'Asian', 'AIAN', 'NHOPI']
        detail.save()

        detail = SubjectDetail(collection='Breast', number=1)
        detail.races = ['Invalid']
        with assert_raises(ValidationError):
            detail.save()

        # Races must be a list.
        detail.races = 'White'
        with assert_raises(ValidationError):
            detail.save()

    def test_ethnicity(self):
        detail = SubjectDetail(collection='Breast', number=1)
        detail.ethnicity = 'Non-Hispanic'
        detail.save()

        detail.ethnicity = 'Invalid'
        with assert_raises(ValidationError):
            detail.save()

    def test_encounter(self):
        detail = SubjectDetail(collection='Breast', number=1)
        date = datetime(2013, 1, 4, tzinfo=pytz.utc)
        encounter = Encounter(encounter_type='Biopsy', date=date)
        detail.encounters = [encounter]
        # The encounter outcome is optional.
        detail.save()
        # Add the evaluation.
        evaluation = Evaluation()
        outcome = TNM()
        evaluation.outcomes = [outcome]
        encounter.evaluation = evaluation
        detail.save()

    def test_tnm_size(self):
        for value in ['T1', 'Tx', 'cT4', 'T1b', 'cT2a']:
            size = TNM.Size.parse(value)
            assert_equal(str(size), value, "TNM parse incorrect -"
                                           " expected %s, found %s"
                                           % (value, str(size)))

    def test_session(self):
        detail = SubjectDetail(collection='Breast', number=1)
        date = datetime(2013, 1, 4, tzinfo=pytz.utc)
        session = Session(number=1, acquisition_date=date)
        detail.sessions = [session]
        detail.save()

    def test_modeling(self):
        # TODO - add modeling test case.
        pass

    def test_series(self):
        detail = SessionDetail()
        detail.bolus_arrival_index = 4
        # The bolus arrival index must refer to a series.
        with assert_raises(ValidationError):
            detail.save()
        
        # Add the series.
        detail.series = [Series(number=7+i) for i in range(0, 32)]
        # The detail is now valid.
        detail.save()

        # The bolus arrival index does not refer to a series.
        detail.bolus_arrival_index = 32
        with assert_raises(ValidationError):
            detail.save()

if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
