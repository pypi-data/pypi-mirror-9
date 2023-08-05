#!/usr/bin/env python
import os
import re
from datetime import (datetime, timedelta)
import pytz
import random
import math
from decimal import Decimal
from mongoengine import connect
from qiutil import uid
from qiprofile_rest import choices
from qiprofile_rest.models import (Subject, SubjectDetail, Session, SessionDetail,
                                   Modeling, ModelingResult, ModelingParameter,
                                   LabelMap, Series, Scan, ScanSet, Registration,
                                   Intensity, Probe, Treatment, Drug, Dosage,
                                   Measurement, Weight,Biopsy, Surgery, Assessment,
                                   GenericEvaluation, BreastPathology, SarcomaPathology,
                                   TNM, ModifiedBloomRichardsonGrade, FNCLCCGrade, NecrosisPercentValue,
                                   NecrosisPercentRange, HormoneReceptorStatus)

PROJECT = 'QIN_Test'

class Collection(object):
    def __init__(self, name, visit_count, series_numbers):
        self.name = name
        self.visit_count = visit_count
        self.series_numbers = series_numbers


class Breast(Collection):
    SERIES_NUMBERS = [7, 8] + [11 + 2*n for n in range(0, 30)]
    """
    The  Breast series numbers are 7, 8, 11, 13, ..., 69.
    There are 32 AIRC Breast scans.
    """
    def __init__(self):
        super(Breast, self).__init__(name='Breast', visit_count=4,
                                     series_numbers=Breast.SERIES_NUMBERS)

    def create_grade(self):
        """
        @return the ModifiedBloomRichardson grade
        """
        tubular_formation = _random_int(1, 3)
        nuclear_pleomorphism = _random_int(1, 3)
        mitotic_count = _random_int(1, 3)

        return ModifiedBloomRichardsonGrade(tubular_formation=tubular_formation,
                                     nuclear_pleomorphism=nuclear_pleomorphism,
                                     mitotic_count=mitotic_count)

    def create_pathology(self):
        # The TNM score.
        tnm = _create_tnm(self, 'p')

        # The estrogen status.
        positive = _random_boolean()
        quick_score = _random_int(0, 8)
        intensity = _random_int(0, 100)
        estrogen = HormoneReceptorStatus(hormone='estrogen',
                                         positive=positive,
                                         quick_score=quick_score,
                                         intensity=intensity)

        # The progesterone status.
        positive = _random_boolean()
        quick_score = _random_int(0, 8)
        intensity = _random_int(0, 100)
        progesterone = HormoneReceptorStatus(hormone='progesterone',
                                             positive=positive,
                                             quick_score=quick_score,
                                             intensity=intensity)

        # HER2 NEU IHC is one of 0, 1, 2, 3.
        her2_neu_ihc = _random_int(0, 3)

        # HER2 NEU FISH is True (positive) or False (negative).
        her2_neu_fish = _random_boolean()

        # KI67 is a percent.
        ki_67 = _random_int(0, 100)

        return BreastPathology(tnm=tnm, estrogen=estrogen,
                               progesterone=progesterone,
                               her2_neu_ihc=her2_neu_ihc,
                               her2_neu_fish=her2_neu_fish,
                               ki_67=ki_67)

class Sarcoma(Collection):
    SERIES_NUMBERS = [9, 10] + [13 + 2*n for n in range(0, 38)]
    """
    The Sarcoma series numbers are 9, 10, 13, 15, ..., 87.
    There are 40 AIRC Sarcoma001 Session01 series.

    Note: the AIRC Sarcoma scan count and numbering scheme varies.
    """

    def __init__(self):
        super(Sarcoma, self).__init__(name='Sarcoma', visit_count=3,
                                     series_numbers=Sarcoma.SERIES_NUMBERS)

    def create_grade(self):
        """
        @return the FNCLCC grade
        """
        differentiation = _random_int(1, 3)
        mitotic_count = _random_int(1, 3)
        necrosis = _random_int(0, 2)

        return FNCLCCGrade(differentiation=differentiation, mitotic_count=mitotic_count,
                           necrosis=necrosis)
        
    def create_pathology(self):
        # The TNM score.
        tnm = _create_tnm(self, 'p')

        # The tumor site.
        site = 'Thigh'

        # The necrosis percent is either a value or a decile range.
        if _random_boolean():
            value = _random_int(0, 100)
            necrosis_pct = NecrosisPercentValue(value=value)
        else:
            low = _random_int(0, 9) * 10
            start = NecrosisPercentRange.LowerBound(value=low)
            stop = NecrosisPercentRange.UpperBound(value=low+10)
            necrosis_pct = NecrosisPercentRange(start=start, stop=stop)

        # The histology                                      
        histology = 'Fibrosarcoma'

        return SarcomaPathology(tnm=tnm, site=site, necrosis_pct=necrosis_pct,
                                histology=histology)


COLLECTIONS = [Breast(), Sarcoma()]

def collection_for(name):
    try:
        return next((coll for coll in COLLECTIONS if coll.name == name))
    except StopIteration:
        raise ValueError("The collection is not supported: %s" % name)


DATE_0 = datetime(2013, 1, 4, tzinfo=pytz.utc)
"""The first image acquisition date."""

FXL_K_TRANS_AVG = 0.2
"""The average Standard Model Ktrans value."""

DELTA_K_TRANS_FACTOR = 1.3
"""
The detal Ktrans multiplier.
The FXR (Shutter Speed Model) Ktrans = FXL_K_TRANS_AVG * DELTA_K_TRANS_FACTOR.
"""

TAU_I_0 = 0.4875
"""The first tau_i."""

V_E_0 = 0.6113
"""The first v_e vale."""

AVG_BOLUS_ARRIVAL_NDX = 2
"""Bolus arrivals are spread evenly around the third visit."""

REG_PARAMS = dict(
    transforms='[Rigid, Affine, SyN]',
    metric='[MI, MI, CC]',
    metric_weight='[1, 1, 1]',
    number_of_iterations='[[10000, 500, 200, 100], [10000, 500, 200, 100], [100, 20, 10]]',
    radius_or_number_of_bins='[32, 32, 4]',
    sampling_strategy='[Regular, Regular, None]',
    sampling_percentage='[0.3, 0.3, None]',
    smoothing_sigmas='[[3,2,1,0], [3,2,1,0], [2,1,0]]',
    shrink_factors='[[8,4,2,1], [8,4,2,1], [4,2,1]]',
    transform_parameters='[(0.1,), (0.1,), (0.1, 3, 0)]'
)


def seed():
    """
    Populates the MongoDB database named ``qiprofile_test`` with
    three subjects each of the ``Breast`` and ``Sarcoma`` collection.
    
    Note: existing subjects are not modified. In order to refresh the
    seed subjects, drop the ``qiprofile_test`` database first.
    
    
    @return: three :obj:`PROJECT` subjects for each collection in
        :obj:`COLLECTIONS`
    """
    # Initialize the pseudo-random generator.
    random.seed()
    # Make the subjects.
    # Note: itertools chain on a generator is preferable to iterate over
    # the collections. This works in python 1.7.1, but not python 1.7.2.
    # The work-around is to build up the subject collection in the for
    # loop below.
    coll_sbjs = []
    for coll in COLLECTIONS:
        coll_sbjs.extend(_seed_collection(coll))

    return coll_sbjs


def clear():
    """Removes the seeded documents."""
    for coll in COLLECTIONS:
        _clear_collection(coll)


def _seed_collection(collection):
    return [_seed_subject(collection, sbj_nbr)
            for sbj_nbr in range(1, 4)]


def _clear_collection(collection):
    for sbj_nbr in range(1, 4):
        try:
            sbj = Subject.objects.get(number=sbj_nbr, project=PROJECT,
                                      collection=collection)
            sbj.delete()
        except Subject.DoesNotExist:
            pass


def _seed_subject(collection, subject_number):
    """
    If the given subject is already in the database, then the
    subject is ignored. Otherwise, a new subject is created
    and populated with detail information.

    @param collection: the subject collection
    @param subject_number: the subject number
    @return: the subject with the given collection and number
    """
    try:
        sbj = Subject.objects.get(number=subject_number, project=PROJECT,
                                  collection=collection.name)
    except Subject.DoesNotExist:
        sbj = _create_subject(collection, subject_number)

    return sbj


def _create_subject(collection, subject_number):
    subject = Subject(number=subject_number, project=PROJECT,
                      collection=collection.name)
    detail = _create_subject_detail(collection, subject)
    detail.save()
    subject.detail = detail
    subject.save()

    return subject


ETHNICITY_INCIDENCE = [15, 85]
"""
The rough US ethnicity incidence for the respective ethnicity choices.
The incidences sum to 100.
"""

RACE_INCIDENCE = [70, 15, 5, 5, 5]
"""
The rough US race incidence for the respective race choices.
The incidences sum to 100.
"""

def _create_subject_detail(collection, subject):
    # The patient demographics.
    yr = _random_int(1950, 1980)
    birth_date = datetime(yr, 7, 7, tzinfo=pytz.utc)
    # Only show one race.
    races = [_choose_race()]
    # The ethnicity is None half of the time.
    ethnicity = _choose_ethnicity()
    # The gender is roughly split.
    gender = _choose_gender(collection)
    # The weight is 100-200.
    weight = _random_int(100, 200)

    # Make the sessions.
    session_cnt = collection.visit_count

    # The modeling input parameters.
    mdl_params = dict(r1_0_val=0.7, baseline_end_idx=1)
    # The modeling object.
    modeling = Modeling(technique='Bolero', input_parameters=mdl_params,
                        results=[])

    # The registration configuration dictionary key.
    reg_cfg_key = "reg_%s" % uid.generate_string_uid()
    
    # The modeling dictionary key.
    mdl_key = "pk_%s" % uid.generate_string_uid()
    
    # The registration configuration.
    reg_cfg = Registration.Configuration(
        technique = 'ANTS',
        parameters=REG_PARAMS,
        modeling={mdl_key: modeling}
    )
    reg_cfg_dict = {reg_cfg_key: reg_cfg}
    
    # The scan sets.
    scan_sets = dict(t1=ScanSet(registration=reg_cfg_dict),
                     t2=ScanSet())
    
    # The sessions.
    sessions = [_create_session(collection, subject, sess_nbr, reg_cfg_dict)
                for sess_nbr in range(1, session_cnt + 1)]

    # The neodjuvant treatment starts a few days after the first visit.
    offset = _random_int(0, 3)
    neo_tx_begin = sessions[0].acquisition_date + timedelta(days=offset)
    # The neodjuvant treatment ends a few days before the last visit.
    offset = _random_int(0, 3)
    neo_tx_end = sessions[-1].acquisition_date - timedelta(days=offset)
    neo_tx = Treatment(treatment_type='Neoadjuvant', begin_date=neo_tx_begin,
                       end_date=neo_tx_end)
    
    # Breast patients have neodjuvant drugs.
    if isinstance(collection, Breast):
        # trastuzumab.
        trast = Drug(name='trastuzumab')
        amt = .002 * subject.number
        trast_amt = Measurement(amount=amt, unit=Weight(), per_unit=Weight(scale='k'))
        trast_dosage = Dosage(agent=trast, amount=trast_amt)
        
        # pertuzumab.
        pert = Drug(name='pertuzumab')
        amt = .006 * subject.number
        pert_amt = Measurement(amount=amt, unit=Weight(), per_unit=Weight(scale='k'))
        pert_dosage = Dosage(agent=pert, amount=pert_amt)
        
        neo_tx.dosages = [trast_dosage, pert_dosage]
    
    # The primary treatment (surgery) is a few days after the last scan.
    offset = _random_int(0, 10)
    surgery_date = sessions[-1].acquisition_date + timedelta(days=offset)
    primary_tx = Treatment(treatment_type='Primary', begin_date=surgery_date,
                           end_date=surgery_date)
    
    # Adjuvant treatment begins shortly after surgery.
    offset = _random_int(0, 3)
    adj_tx_begin = surgery_date + timedelta(days=offset)
    # Adjuvant treatment ends about two weeks later.
    offset = _random_int(10, 20)
    adj_tx_end = adj_tx_begin + timedelta(days=offset)
    adj_tx = Treatment(treatment_type='Adjuvant', begin_date=adj_tx_begin,
                       end_date=adj_tx_end)
    treatments = [neo_tx, primary_tx, adj_tx]

    # The biopsy is a few days before the first visit.
    offset = _random_int(0, 10)
    biopsy_date = sessions[0].acquisition_date - timedelta(days=offset)
    
    # The biopsy has a pathology report.
    biopsy_path = collection.create_pathology()
    biopsy = Biopsy(date=biopsy_date, pathology=biopsy_path)

    # The surgery doesn't have an outcome.
    surgery = Surgery(date=surgery_date)

    # The post-surgery assessment.
    offset = _random_int(3, 13)
    assessment_date = surgery_date + timedelta(days=offset)
    # The post-surgery evaluation has a TNM.
    assessment_tnm = _create_tnm(collection)
    evaluation = GenericEvaluation(outcomes=[assessment_tnm])
    assessment = Assessment(date=assessment_date, evaluation=evaluation)
    encounters = [biopsy, surgery, assessment]

    # Make the subject detail.
    return SubjectDetail(birth_date=birth_date, races=races, gender=gender,
                         weight=weight, ethnicity=ethnicity,
                         encounters=encounters, treatments=treatments,
                         sessions=sessions, scan_sets=scan_sets)


def _choose_race():
    # Partition the race incidence from 1 to 100 and select the race by
    # partition.
    offset = _random_int(0, 99)
    n = 0
    for i, proportion in enumerate(RACE_INCIDENCE):
        n += proportion
        if offset < n:
            # The first item in the race tuple is the database value,
            # the second is the display value.
            return choices.RACE_CHOICES[i][0]


def _choose_ethnicity():
    offset = _random_int(0, 99)
    n = 0
    for i, proportion in enumerate(ETHNICITY_INCIDENCE):
        n += proportion
        if offset < n:
            # The first item in the ethnicity tuple is the database value,
            # the second is the display value.
            return choices.ETHNICITY_CHOICES[i][0]


def _choose_gender(collection):
    if collection.name == 'Breast':
        return 'Female'
    else:
        # Half of the sarcoma subjects are male, half female.
        index = _random_int(0, 1)
        return choices.GENDER_CHOICES[index][0]


def _create_tnm(collection, prefix=None):
    grade = collection.create_grade()
    
    tumor_size_max = TNM.Size.tumor_size_choices(collection.name)[-1]
    tumor_size = _random_int(1, tumor_size_max)
    suffix_choices = TNM.Size.suffix_choices(collection.name)
    suffix_ndx = _random_int(-1, len(suffix_choices) - 1)
    if suffix_ndx < 0:
        suffix = None
    else:
        suffix = suffix_choices[suffix_ndx]
    size = TNM.Size(prefix=prefix, tumor_size=tumor_size, suffix=suffix)
    lymph_status_max = TNM.lymph_status_choices(collection.name)[-1]
    lymph_status = _random_int(0, lymph_status_max)
    metastasis = _random_boolean()
    invasion = _random_boolean()

    return TNM(tumor_type=collection.name, grade=grade, size=size,
               lymph_status=lymph_status, metastasis=metastasis,
               lymphatic_vessel_invasion=invasion)


FXL_K_TRANS_FILE_NAME = 'fxl_k_trans.nii.gz'

FXR_K_TRANS_FILE_NAME = 'fxr_k_trans.nii.gz'

DELTA_K_TRANS_FILE_NAME = 'delta_k_trans.nii.gz'

V_E_FILE_NAME = 'v_e_trans.nii.gz'

TAU_I_FILE_NAME = 'tau_i_trans.nii.gz'

COLOR_TABLE_FILE_NAME = 'etc/jet_colors.txt'

def _create_session(collection, subject, session_number, reg_cfg_dict):
    # Stagger the inter-session duration.
    date = _create_session_date(subject, session_number)

    # The bolus arrival.
    arv = int(round((0.5 - random.random()) * 4)) + AVG_BOLUS_ARRIVAL_NDX
    # Make the series list.
    series = _create_all_series(collection)
    
    # Make the scans.
    t1_scan = _create_t1_scan(subject, session_number, series, arv,
                              reg_cfg_dict)
    t2_scan = _create_t2_scan(subject, session_number, series, arv)
    scans = dict(t1=t1_scan, t2=t2_scan)
    
    # Make the session detail.
    detail = SessionDetail(bolus_arrival_index=arv, series=series,
                           scans=scans)
    
    # Save the detail, since it is not embedded.
    detail.save()

    # The session modeling results.
    for reg_cfg_key, reg_cfg in reg_cfg_dict.iteritems():
        mdl_result = _create_modeling_result(subject, session_number)
        for mdl in reg_cfg.modeling.itervalues():
          mdl.results.append(mdl_result)

    return Session(number=session_number, acquisition_date=date,
                   detail=detail)


def _create_modeling_result(subject, session_number):
    # The modeling resource name.
    resource = "pk_%s" % uid.generate_string_uid()
    
    # Add modeling parameters with a random offset.
    factor = 1 + ((random.random() - 0.5) * 0.4)
    fxl_k_trans_avg = FXL_K_TRANS_AVG * factor
    fxl_k_trans_file = _resource_filename(subject, session_number, resource,
                                          FXL_K_TRANS_FILE_NAME)
    fxl_k_trans_label_map = _create_label_map(fxl_k_trans_file)
    fxl_k_trans = ModelingParameter(average=fxl_k_trans_avg,
                                    filename=fxl_k_trans_file,
                                    label_map=fxl_k_trans_label_map)

    factor = DELTA_K_TRANS_FACTOR + ((random.random() - 0.5) * 0.4)
    fxr_k_trans_avg = fxl_k_trans_avg * factor
    fxr_k_trans_file = _resource_filename(subject, session_number, resource,
                                          FXR_K_TRANS_FILE_NAME)
    fxr_k_trans_label_map = _create_label_map(fxr_k_trans_file)
    fxr_k_trans = ModelingParameter(average=fxr_k_trans_avg,
                                    filename=fxr_k_trans_file,
                                    label_map=fxr_k_trans_label_map)

    delta_k_trans_avg = fxl_k_trans_avg - fxr_k_trans_avg
    delta_k_trans_file = _resource_filename(subject, session_number, resource,
                                            DELTA_K_TRANS_FILE_NAME)
    delta_k_trans_label_map = _create_label_map(delta_k_trans_file)
    delta_k_trans = ModelingParameter(average=delta_k_trans_avg,
                                      filename=delta_k_trans_file,
                                      label_map=delta_k_trans_label_map)

    offset = (0.5 - random.random()) * 0.2
    v_e_avg = V_E_0 + offset
    v_e_file = _resource_filename(subject, session_number, resource, V_E_FILE_NAME)
    v_e_label_map = _create_label_map(v_e_file)
    v_e = ModelingParameter(average=v_e_avg, filename=v_e_file,
                            label_map=v_e_label_map)

    offset = (0.5 - random.random()) * 0.2
    tau_i_avg = TAU_I_0 + offset
    tau_i_file = _resource_filename(subject, session_number, resource, V_E_FILE_NAME)
    tau_i_label_map = _create_label_map(tau_i_file)
    tau_i = ModelingParameter(average=tau_i_avg, filename=tau_i_file,
                                      label_map=tau_i_label_map)

    return ModelingResult(resource=resource, fxl_k_trans=fxl_k_trans, fxr_k_trans=fxr_k_trans,
                          delta_k_trans=delta_k_trans, v_e=v_e, tau_i=tau_i)


SESSION_OFFSET_RANGES = dict(
    Breast=[(0, 5), (10, 15), (25, 30), (50,60)],
    Sarcoma=[(0, 5), (10, 20), (40,50)]
)
"""The range of offsets from the initial date for the breast scan dates. """

def _create_session_date(subject, session_number):
    date_range = SESSION_OFFSET_RANGES[subject.collection][session_number - 1]
    offset = _random_int(*date_range)
    return DATE_0 + timedelta(days=offset)


def _create_all_series(collection):
    # @param collection the Breast or Sarcoma collection
    # @returns an array of series objects
    return [Series(number=number) for number in collection.series_numbers]


def _create_t1_scan(subject, session_number, series, bolus_arrival_index,
                    reg_cfg_dict):
    files = _create_scan_filenames(subject, session_number, series, 't1')
    intensity = _create_intensity(len(series), bolus_arrival_index)
    # Add a motion artifact.
    start = 12 + _random_int(0, 5)
    for i in range(start, start + 5):
        intensity.intensities[i] -= random.random() * 8
    # Make the T1 registrations.
    regs = {reg_cfg_key: _create_registration(subject, session_number, series,
                                 bolus_arrival_index)
            for reg_cfg_key in reg_cfg_dict.iterkeys()}

    return Scan(scan_type='t1', files=files, intensity=intensity, registrations=regs)


def _create_t2_scan(subject, session_number, series, bolus_arrival_index):
    files = _create_scan_filenames(subject, session_number, series, 't2')
    intensity = _create_intensity(len(series), bolus_arrival_index)
    
    return Scan(scan_type='t2', files=files, intensity=intensity)


def _create_registration(subject, session_number, series, bolus_arrival_index):
    resource = "reg_%s" % uid.generate_string_uid()
    files = _create_registration_filenames(subject, session_number, resource,
                                           series)
    intensity = _create_intensity(len(series), bolus_arrival_index)
    
    return Registration(resource=resource, files=files, intensity=intensity)


def _create_scan_filenames(subject, session_number, series, scan_type):
    # Creates the file names for the given session. The file is
    # name is given as:
    #
    # ``data/``*project*``/``*subject*``/``*session*``/scan/``*number*``/series``*number*``_``*type*``.nii.gz``
    #
    # where:
    # * *number* is the series number
    # * *type* is the scan type
    #
    # e.g.::
    #
    #     data/QIN_Test/Breast003/Session02/scan/2/series002_t1.nii.gz
    return [_scan_filename(subject, session_number, series.number, scan_type)
            for series in series]


def _create_registration_filenames(subject, session_number, resource, series):
    # Creates the file names for the given resource and series list. The file is
    # name is given as:
    #
    # ``data/``*project*``/``*subject*``/``*session*``/resource/``*name*``/series``*number*``.nii.gz``
    #
    # where:
    # * *resource* is the resource name
    # * *number* is the series number
    #
    # e.g.::
    #
    #     data/QIN_Test/Sarcoma003/Session02/resource/reg_01/series027.nii.gz
    #
    # @param subject the parent subject
    # @param session_number the session number
    # @param name the registration name
    # @param series the series array
    # @return the file name array
    return [_registration_filename(subject, session_number, series.number, resource)
            for series in series]


SESSION_TMPL = "data/%s/arc001/%s%03d_Session%02d/"

SCAN_FILE_TMPL = "series%03d_%s.nii.gz"

REG_FILE_TMPL = "series%03d.nii.gz"

SCAN_TMPL = SESSION_TMPL + "SCANS/%d/NIFTI/" + SCAN_FILE_TMPL

RESOURCE_TMPL = SESSION_TMPL + "RESOURCES/%s/%s"


def _scan_filename(subject, session_number, series_number, scan_type):
    return SCAN_TMPL % (subject.project, subject.collection, subject.number,
                        session_number, series_number, series_number, scan_type)


def _registration_filename(subject, session_number, series, name):
    resource = "reg_%s" % name
    filename = REG_FILE_TMPL % series

    return _resource_filename(subject, session_number, resource, filename)


def _resource_filename(subject, session_number, resource, filename):
    return RESOURCE_TMPL % (subject.project, subject.collection,
                            subject.number, session_number, resource, filename)

SPLITEXT_PAT = re.compile("""
    (.*?)           # The file path without the extension
    (               # The extension group
        (\.\w+)+    # The (possibly composite) extension
    )?              # The extension is optional
    $               # Anchor to the end of the file path
    """, re.VERBOSE)
"""
Regexp pattern that splits the name and extension.

:see: :meth:`splitexts`
"""


def splitexts(path):
    """
    Splits the given file path into a name and extension.
    Unlike ``os.path.splitext``, the resulting extension can be composite.
    
    Example:
    
    >>> import os
    >>> os.path.splitext('/tmp/foo.nii.gz')
    ('/tmp/foo.nii', '.gz')
    >>> from qiutil.file_helper import splitexts
    >>> splitexts('/tmp/foo.3/bar.nii.gz')
    ('/tmp/foo.3/bar', '.nii.gz')
    
    This function is lifted from the ``qiutil`` project.
    
    :param path: the file path
    :return: the *(prefix, extensions)* tuple
    """
    matches = SPLITEXT_PAT.match(path).groups()[:2]
    # Pad with an empty extension, if necessary.
    matches += (None,) * (2 - len(matches))
    
    return tuple(matches)


def _create_label_map(modeling_file):
    base, ext = splitexts(modeling_file)
    label_map = base + '_color' + ext
    
    return LabelMap(filename=label_map, color_table=COLOR_TABLE_FILE_NAME)


def _create_intensity(count, bolus_arrival_index):
    """
    @param count the number of time points
    @param bolus_arrival_index the bolus arrival series index
    @return the Intensity object
    """
    # Ramp intensity up logarithmically until two time points after
    # bolus arrival.
    top = bolus_arrival_index + 2
    intensities = [(math.log(i) * 20) + (random.random() * 5)
                   for i in range(1, top + 2)]
    arv_intensity = intensities[top]
    # Tail intensity off inverse exponentially thereafter.
    for i in range(1, count - top):
        # A negative exponential declining factor.
        factor = math.exp(-2 * (float(i)/25))
        # The signal intensity.
        intensity = (factor * arv_intensity) + (random.random() * 5)
        intensities.append(intensity)

    return Intensity(intensities=intensities)


def _random_int(low, high):
    """
    @param low the inclusive minimum value
    @param high the inclusive maximum value
    @return a random integer in the inclusive [low, high] range
    """
    return int(Decimal(random.random() * (high - low)).to_integral_value()) + low


def _random_boolean():
    """
    @return a random True or False value
    """
    if _random_int(0, 1):
        return True
    else:
        return False


if __name__ == "__main__":
    connect(db='qiprofile_test')
    seed()
