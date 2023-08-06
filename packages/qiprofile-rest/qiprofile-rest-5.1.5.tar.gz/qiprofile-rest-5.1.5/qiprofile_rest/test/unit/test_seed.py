from nose.tools import (assert_is_none, assert_is_instance, assert_in,
                        assert_is_not_none, assert_true, assert_equal)
from datetime import datetime
from mongoengine import connect
from mongoengine.connection import get_db
from qiprofile_rest_client.model.subject import Subject
from qiprofile_rest_client.model.uom import Weight
from qiprofile_rest_client.model.clinical import (Assessment, Biopsy, Surgery, Drug)
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
        self._validate_clincal_data(subject)
        self._validate_sessions(subject)

    def _validate_demographics(self, subject):
        assert_is_not_none(subject.gender, "%s is missing gender" % subject)

    def _validate_clincal_data(self, subject):
        # There are three treatments.
        self._validate_treatments(subject)
        # Validate the encounters.
        self._validate_encounters(subject)

    def _validate_treatments(self, subject):
        # There are three treatments.
        treatments = subject.treatments
        assert_is_not_none(treatments, "%s has no treatments" % subject)
        assert_equal(len(treatments), 3,
                     "%s Subject %d treatments count is incorrect: %d" %
                     (subject.collection, subject.number, len(treatments)))
        # Breast has neoadjuvant drugs.
        if subject.collection == 'Breast':
            self._validate_breast_treatments(subject, treatments)

    def _validate_breast_treatments(self, subject, treatments):
        # Breast has neoadjuvant drugs.
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

    def _validate_encounters(self, subject):
        encounters = subject.encounters
        assert_is_not_none(encounters, "%s has no encounters" % subject)
        assert_equal(len(encounters), 3,
                     "%s Subject %d encounter count is incorrect: %d" %
                     (subject.collection, subject.number, len(encounters)))
        biopsy = next(((enc for enc in encounters if isinstance(enc, Biopsy))),
                      None)
        assert_is_not_none(biopsy, "%s Subject %d is missing a biopsy" %
                                   (subject.collection, subject.number))
        self._validate_pathology(subject, biopsy.pathology)
        
        # There is a surgery with a pathology.
        surgery = next(((enc for enc in encounters if isinstance(enc, Surgery))),
                       None)
        assert_is_not_none(surgery, "%s Subject %d is missing a surgery" %
                                     (subject.collection, subject.number))
        assert_is_not_none(surgery.pathology,
                     "%s surgery is missing a pathology report" % subject)
        self._validate_pathology(subject, surgery.pathology)
        
        # There is a post-treatment TNM.
        post_trt = next(((enc for enc in encounters if isinstance(enc, Assessment))),
                        None)
        assert_is_not_none(post_trt, "%s Subject %d is missing an assessment" %
                                     (subject.collection, subject.number))
        assert_is_not_none(post_trt.evaluation,
                           "%s post-treatment assessment is missing an evaluation" %
                           subject)
        assert_is_not_none(post_trt.evaluation.outcomes,
                           "%s post-treatment assessment is missing outcomes" %
                           subject)
        assert_equal(len(post_trt.evaluation.outcomes), 1,
                        "%s post-treatment outcomes count is incorrect" % subject)
        post_trt_tnm = post_trt.evaluation.outcomes[0]
        self._validate_tnm(subject, post_trt_tnm)
        
    def _validate_pathology(self, subject, pathology):
        assert_is_not_none(pathology, "%s is missing a pathology report" %
                                      subject)
        self._validate_tnm(subject, pathology.tnm)
        # The tumor-specific tests.
        if subject.collection == 'Breast':
            self._validate_breast_pathology(subject, pathology)
        elif subject.collection == 'Sarcoma':
            self._validate_sarcoma_pathology(subject, pathology)
        
    def _validate_tnm(self, subject, tnm):
        assert_is_not_none(tnm, "%s is missing a TNM" % subject)
        assert_is_not_none(tnm.tumor_type,
                           "%s TNM is missing the tumor type" % subject)
        assert_is_not_none(tnm.grade,
                           "%s TNM is missing the grade" % subject)
        assert_is_not_none(tnm.size,
                           "%s TNM is missing the grade" % subject)
        assert_is_not_none(tnm.lymph_status,
                           "%s TNM is missing the grade" % subject)
        assert_is_not_none(tnm.lymphatic_vessel_invasion,
                           "%s TNM is missing the grade" % subject)
        assert_is_not_none(tnm.metastasis,
                           "%s TNM is missing the grade" % subject)
        
    def _validate_breast_pathology(self, subject, pathology):
        assert_is_not_none(pathology.hormone_receptors.estrogen,
                           "%s pathology report is missing an"
                           " estrogen status" % subject)
        assert_is_not_none(pathology.hormone_receptors.progesterone,
                           "%s pathology report is missing a"
                           " progesterone status" % subject)
        assert_is_not_none(pathology.genetic_expression.her2_neu_ihc,
                           "%s pathology report is missing a"
                           " HER2 NEU IHC status" % subject)
        assert_is_not_none(pathology.genetic_expression.her2_neu_fish,
                           "%s pathology report is missing a"
                           " HER2 NEU FISH status" % subject)
        assert_is_not_none(pathology.genetic_expression.ki67,
                           "%s pathology report is missing a"
                           " Ki67 status" % subject)
        # The first breast subject has value overrides.
        if subject.number == 1:
            assert_true(pathology.hormone_receptors.estrogen.positive,
                        "The first Breast subject is not estrogen-receptor-positive")
            assert_equal(pathology.tnm.lymph_status, 0, "The first Breast subject"
                                                   " lymph status is incorrect")
        # A subject who is estrogen-receptor-positive and has no lymph nodes
        # has a normalized assay.
        if pathology.hormone_receptors.estrogen.positive and not pathology.tnm.lymph_status:
            assay = pathology.genetic_expression.normalized_assay
            assert_is_not_none(assay, "%s pathology report with HER2"
                                      " positive and no lymph nodes is missing"
                                      " a normalized assay" % subject)
            assert_is_not_none(assay.gstm1, "%s pathology report"
                                            " normalized assay is missing"
                                            " a GSTM1 result" % subject)
            assert_is_not_none(assay.cd68, "%s pathology report"
                                           " normalized assay is missing"
                                           " a CD68 result" % subject)
            assert_is_not_none(assay.bag1, "%s pathology report"
                                           " normalized assay is missing"
                                           " a BAG1 result" % subject)
            assert_is_not_none(assay.her2, "%s pathology report"
                                           " normalized assay is missing"
                                           " the HER2 group" % subject)
            assert_is_not_none(assay.estrogen, "%s pathology report"
                                               " normalized assay is missing"
                                               " the estrogen group" % subject)
            assert_is_not_none(assay.proliferation, "%s pathology report"
                                                    " normalized assay is missing"
                                                    " the proliferation group" %
                                                    subject)
            assert_is_not_none(assay.invasion, "%s pathology report"
                                               " normalized assay is missing"
                                               " the invasion group" % subject)
        
    def _validate_sarcoma_pathology(self, subject, pathology):
        assert_is_not_none(pathology.location,
                           "%s pathology report is missing a tumor location" % subject)

    def _validate_sessions(self, subject):
        sessions = subject.sessions
        assert_is_not_none(sessions, "%s has no sessions" % subject)
        session_cnt = TestSeed.SESSION_CNT[subject.collection]
        assert_equal(len(sessions), session_cnt, "%s session count is incorrect: %d" %
                                  (subject, len(sessions)))
        for i, session in enumerate(sessions):
            # Set a session number for reporting.
            session.number = i + 1
            self._validate_session(subject, session)

    def _validate_session(self, subject, session):
        assert_is_not_none(session.acquisition_date,
                           "%s session %d is missing the acquisition date" %
                           (subject, session.number))
        assert_is_instance(session.acquisition_date, datetime,
                           "%s session %d acquisition date type is incorrect: %s" %
                           (subject, session.number, session.acquisition_date.__class__))
        assert_is_not_none(session.subject_weight,
                           "%s session %d is missing the subject weight" %
                           (subject, session.number))
        assert_is_instance(session.subject_weight, int,
                           "%s session %d subject weight type is incorrect: %s" %
                           (subject, session.number, session.subject_weight.__class__))
        self._validate_modeling(subject, session)
        self._validate_session_detail(subject, session)
    
    def _validate_modeling(self, subject, session):
        # The registration is modeled.
        assert_equal(len(session.modelings), 1,
                     "%s session %d modeling length is incorrect: %d" %
                     (subject, session.number, len(session.modelings)))
        modeling = session.modelings[0]
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
        for i, volume in enumerate(scan.volumes):
            assert_is_not_none(volume.average_intensity,
                               "%s session %d scan %d volume %d is missing an intensity" %
                               (subject, session.number, scan.number, i + 1))
            # Verify that intensities are floats.
            assert_true(isinstance(volume.average_intensity, float),
                        "%s session %d scan %d volume %d intensity type is"
                        " incorrect for value %s: %s" %
                        (subject, session.number, scan.number, i + 1,
                         volume.average_intensity, volume.average_intensity.__class__))

        # Validate the registration.
        regs = scan.registrations
        assert_equal(len(regs), 1, "%s session %d scan %d registration count"
                                    " is incorrect: %d" %
                                    (subject, session.number, scan.number, len(regs)))
        for reg in regs:
            for i, volume in enumerate(reg.volumes):
                assert_is_not_none(volume.average_intensity,
                                   "%s session %d scan %d registration %s volume %d"
                                   " is missing an intensity" %
                                   (subject, session.number, scan.number, reg.resource,
                                    i + 1))
                # Verify that intensities are floats.
                assert_true(isinstance(volume.average_intensity, float),
                            "%s session %d scan %d registration %s volume %d"
                            " intensity type is incorrect for value %s: %s" %
                            (subject, session.number, scan.number, reg.resource,
                             i + 1, volume.average_intensity,
                             volume.average_intensity.__class__))

        # The T2 scan has one volume without an intensity value.
        scan = scans[1]
        assert_equal(len(scan.volumes), 1,
                     "%s session %d scan %d volumes count is incorrect: %d" %
                     (subject, session.number, scan.number, len(scan.volumes)))
        volume = scan.volumes[0]
        assert_is_none(volume.average_intensity,
                       "%s session %d scan %d volume %d incorrectly has an intensity" %
                       (subject, session.number, scan.number, 1))


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
