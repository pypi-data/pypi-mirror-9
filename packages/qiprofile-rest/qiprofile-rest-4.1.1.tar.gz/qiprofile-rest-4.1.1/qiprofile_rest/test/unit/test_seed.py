from nose.tools import (assert_is_none, assert_is_instance, assert_in,
                        assert_is_not_none, assert_true, assert_equal)
from datetime import datetime
from mongoengine import connect
from mongoengine.connection import get_db
from qiprofile_rest.model.subject import Subject
from qiprofile_rest.model.uom import Weight
from qiprofile_rest.model.clinical import (Assessment, Biopsy, Surgery, Drug)
from qiprofile_rest.test.helpers import seed

MODELING_RESULT_PARAMS = ['fxl_k_trans', 'fxr_k_trans', 'delta_k_trans', 'v_e', 'tau_i']
"""The test seed modeling result parameters."""

class TestSeed(object):
    """
    This TestSeed class tests the seed helper utility.

    Note: this test drops the ``qiprofile-test`` Mongo database
    at the beginning and end of execution.
    """
    def setup(self):
        connect(db='qiprofile_test')
        self.db = get_db()
        self.db.connection.drop_database('qiprofile_test')
        self._subjects = seed.seed()

    def tearDown(self):
        self.db.connection.drop_database('qiprofile_test')

    def test_serialization(self):
        for saved_sbj in self._subjects:
            query = dict(project=saved_sbj.project,
                         collection=saved_sbj.collection,
                         number=saved_sbj.number)
            fetched_sbj = Subject.objects.get(**query)
            self._validate_subject(fetched_sbj)
 
    SESSION_CNT = dict(
        Breast=4,
        Sarcoma=3
    )
 
    def _validate_subject(self, subject):
        collections = ((coll.name for coll in seed.COLLECTIONS))
        assert_in(subject.collection, collections,
                  "Collection is invalid: %s" % subject.collection)
        self._validate_demographics(subject)
        self._validate_sessions(subject)


    def _validate_demographics(self, subject):
        assert_is_not_none(subject.gender, "%s is missing gender" % subject)
        assert_is_not_none(subject.weight, "%s is missing weight" % subject)
        assert_is_not_none(subject.sessions, "%s has no sessions" % subject)


    def _validate_clincal_date(self, subject):
        # There are three treatments.
        treatments = subject.treatments
        assert_equal(len(treatments), 3,
                     "%s Subject %d treatments count is incorrect: %d" %
                     (subject.collection, subject.number, len(treatments)))
        # Breast has neoadjuvant drugs.
        if subject.collection == 'Breast':
            neo_tx = next(((trt for trt in treatments if trt.treatment_type == 'Neoadjuvant')),
                          None)
            assert_is_not_none(neo_tx, ("%s Subject %d is missing a neodjuvant" +
                                        " treatment") % (subject.collection, subject.number))
            dosages = neo_tx.dosages
            assert_equal(len(dosages), 2,
                         (("%s session %d neoadjuvant treatment dosage count is" +
                          " incorrect: %d") % (subject.collection, subject.number, len(dosages))))
            # Validate the agent type and dosage unit.
            for dosage in dosages:
                agent = dosage.agent
                assert_is_instance(agent, Drug,
                                   "%s Subject %d neoadjuvant agent is not a drug" %
                                   (subject.collection, subject.number))
                amount = dosage.amount
                assert_is_not_none(amount, ("%s Subject %d is missing a neodjuvant drug" +
                                          " dosage amount") % (subject.collection, subject.number))
                unit = amount.unit
                assert_is_not_none(unit, ("%s Subject %d is missing a neodjuvant drug" +
                                          " dosage unit") % (subject.collection, subject.number))
                assert_is_instance(unit, Weight, ("%s Subject %d neodjuvant drug dosage" +
                                                      " unit is incorrect") %
                                                      (subject.collection, subject.number))
                per_unit = amount.per_unit
                assert_is_not_none(per_unit, ("%s Subject %d is missing a neodjuvant drug" +
                                              " dosage per unit") % (subject.collection, subject.number))
                assert_is_instance(per_unit, Weight, ("%s Subject %d neodjuvant drug" +
                                                          " dosage per unit is incorrect") %
                                                          (subject.collection, subject.number))
                assert_equal(per_unit.scale, 'k', ("%s Subject %d neodjuvant drug per unit scale" +
                                             " is not kilogram") % ((subject.collection, subject.number)))

        encounters = subject.encounters
        assert_equal(len(encounters), 3,
                     "%s Subject %d encounter count is incorrect: %d" %
                     (subject.collection, subject.number, len(encounters)))
        biopsy = next(((enc for enc in encounters if isinstance(enc, Biopsy))),
                      None)
        assert_is_not_none(biopsy, "%s Subject %d is missing a biopsy" %
                                   (subject.collection, subject.number))
        path = biopsy.pathology
        assert_is_not_none(path, "%s biopsy is missing a pathology report" %
                                 subject)
        assert_is_not_none(path.tnm, "%s biopsy pathology report is missing"
                                     " a TNM" % subject)
        assert_is_not_none(path.tnm.tumor_type, "%s biopsy TNM is missing the"
                                     " tumor type" % subject)
        
        # Breast has specialized tests.
        if subject.collection == 'Breast':
            assert_is_not_none(path.hormone_receptors.estrogen,
                               "%s biopsy pathology report is missing an"
                               " estrogen status" % subject)
            assert_is_not_none(path.hormone_receptors.progesterone,
                               "%s biopsy pathology report is missing a"
                               " progesterone status" % subject)
            assert_is_not_none(path.genetic_expression.her2_neu_ihc,
                               "%s biopsy pathology report is missing a"
                               " HER2 NEU IHC status" % subject)
            assert_is_not_none(path.genetic_expression.her2_neu_fish,
                               "%s biopsy pathology report is missing a"
                               " HER2 NEU FISH status" % subject)
            assert_is_not_none(path.genetic_expression.ki67,
                               "%s biopsy pathology report is missing a"
                               " Ki67 status" % subject)
            # The first breast subject has value overrides.
            if subject.number == 1:
                assert_true(path.hormone_receptors.estrogen.positive,
                            "The first Breast subject is not estrogen-receptor-positive")
                assert_equal(path.tnm.lymph_status, 0, "The first Breast subject"
                                                       " lymph status is incorrect")
            # A subject who is estrogen-receptor-positive and has no lymph nodes
            # has a normalized assay.
            if path.hormone_receptors.estrogen.positive and not path.tnm.lymph_status:
                assay = path.genetic_expression.normalized_assay
                assert_is_not_none(assay, "%s biopsy pathology report with HER2"
                                          " positive and no lymph nodes is missing"
                                          " a normalized assay" % subject)
                assert_is_not_none(assay.gstm1, "%s biopsy pathology report"
                                                " normalized assay is missing"
                                                " a GSTM1 result" % subject)
                assert_is_not_none(assay.cd68, "%s biopsy pathology report"
                                               " normalized assay is missing"
                                               " a CD68 result" % subject)
                assert_is_not_none(assay.bag1, "%s biopsy pathology report"
                                               " normalized assay is missing"
                                               " a BAG1 result" % subject)
                assert_is_not_none(assay.her2, "%s biopsy pathology report"
                                               " normalized assay is missing"
                                               " the HER2 group" % subject)
                assert_is_not_none(assay.estrogen, "%s biopsy pathology report"
                                                   " normalized assay is missing"
                                                   " the estrogen group" % subject)
                assert_is_not_none(assay.proliferation, "%s biopsy pathology report"
                                                        " normalized assay is missing"
                                                        " the proliferation group" %
                                                        subject)
                assert_is_not_none(assay.invasion, "%s biopsy pathology report"
                                                   " normalized assay is missing"
                                                   " the invasion group" % subject)
                
        
        surgery = next(((enc for enc in encounters if isinstance(enc, Surgery))),
                      None)
        assert_is_not_none(surgery, "%s Subject %d is missing a surgery" %
                                     (subject.collection, subject.number))
        assert_is_none(surgery.pathology,
                     "%s surgery incorrectly has an evaluation" % subject)
        post_trt = next(((enc for enc in encounters if isinstance(enc, Assessment))),
                      None)
        assert_is_not_none(post_trt, "%s Subject %d is missing an assessment" %
                                     (subject.collection, subject.number))
        assert_is_not_none(post_trt.evaluation,
                     "%s post-treatment assessment is missing an evaluation" % subject)

    def _validate_sessions(self, subject):
        sessions = subject.sessions
        session_cnt = TestSeed.SESSION_CNT[subject.collection]
        assert_equal(len(sessions), session_cnt, "%s session count is incorrect: %d" %
                                  (subject, len(sessions)))
        for session in sessions:
            self._validate_session(subject, session)

    def _validate_session(self, subject, session):
        assert_is_not_none(session.acquisition_date,
                           "%s session %d is missing an acquisition date" %
                           (subject, session.number))
        assert_is_instance(session.acquisition_date, datetime,
                           "%s session %d acquisition date type is incorrect: %s" %
                           (subject, session.number, session.acquisition_date.__class__))
        self._validate_modeling(subject, session)
        self._validate_session_detail(subject, session)
    
    def _validate_modeling(self, subject, session):
        # The registration is modeled.
        assert_equal(len(session.modeling), 1,
                     "%s session %d modeling length is incorrect: %d" %
                     (subject, session.number, len(session.modeling)))
        modeling = session.modeling[0]
        assert_is_not_none(modeling.resource,
                           "%s session %d is missing the modeling resource" %
                           (subject, session.number))
        assert_is_not_none(modeling.protocol,
                           "%s session %d modeling %s is missing the protocol" %
                           (subject, session.number, modeling.resource))
        assert_is_not_none(modeling.source,
                           "%s session %d modeling %s is missing the source" %
                           (subject, session.number, modeling.resource))
        
        # Validate the modeling result.
        for param in MODELING_RESULT_PARAMS:
            value = modeling.result[param]
            assert_is_not_none(value,
                               "%s Subject %d modeling %s is missing a %s parameter" %
                               (subject.collection, subject.number, modeling.resource, param))
            assert_is_not_none(value.average,
                               "%s Subject %d modeling %s is missing a %s average" %
                               (subject.collection, subject.number, modeling.resource, param))
            assert_is_not_none(value.filename,
                               "%s Subject %d modeling %s is missing a %s filename" %
                               (subject.collection, subject.number, modeling.resource, param))
        
        # The delta Ktrans result has an overlay.
        label_map = modeling.result['delta_k_trans'].label_map
        assert_is_not_none(label_map,
                           "%s Subject %d modeling is missing a label_map" %
                           (subject.collection, subject.number))
        assert_is_not_none(label_map.filename,
                           "%s Subject %d modeling label map is missing a file name" %
                           (subject.collection, subject.number))
        assert_is_not_none(label_map.color_table,
                           "%s Subject %d modeling   label map is missing a color table" %
                           (subject.collection, subject.number))

    def _validate_session_detail(self, subject, session):
        assert_is_not_none(session.detail, "%s session %d is missing detail" %
                                           (subject, session.number))
        # Validate the scans.
        scans = session.detail.scans
        assert_equal(len(scans), 2, "%s session %d scan count is incorrect: %d" %
                                    (subject, session.number, len(scans)))
        # The T1 scan.
        scan = scans[0]
        expected_volume_cnt = seed.collection_for(subject.collection).volume_count
        assert_equal(len(scan.volumes), expected_volume_cnt,
                     "%s session %d scan %d volumes count is incorrect: %d" %
                     (subject, session.number, scan.number, len(scan.volumes)))
        for volume in scan.volumes:
            assert_is_not_none(volume.average_intensity,
                               "%s session %d scan %d volume %d is missing an intensity" %
                               (subject, session.number, scan.number, volume.number))
            # Verify that intensities are floats.
            assert_true(isinstance(volume.average_intensity, float),
                        "%s session %d scan %d volume %d intensity type is"
                        " incorrect for value %s: %s" %
                        (subject, session.number, scan.number, volume.number,
                         volume.average_intensity, volume.average_intensity.__class__))

        # Validate the registration.
        regs = scan.registrations
        assert_equal(len(regs), 1, "%s session %d scan %d registration count"
                                    " is incorrect: %d" %
                                    (subject, session.number, scan.number, len(regs)))
        for reg in regs:
            for volume in reg.volumes:
                assert_is_not_none(volume.average_intensity,
                                   "%s session %d scan %d registration %s volume %d"
                                   " is missing an intensity" %
                                   (subject, session.number, scan.number, reg.resource,
                                    volume.number))
                # Verify that intensities are floats.
                assert_true(isinstance(volume.average_intensity, float),
                            "%s session %d scan %d registration %s volume %d"
                            " intensity type is incorrect for value %s: %s" %
                            (subject, session.number, scan.number, reg.resource,
                             volume.number, volume.average_intensity,
                             volume.average_intensity.__class__))


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
