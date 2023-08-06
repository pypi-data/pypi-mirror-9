#!/usr/bin/env python
import os
import re
from datetime import (datetime, timedelta)
import pytz
import random
import math
from decimal import Decimal
from bunch import Bunch
from mongoengine import connect
from qiutil import uid
from qiutil.file import splitexts
from qiprofile_rest_client.model.subject import Subject
from qiprofile_rest_client.model.imaging import (
  Session, SessionDetail, Modeling, ModelingProtocol, Scan, ScanProtocol,
  Registration, RegistrationProtocol, LabelMap, Volume)
from qiprofile_rest_client.model.uom import (Measurement, Weight)
from qiprofile_rest_client.model.clinical import (
  Treatment, Drug, Dosage, Biopsy, Surgery, Assessment, GenericEvaluation,
  TNM, BreastPathology, BreastReceptorStatus, HormoneReceptorStatus,
  BreastGeneticExpression, NormalizedAssay, ModifiedBloomRichardsonGrade,
  SarcomaPathology, FNCLCCGrade, NecrosisPercentValue, NecrosisPercentRange)

PROJECT = 'QIN_Test'

class Collection(object):
    def __init__(self, name, visit_count, volume_count):
        self.name = name
        self.visit_count = visit_count
        self.volume_count = volume_count


class Breast(Collection):
    """
    The test Breast collection has four visits with 32 volumes each.
    """
    def __init__(self):
        super(Breast, self).__init__(name='Breast', visit_count=4,
                                     volume_count=32)

    def create_grade(self):
        """
        :return: the ModifiedBloomRichardson grade
        """
        tubular_formation = _random_int(1, 3)
        nuclear_pleomorphism = _random_int(1, 3)
        mitotic_count = _random_int(1, 3)

        return ModifiedBloomRichardsonGrade(tubular_formation=tubular_formation,
                                     nuclear_pleomorphism=nuclear_pleomorphism,
                                     mitotic_count=mitotic_count)

    def create_pathology(self, **opts):
        # The TNM score.
        tnm_opts = opts.pop('tnm', {})
        tnm = _create_tnm(self, 'p', **tnm_opts)

        # Make the breast hormone status results.
        hormone_receptors_opts = opts.pop('hormone_receptors', {})
        hormone_receptors = self._create_hormone_receptors(**hormone_receptors_opts)

        # Make the gene expression results.
        gene_expr_opts = opts.pop('genetic_expression', {})
        # If this subject is estrogen receptor-status-positive
        # and has no lymph nodes, then create an assay.
        if hormone_receptors.estrogen.positive and not tnm.lymph_status:
            assay_opts = opts.pop('normalized_assay', {})
            assay = self._create_normalized_assay(**assay_opts)
            gene_expr_opts['normalized_assay'] = assay
        genetic_expression = self._create_genetic_expression(**gene_expr_opts)
        
        values = dict(tnm=tnm, hormone_receptors=hormone_receptors,
                      genetic_expression=genetic_expression)
        values.update(opts)
        
        return BreastPathology(**values)

        # HER2 NEU IHC is one of 0, 1, 2, 3.
        her2_neu_ihc = _random_int(0, 3)

        # HER2 NEU FISH is True (positive) or False (negative).
        her2_neu_fish = _random_boolean()

    def _create_hormone_receptors(self, **opts):
        # The estrogen status.
        estrogen_opts = opts.pop('estrogen', {})
        estrogen = self._create_hormone_status('estrogen', **estrogen_opts)

        # The progesterone status.
        progesterone_opts = opts.pop('progesterone', {})
        progesterone = self._create_hormone_status('progesterone', **progesterone_opts)

        return BreastReceptorStatus(estrogen=estrogen, progesterone=progesterone)

    def _create_genetic_expression(self, **opts):
        # HER2 NEU IHC is one of 0, 1, 2, 3.
        her2_neu_ihc = _random_int(0, 3)

        # HER2 NEU FISH is True (positive) or False (negative).
        her2_neu_fish = _random_boolean()

        # KI67 is a percent.
        ki67 = _random_int(0, 100)
        
        values = dict(her2_neu_ihc=her2_neu_ihc, her2_neu_fish=her2_neu_fish,
                      ki67=ki67)
        values.update(opts)

        return BreastGeneticExpression(**values)

    def _create_hormone_status(self, hormone, **opts):
        opts['hormone'] = hormone
        positive = _random_boolean()
        quick_score = _random_int(0, 8)
        intensity = _random_int(0, 100)
        values = dict(positive=positive, quick_score=quick_score,
                      intensity=intensity)
        values.update(opts)

        return HormoneReceptorStatus(**values)

    def _create_normalized_assay(self, **opts):
        gstm1 = _random_int(0, 15)
        cd68 = _random_int(0, 15)
        bag1 = _random_int(0, 15)
        her2 = self._create_HER2_group()
        estrogen = self._create_estrogen_group()
        proliferation = self._create_proliferation_group()
        invasion = self._create_invasion_group()
        groups = dict(her2=her2, estrogen=estrogen,
                      proliferation=proliferation, invasion=invasion)
        values = dict(gstm1=gstm1, cd68=cd68, bag1=bag1, **groups)
        values.update(opts)

        return NormalizedAssay(**values)

    def _create_HER2_group(self):
        grb7 = _random_int(0, 15)
        her2 = _random_int(0, 15)

        return NormalizedAssay.HER2(grb7=grb7, her2=her2)

    def _create_estrogen_group(self):
        er = _random_int(0, 15)
        pgr = _random_int(0, 15)
        bcl2 = _random_int(0, 15)
        scube2 = _random_int(0, 15)

        return NormalizedAssay.Estrogen(er=er, pgr=pgr, bcl2=bcl2, scube2=scube2)

    def _create_proliferation_group(self):
        ki67 = _random_int(0, 15)
        stk15 = _random_int(0, 15)
        survivin = _random_int(0, 15)
        ccnb1 = _random_int(0, 15)
        mybl2 = _random_int(0, 15)

        return NormalizedAssay.Proliferation(ki67=ki67, stk15=stk15,
                                             survivin=survivin, ccnb1=ccnb1,
                                             mybl2=mybl2)

    def _create_invasion_group(self):
        mmp11 = _random_int(0, 15)
        ctsl2 = _random_int(0, 15)

        return NormalizedAssay.Invasion(mmp11=mmp11, ctsl2=ctsl2)


class Sarcoma(Collection):
    """
    The test Sarcoma collection has three visits with 40 volumes each.

    Note: the AIRC Sarcoma scan count and numbering scheme varies.
    """

    def __init__(self):
        super(Sarcoma, self).__init__(name='Sarcoma', visit_count=3,
                                      volume_count=40)

    def create_grade(self):
        """
        :return: the FNCLCC grade
        """
        differentiation = _random_int(1, 3)
        mitotic_count = _random_int(1, 3)
        necrosis = _random_int(0, 2)

        return FNCLCCGrade(differentiation=differentiation,
                           mitotic_count=mitotic_count, necrosis=necrosis)

    def create_pathology(self, **opts):
        # The TNM score.
        tnm = _create_tnm(self, 'p', **opts)

        # The tumor site.
        location = 'Thigh'

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

        return SarcomaPathology(tnm=tnm, location=location,
                                necrosis_pct=necrosis_pct, histology=histology)


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

# The modeling input parameters.
MODELING_INPUT_PARAMS = dict(r1_0_val=0.7, baseline_end_idx=1)

PROTOCOLS = Bunch()

def seed():
    """
    Populates the MongoDB database named ``qiprofile_test`` with
    three subjects each of the ``Breast`` and ``Sarcoma`` collection.

    :Note: existing subjects are not modified. In order to refresh the
      seed subjects, drop the ``qiprofile_test`` database first.

    :return:: three :obj:`PROJECT` subjects for each collection in
        :obj:`COLLECTIONS`
    """
    # Initialize the pseudo-random generator.
    random.seed()
    
    # Make the protocols.
    PROTOCOLS.update(_get_or_create_protocols())
    
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

    :param collection: the subject collection
    :param subject_number: the subject number
    :return: the subject with the given collection and number
    """
    try:
        sbj = Subject.objects.get(number=subject_number, project=PROJECT,
                                  collection=collection.name)
    except Subject.DoesNotExist:
        sbj = _create_subject(collection, subject_number)

    return sbj


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

def _get_or_create_protocols():
    # The modeling protocol.
    bolero_defs = dict(input_parameters=MODELING_INPUT_PARAMS)
    bolero, _ = ModelingProtocol.objects.get_or_create(
        technique='Bolero', defaults=bolero_defs
    )
    scan_defs = dict(orientation='axial')
    # The T1 scan protocol.
    t1, _ = ScanProtocol.objects.get_or_create(scan_type='T1',
                                               defaults=scan_defs)
    # The T2 scan protocol.
    t2, _ = ScanProtocol.objects.get_or_create(scan_type='T2',
                                               defaults=scan_defs)
    # The registration protocol.
    ants_defs = dict(parameters=REG_PARAMS)
    ants, _ = RegistrationProtocol.objects.get_or_create(technique='ANTS',
                                                         defaults=ants_defs)
    
    return dict(t1=t1, t2=t2, bolero=bolero, ants=ants)


def _create_subject(collection, subject_number):
    # The subject with just a secondary key.
    subject = Subject(project=PROJECT, collection=collection.name,
                      number=subject_number)
    
    # The patient demographics.
    yr = _random_int(1950, 1980)
    subject.birth_date = datetime(yr, 7, 7, tzinfo=pytz.utc)
    # Only show one race.
    subject.races = [_choose_race()]
    # The ethnicity is None half of the time.
    subject.ethnicity = _choose_ethnicity()
    # The gender is roughly split.
    subject.gender = _choose_gender(collection)
    # The weight is between 100 and 200.
    subject.weight = _random_int(100, 200)

    # The sessions.
    subject.sessions = [_create_session(collection, subject, i + 1)
                for i in range(collection.visit_count)]

    # The neodjuvant treatment starts a few days after the first visit.
    offset = _random_int(0, 3)
    neo_tx_begin = subject.sessions[0].acquisition_date + timedelta(days=offset)
    # The neodjuvant treatment ends a few days before the last visit.
    offset = _random_int(0, 3)
    neo_tx_end = subject.sessions[-1].acquisition_date - timedelta(days=offset)
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
    surgery_date = subject.sessions[-1].acquisition_date + timedelta(days=offset)
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
    
    # Add the treatments.
    subject.treatments = [neo_tx, primary_tx, adj_tx]

    # The biopsy is a few days before the first visit.
    offset = _random_int(0, 10)
    biopsy_date = subject.sessions[0].acquisition_date - timedelta(days=offset)

    # Force the first breast patient to be free of lymph nodes,
    # since we want at least one patient with a normalized assay.
    opts = {}
    if isinstance(collection, Breast) and subject.number == 1:
        opts['hormone_receptors'] = dict(estrogen=dict(positive=True))
        opts['tnm'] = dict(lymph_status=0)
    # The biopsy has a pathology report.
    biopsy_path = collection.create_pathology(**opts)
    biopsy = Biopsy(date=biopsy_date, pathology=biopsy_path)

    # The surgery has a pathology report.
    surgery_path = collection.create_pathology(**opts)
    surgery = Surgery(date=surgery_date, pathology=surgery_path)

    # The post-surgery assessment.
    offset = _random_int(3, 13)
    assessment_date = surgery_date + timedelta(days=offset)
    # The post-surgery evaluation has a TNM.
    assessment_tnm = _create_tnm(collection)
    evaluation = GenericEvaluation(outcomes=[assessment_tnm])
    assessment = Assessment(date=assessment_date, evaluation=evaluation)
    
    # Add the encounters.
    subject.encounters = [biopsy, surgery, assessment]

    # Save the subject.
    subject.save()
    
    return subject


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
            return Subject.RACE_CHOICES[i][0]


def _choose_ethnicity():
    offset = _random_int(0, 99)
    n = 0
    for i, proportion in enumerate(ETHNICITY_INCIDENCE):
        n += proportion
        if offset < n:
            # The first item in the ethnicity tuple is the database value,
            # the second is the display value.
            return Subject.ETHNICITY_CHOICES[i][0]


def _choose_gender(collection):
    if collection.name == 'Breast':
        return 'F'
    else:
        # Half of the sarcoma subjects are male, half female.
        index = _random_int(0, 1)
        return Subject.GENDER_CHOICES[index][0]


def _create_tnm(collection, prefix=None, **opts):
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

    # The value dictionary.
    values = dict(tumor_type=collection.name, grade=grade, size=size,
                  lymph_status=lymph_status, metastasis=metastasis,
                  lymphatic_vessel_invasion=invasion)
    # The options override the random values.
    values.update(opts)

    return TNM(**values)


FXL_K_TRANS_FILE_NAME = 'fxl_k_trans.nii.gz'

FXR_K_TRANS_FILE_NAME = 'fxr_k_trans.nii.gz'

DELTA_K_TRANS_FILE_NAME = 'delta_k_trans.nii.gz'

V_E_FILE_NAME = 'v_e_trans.nii.gz'

TAU_I_FILE_NAME = 'tau_i_trans.nii.gz'

COLOR_TABLE_FILE_NAME = 'etc/jet_colors.txt'

def _create_session(collection, subject, session_number):
    """
    Returns a new Session object which includes the following:
    * a T1 scan with a registration
    * a T2 scan
    * a modeling result for the registration
    """
    # Stagger the inter-session duration.
    date = _create_session_date(subject, session_number)
    # Make the session detail.
    detail = _create_session_detail(collection, subject, session_number)
    # Save the detail first, since it is not embedded and we need to
    # set the detail reference to make the session.
    detail.save()

    # The session modeling objects.
    modelings = _create_modeling(subject, session_number)

    return Session(acquisition_date=date, modelings=[modelings], detail=detail)


def _create_session_detail(collection, subject, session_number):
    """
    Returns a new SessionDetail object which includes the following:
    * a T1 scan with a registration
    * a T2 scan
    * a modeling result for the registration
    """
    # The bolus arrival.
    arv = int(round((0.5 - random.random()) * 4)) + AVG_BOLUS_ARRIVAL_NDX
    # Make the scans.
    t1 = _create_t1_scan(collection, subject, session_number, arv)
    t2 = _create_t2_scan(collection, subject, session_number)
    scans = [t1, t2]

    # Return the session detail.
    return SessionDetail(scans=scans)


def _create_modeling(subject, session_number):
    # The modeling resource name.
    resource = "pk_%s" % uid.generate_string_uid()

    # Add modeling parameters with a random offset.
    factor = 1 + ((random.random() - 0.5) * 0.4)
    fxl_k_trans_avg = FXL_K_TRANS_AVG * factor
    fxl_k_trans_file = _resource_filename(subject, session_number, resource,
                                          FXL_K_TRANS_FILE_NAME)
    fxl_k_trans_label_map = _create_label_map(fxl_k_trans_file)
    fxl_k_trans = Modeling.ParameterResult(average=fxl_k_trans_avg,
                                           filename=fxl_k_trans_file,
                                           label_map=fxl_k_trans_label_map)

    factor = DELTA_K_TRANS_FACTOR + ((random.random() - 0.5) * 0.4)
    fxr_k_trans_avg = fxl_k_trans_avg * factor
    fxr_k_trans_file = _resource_filename(subject, session_number, resource,
                                          FXR_K_TRANS_FILE_NAME)
    fxr_k_trans_label_map = _create_label_map(fxr_k_trans_file)
    fxr_k_trans = Modeling.ParameterResult(average=fxr_k_trans_avg,
                                           filename=fxr_k_trans_file,
                                           label_map=fxr_k_trans_label_map)

    delta_k_trans_avg = fxl_k_trans_avg - fxr_k_trans_avg
    delta_k_trans_file = _resource_filename(subject, session_number, resource,
                                            DELTA_K_TRANS_FILE_NAME)
    delta_k_trans_label_map = _create_label_map(delta_k_trans_file)
    delta_k_trans = Modeling.ParameterResult(average=delta_k_trans_avg,
                                             filename=delta_k_trans_file,
                                             label_map=delta_k_trans_label_map)

    offset = (0.5 - random.random()) * 0.2
    v_e_avg = V_E_0 + offset
    v_e_file = _resource_filename(subject, session_number, resource, V_E_FILE_NAME)
    v_e_label_map = _create_label_map(v_e_file)
    v_e = Modeling.ParameterResult(average=v_e_avg, filename=v_e_file,
                                   label_map=v_e_label_map)

    offset = (0.5 - random.random()) * 0.2
    tau_i_avg = TAU_I_0 + offset
    tau_i_file = _resource_filename(subject, session_number, resource, V_E_FILE_NAME)
    tau_i_label_map = _create_label_map(tau_i_file)
    tau_i = Modeling.ParameterResult(average=tau_i_avg, filename=tau_i_file,
                                     label_map=tau_i_label_map)
    
    result = dict(fxl_k_trans=fxl_k_trans, fxr_k_trans=fxr_k_trans,
                  delta_k_trans=delta_k_trans, v_e=v_e, tau_i=tau_i)

    return Modeling(protocol=PROTOCOLS.bolero,
                    source=Modeling.Source(registration=PROTOCOLS.ants),
                    resource=resource, result=result)

SESSION_OFFSET_RANGES = dict(
    Breast=[(0, 5), (10, 15), (25, 30), (50,60)],
    Sarcoma=[(0, 5), (10, 20), (40,50)]
)
"""The range of offsets from the initial date for the breast scan dates. """

def _create_session_date(subject, session_number):
    date_range = SESSION_OFFSET_RANGES[subject.collection][session_number - 1]
    offset = _random_int(*date_range)
    return DATE_0 + timedelta(days=offset)


def _create_t1_scan(collection, subject, session_number, bolus_arrival_index):
    # Make the volume image file names.
    filenames = [_scan_filename(subject, session_number, 1, i+1)
                 for i in range(collection.volume_count)]
    # Make the average intensity values.
    intensities = _create_intensities(collection.volume_count, bolus_arrival_index)
    # Add a motion artifact.
    _add_motion_artifact(intensities)
    # Make the volumes.
    volumes = [Volume(filename=filenames[i], average_intensity=intensities[i])
               for i in range(collection.volume_count)]   
    
    # Make the T1 registration.
    reg = _create_registration(collection, subject, session_number,
                               bolus_arrival_index)

    return Scan(number=1, protocol=PROTOCOLS.t1, volumes=volumes, registrations=[reg])


def _create_t2_scan(collection, subject, session_number):
    # Make the volume image file names.
    filename = _scan_filename(subject, session_number, 2, 1)
    # Make the volume.
    volumes = [Volume(filename=filename)]   

    return Scan(number=2, protocol=PROTOCOLS.t2, volumes=volumes)


def _create_registration(collection, subject, session_number, bolus_arrival_index):
    # The XNAT resource name.
    resource = "reg_%s" % uid.generate_string_uid()
    # Make the volume image file names.
    filenames = [_registration_filename(subject, session_number, resource, i+1)
                 for i in range(collection.volume_count)]
    # Make the average intensity values.
    intensities = _create_intensities(collection.volume_count, bolus_arrival_index)
    # Make the volumes.
    volumes = [Volume(filename=filenames[i], average_intensity=intensities[i])
               for i in range(collection.volume_count)]   

    return Registration(protocol=PROTOCOLS.ants, resource=resource, volumes=volumes)


SESSION_TMPL = "data/%s/arc001/%s%03d_Session%02d/"

SCAN_FILE_TMPL = "volume%03d.nii.gz"

REG_FILE_TMPL = "volume%03d.nii.gz"

SCAN_TMPL = SESSION_TMPL + "SCANS/%d/NIFTI/" + SCAN_FILE_TMPL

RESOURCE_TMPL = SESSION_TMPL + "RESOURCES/%s/%s"


def _scan_filename(subject, session, scan, volume):
    """
    Creates the file name for the given scan volume hierarchy. The file
    name is given by:

    ``data/``*project*``/``*subject*``/``*session*``/scan/``*scan*``/volume``*volume*``.nii.gz``

    e.g.::

        data/QIN_Test/Breast003/Session02/scan/2/volume002.nii.gz

    :param subject: the Subject object
    :param session: the session number
    :param scan: the scan number
    :param volume: the volume number
    """
    return SCAN_TMPL % (subject.project, subject.collection, subject.number,
                        session, scan, volume)


def _registration_filename(subject, session, resource, volume):
    """
    Creates the file name for the given registration volume hierarchy.
    The file name is given by:

    ``data/``*project*``/``*subject*``/``*session*``/resource/``*resource*``/volume``*volume*``.nii.gz``

    e.g.::

        data/QIN_Test/Breast003/Session02/resource/reg_uHjY3/volume002.nii.gz

    :param subject: the Subject object
    :param session: the session number
    :param resource: the registration resource name
    :param volume: the volume number
    """
    filename = REG_FILE_TMPL % volume

    return _resource_filename(subject, session, resource, filename)


def _resource_filename(subject, session, resource, filename):
    """
    Creates the file name for the given resource hierarchy and file base name.
    The file name is given by:

    ``data/``*project*``/``*subject*``/``*session*``/resource/``*resource*``/``*filename*

    e.g.::

        data/QIN_Test/Breast003/Session02/resource/reg_uHjY3/volume002.nii.gz

    :param subject: the Subject object
    :param session: the session number
    :param resource: the resource name
    :param filename: the resource file base name
    """
    return RESOURCE_TMPL % (subject.project, subject.collection,
                            subject.number, session, resource, filename)


def _create_label_map(modeling_file):
    base, ext = splitexts(modeling_file)
    label_map = base + '_color' + ext

    return LabelMap(filename=label_map, color_table=COLOR_TABLE_FILE_NAME)


def _create_intensities(count, bolus_arrival_index):
    """
    :param count: the number of time points
    :param bolus_arrival_index: the bolus arrival volume index
    :return: the intensities array
    """
    # Ramp intensity up logarithmically (+ or - up to 5) until two time
    # points after bolus arrival.
    top = bolus_arrival_index + 2
    intensities = [(math.log(i + 1) * 20) + (random.random() * 5)
                   for i in range(top + 1)]
    top_intensity = intensities[top]
    
    # Tail intensity off inverse exponentially thereafter.
    for i in range(count - top - 1):
        # A negative exponential declining factor.
        factor = math.exp(-2 * (float(i + 1)/25))
        # The signal intensity.
        intensity = (factor * top_intensity) + (random.random() * 5)
        intensities.append(intensity)

    return intensities


def _add_motion_artifact(intensities):
    """
    Introduces a blip in the given intensity values. Five intensity values
    roughly halfway into the sequence are skewed slightly downward.
    
    :param intensities: the intensity values
    """
    start = int(len(intensities) / 2) + _random_int(-2, 2)
    for i in range(start, start + 5):
        intensities[i] -= random.random() * 8


def _random_int(low, high):
    """
    :param low: the inclusive minimum value
    :param high: the inclusive maximum value
    :return: a random integer in the inclusive [low, high] range
    """
    return int(Decimal(random.random() * (high - low)).to_integral_value()) + low


def _random_boolean():
    """
    :return: a random True or False value
    """
    if _random_int(0, 1):
        return True
    else:
        return False


if __name__ == "__main__":
    connect(db='qiprofile_test')
    seed()
