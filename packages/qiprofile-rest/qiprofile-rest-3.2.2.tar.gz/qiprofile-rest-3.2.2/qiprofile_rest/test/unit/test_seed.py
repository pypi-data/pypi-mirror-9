from nose.tools import (assert_is_none, assert_is_instance, assert_in,
                        assert_is_not_none, assert_true, assert_equal)
from datetime import datetime
from mongoengine import connect
from mongoengine.connection import get_db
from qiprofile_rest.model.subject import Subject
from qiprofile_rest.model.uom import Weight
from qiprofile_rest.model.clinical import (Assessment, Biopsy, Surgery, Drug)
from qiprofile_rest.test.helpers import seed

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
        assert_is_not_none(subject.gender, "%s is missing gender" % subject)
        assert_is_not_none(subject.weight, "%s is missing weight" % subject)
        assert_is_not_none(subject.sessions, "%s has no sessions" % subject)
        sessions = subject.sessions
        session_cnt = TestSeed.SESSION_CNT[subject.collection]
        assert_equal(len(sessions), session_cnt, "%s session count is incorrect: %d" %
                                  (subject, len(sessions)))
        for session in sessions:
            self._validate_session(subject, session)
        
        # There are scan sets.
        scan_sets = subject.scan_sets
        assert_is_not_none(scan_sets, "%s Subject %s is missing scan sets" %
                                       (subject.collection, subject.number))
        assert_equal(set(scan_sets.keys()), set(['t1', 't2']),
                     "%s Subject %s scan set keys are incorrect: %s" %
                     (subject.collection, subject.number, scan_sets.keys()))
        
        # The T1 scan set has a registration.
        t1_scan_set = scan_sets['t1']
        reg_cfgs = t1_scan_set.registration
        assert_is_not_none(reg_cfgs, "%s Subject %s is missing registration"
                                     " configurations" %
                                     (subject.collection, subject.number))
        assert_equal(len(reg_cfgs), 1,
                     "%s Subject %s registration configurations size is"
                     " incorrect: %d" %
                     (subject.collection, subject.number, len(reg_cfgs)))
        reg_cfg = next(reg_cfgs.itervalues())
        assert_is_not_none(reg_cfg.parameters,
                           "%s Subject %s registration configuration is missing"
                           " parameters" % (subject.collection, subject.number))
        assert_equal(reg_cfg.parameters, seed.REG_PARAMS,
                     "%s Subject %s registration parameters are incorrect: %s" %
                     (subject.collection, subject.number, reg_cfg.parameters))
        
        # The registration configuration is modeled.
        assert_is_not_none(reg_cfg.modeling, "%s is missing modeling" %
                                             subject)
        assert_equal(len(reg_cfg.modeling), 1, "%s modeling length is incorrect: %d" %
                                               (subject, len(reg_cfg.modeling)))
        mdl = next(reg_cfg.modeling.itervalues())
        assert_is_not_none(mdl.input_parameters,
                           "%s Subject %d modeling is missing the input parameters" %
                           (subject.collection, subject.number))
        if subject.collection == 'Breast':
            mdl_result_len = 4
        elif subject.collection == 'Sarcoma':
            mdl_result_len = 3
        assert_equal(len(mdl.results), mdl_result_len,
                     "%s Subject %s modeling results size is incorrect: %d" %
                     (subject.collection, subject.number, len(mdl.results)))
        mdl_result = mdl.results[0]
        fxl_k_trans = mdl_result.fxl_k_trans
        assert_is_not_none(fxl_k_trans, ("%s Subject %d modeling is"
                                         " missing a fxl_k_trans parameter") %
                                         (subject.collection, subject.number))
        assert_is_not_none(fxl_k_trans.average, ("%s Subject %d modeling"
                                        " is missing a fxl_k_trans average") %
                                        (subject.collection, subject.number))
        assert_is_not_none(fxl_k_trans.filename, ("%s Subject %d modeling"
                                        " is missing a fxl_k_trans filename") %
                                        (subject.collection, subject.number))
        
        fxr_k_trans = mdl_result.fxr_k_trans
        assert_is_not_none(fxr_k_trans, ("%s Subject %d modeling is"
                                        " missing a fxr_k_trans parameter") %
                                        (subject.collection, subject.number))
        assert_is_not_none(fxr_k_trans.average, ("%s Subject %d modeling"
                                        " is missing a fxr_k_trans average") %
                                        (subject.collection, subject.number))
        assert_is_not_none(fxr_k_trans.filename, ("%s Subject %d modeling"
                                        " is missing a fxr_k_trans filename") %
                                        (subject.collection, subject.number))
        
        delta_k_trans = mdl_result.delta_k_trans
        assert_is_not_none(delta_k_trans, ("%s Subject %d modeling is"
                                          " missing a delta_k_trans parameter") %
                                          (subject.collection, subject.number))
        assert_is_not_none(delta_k_trans.average,
                           ("%s Subject %d modeling is missing a"
                            " delta_k_trans average") %
                            (subject.collection, subject.number))
        assert_is_not_none(delta_k_trans.filename,
                           ("%s Subject %d modeling is missing a"
                           " delta_k_trans filename") %
                           (subject.collection, subject.number))
        label_map = delta_k_trans.label_map
        assert_is_not_none(label_map,
                           ("%s Subject %d modeling is missing a"
                            " label_map") % (subject.collection, subject.number))
        assert_is_not_none(label_map.filename,
                           ("%s Subject %d modeling label map is"
                            " missing a file name") % (subject.collection, subject.number))
        assert_is_not_none(label_map.color_table,
                           ("%s Subject %d modeling   label map is"
                            " missing a color table") % (subject.collection, subject.number))
        
        v_e = mdl_result.v_e
        assert_is_not_none(v_e, ("%s Subject %d modeling is missing"
                                 " a v_e parameter" %
                                 (subject.collection, subject.number)))
        assert_is_not_none(v_e.average, ("%s Subject %d modeling"
                                         " is missing a v_e average") %
                                         (subject.collection, subject.number))
        assert_is_not_none(v_e.filename, ("%s Subject %d modeling"
                                          " is missing a v_e filename") %
                                          (subject.collection, subject.number))
        
        tau_i = mdl_result.tau_i
        assert_is_not_none(tau_i, ("%s Subject %d modeling is missing"
                                  " a tau_i parameter") %
                                  (subject.collection, subject.number))
        assert_is_not_none(tau_i.average, ("%s Subject %d modeling"
                                          " is missing a tau_i average") %
                                          (subject.collection, subject.number))
        assert_is_not_none(tau_i.filename, ("%s Subject %d modeling"
                                           " is missing a tau_i filename") %
                                           (subject.collection, subject.number))

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

    def _validate_session(self, subject, session):
        assert_is_not_none(session.acquisition_date,
                           "%s session %d is missing an acquisition date" %
                           (subject, session.number))
        assert_is_instance(session.acquisition_date, datetime,
                           "%s session %d acquisition date type is incorrect: %s" %
                           (subject, session.number, session.acquisition_date.__class__))
        assert_is_not_none(session.detail, "%s session %d is missing detail" %
                                           (subject, session.number))
        
        # Validate the scans.
        scans = session.detail.scans
        assert_equal(len(scans), 2, "%s session %d scan count is incorrect: %d" %
                                    (subject, session.number, len(scans)))
        
        # The T1 scan.
        t1_scan = scans.get('t1', None)
        assert_is_not_none(t1_scan, "%s session %d is missing the T1 scan" %
                                        (subject, session.number))
        scan_intensity = t1_scan.intensity
        assert_is_not_none(scan_intensity, "%s session %d scan is missing an"
                                           " intensity" % (subject, session.number))
        
        # Validate the registration.
        assert_true(not not t1_scan.registration,
               "%s session %d registration is missing a registration" %
               (subject, session.number))
        reg = next(t1_scan.registration.itervalues())

        reg_intensity = reg.intensity
        assert_is_not_none(reg.intensity,
                           "%s session %d registration is missing an intensity" %
                            (subject, session.number))
        
        # Verify that decimals are decoded as numbers.
        for value in reg_intensity.intensities:
            assert_true(isinstance(value, float),
                        "Float field type is incorrect for value %s: %s" %
                        (value, value.__class__))


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
