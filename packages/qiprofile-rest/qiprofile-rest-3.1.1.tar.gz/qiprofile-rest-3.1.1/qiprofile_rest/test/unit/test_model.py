from nose.tools import (assert_true, assert_false, assert_equal, assert_raises)
from datetime import datetime
import pytz
from mongoengine import (connect, ValidationError)
from mongoengine.connection import get_db
from qiprofile_rest.model.subject import Subject
from qiprofile_rest.model.imaging import (Session, SessionDetail, Volume)
from qiprofile_rest.model.clinical import (Encounter, Evaluation, TNM)

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
        subject = Subject(collection='Breast', number=1)
        subject.races = ['White', 'Black', 'Asian', 'AIAN', 'NHOPI']
        subject.save()

        subject = Subject(collection='Breast', number=1)
        subject.races = ['Invalid']
        with assert_raises(ValidationError):
            subject.save()

        # Races must be a list.
        subject.races = 'White'
        with assert_raises(ValidationError):
            subject.save()

    def test_ethnicity(self):
        subject = Subject(collection='Breast', number=1)
        subject.ethnicity = 'Non-Hispanic'
        subject.save()

        subject.ethnicity = 'Invalid'
        with assert_raises(ValidationError):
            subject.save()

    def test_encounter(self):
        subject = Subject(collection='Breast', number=1)
        date = datetime(2013, 1, 4, tzinfo=pytz.utc)
        encounter = Encounter(encounter_type='Biopsy', date=date)
        subject.encounters = [encounter]
        # The encounter outcome is optional.
        subject.save()
        # Add the evaluation.
        evaluation = Evaluation()
        outcome = TNM()
        evaluation.outcomes = [outcome]
        encounter.evaluation = evaluation
        subject.save()

    def test_tnm_size(self):
        for value in ['T1', 'Tx', 'cT4', 'T1b', 'cT2a']:
            size = TNM.Size.parse(value)
            assert_equal(str(size), value, "TNM parse incorrect -"
                                           " expected %s, found %s"
                                           % (value, str(size)))

    def test_session(self):
        subject = Subject(collection='Breast', number=1)
        date = datetime(2013, 1, 4, tzinfo=pytz.utc)
        session = Session(number=1, acquisition_date=date)
        subject.sessions = [session]
        subject.save()

    def test_modeling(self):
        # TODO - add modeling test case.
        pass

    def test_detail(self):
        # Make a detail object with a bogus bolus arrival index.
        detail = SessionDetail(bolus_arrival_index=4)
        # The bolus arrival index must refer to an existing volume.
        with assert_raises(ValidationError):
            detail.save()
        
        # Add the volumes.
        detail.volumes = [Volume(number=7+i) for i in range(0, 32)]
        # The detail is now valid.
        detail.save()

        # The bolus arrival index does not refer to a volume.
        detail.bolus_arrival_index = 32
        with assert_raises(ValidationError):
            detail.save()

if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
