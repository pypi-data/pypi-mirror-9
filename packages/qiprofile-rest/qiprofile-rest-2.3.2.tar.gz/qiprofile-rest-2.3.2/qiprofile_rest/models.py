"""
The qiprofile Mongodb data model.

The model field choices are listed in the preferred display order,
most common to least common.

The data capture client has the following responsibility:

*  Validate the data upon input as determined by the model
   validation below.
   
* Resolve conflicts between data capture and the model, e.g. the
   default value or validation. 
"""

import re
import decimal
from numbers import Number
import mongoengine
from mongoengine import (fields, signals, ValidationError)
from . import choices

class User(mongoengine.Document):
    """
    The application user.
    """

    meta = dict(collection='qiprofile_user')

    email = fields.StringField()
    first_time = fields.BooleanField(default=True)

    def __str__(self):
        return self.email


class Subject(mongoengine.Document):
    """
    The patient.
    """

    meta = dict(collection='qiprofile_subject')

    project = fields.StringField(default='QIN')

    collection = fields.StringField(required=True)

    number = fields.IntField(required=True)

    detail = fields.ReferenceField('SubjectDetail')

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this Session's detail."""

        if self.detail:
            self.detail.delete()

    def __str__(self):
        return ("%s %s Subject %d" %
                (self.project, self.collection, self.number))

signals.pre_delete.connect(Subject.pre_delete, sender=Subject)


class Session(mongoengine.EmbeddedDocument):
    """The MR session (a.k.a. *study* in DICOM terminology)."""

    number = fields.IntField(required=True)

    acquisition_date = fields.DateTimeField()

    detail = fields.ReferenceField('SessionDetail')

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this Session's detail."""

        if self.detail:
            self.detail.delete()

signals.pre_delete.connect(Session.pre_delete, sender=Session)


class Series(mongoengine.EmbeddedDocument):
    """The MR series."""

    number = fields.IntField(required=True)


class LabelMap(mongoengine.EmbeddedDocument):
    """A label map with an optional associated color lookup table."""

    filename = fields.StringField(required=True)
    """The label map file path relative to the web app root."""
    
    color_table = fields.StringField()
    """The color map lookup table file path relative to the web app root."""


class ImageContainer(mongoengine.EmbeddedDocument):
    """
    The patient scan or registration.
    """

    meta = dict(allow_inheritance=True)

    files = fields.ListField(field=fields.StringField())
    """The image file pathnames relative to the web app root."""

    # TODO - is there a use case for several intensity measures
    # per container?
    intensity = fields.EmbeddedDocumentField('Intensity')


class Scan(ImageContainer):
    """The patient image scan."""
    
    SCAN_TYPES = ['t1', 't2']
    
    scan_type = fields.StringField(
        choices=SCAN_TYPES,
        max_length=choices.max_length(SCAN_TYPES),
        required=True
    )
    
    registrations = fields.DictField(
        field=mongoengine.EmbeddedDocumentField('Registration')
    )
    """
    The {key: registration} dictionary, where *key* is the
    subject registration configuration dictionary key.
    """


class Modeling(mongoengine.EmbeddedDocument):
    """
    The QIN pharmicokinetic modeling run over a consistent list of image
    containers.
    """
    
    technique = fields.StringField()

    input_parameters = fields.DictField()
    """The modeling execution input parameters."""

    results = fields.ListField(
        fields.EmbeddedDocumentField('ModelingResult')
    )
    """
    The modeling results in session number order.
    """


class ModelingResult(mongoengine.EmbeddedDocument):
    """The QIN pharmicokinetic modeling result."""

    resource = fields.StringField(required=True)
    """The modeling XNAT resource name, e.g. ``pk_R3y9``."""

    fxl_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    fxr_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    delta_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    v_e = fields.EmbeddedDocumentField('ModelingParameter')

    tau_i = fields.EmbeddedDocumentField('ModelingParameter')

    def __str__(self):
        return "Modeling %s" % self.name


class ModelingParameter(mongoengine.EmbeddedDocument):
    """The discrete modeling result."""

    filename = fields.StringField(required=True)
    """The voxel-wise mapping file path relative to the web app root."""

    average = fields.FloatField(required=True)
    """The average parameter value over all voxels."""
    
    label_map = fields.EmbeddedDocumentField('LabelMap')


class Modelable(mongoengine.EmbeddedDocument):
    
    meta = dict(allow_inheritance=True)
        
    modeling = fields.DictField(field=fields.EmbeddedDocumentField('Modeling'))
    """
    PK modeling performed on subject scans grouped by type or registrations
    grouped by registration configuration.
    """


class Registration(ImageContainer):
    """
    The patient image registration that results from processing
    the image scan.
    """
    
    class Configuration(Modelable):
        """
        The registration technique and input parameters.
        Since the configuration binds registrations across sessions,
        the Configuration objects are embedded in the SubjectDetail.
        """
        
        TECHNIQUE = ['ANTS', 'FNIRT']

        technique = fields.StringField(
            choices=TECHNIQUE,
            max_length=choices.max_length(TECHNIQUE),
            required=True
        )
        """The registration technique."""
        
        parameters = fields.DictField()
        """The registration input parameters."""


    resource = fields.StringField(required=True)
    """The registration XNAT resource name, e.g. ``reg_k3RtZ``."""


class ScanSet(Modelable):
    """
    A consistent set of scans for a given scan type. This is the concrete
    subclass of the abstract Modelable class for scans.
    
    Note: The subject holds a {scan type: scan set} dictionary. Therefore, it
    is unnecessary to redundantly have a scan type field in this ScanSet class.
    """
    
    registration = fields.DictField(
        field=fields.EmbeddedDocumentField(Registration.Configuration)
    )
    """The registration {key: configuration} dictionary."""


class SubjectDetail(mongoengine.Document):
    """
    The patient detail aggregate. The Mongodb quiprofile_subject_detail
    document embeds the subject sessions and outcomes.
    """

    meta = dict(collection='qiprofile_subject_detail')
    
    # The {scan type: ScanSet} dictionary
    scan_sets = fields.DictField(field=fields.EmbeddedDocumentField(ScanSet))

    birth_date = fields.DateTimeField()

    races = fields.ListField(
        fields.StringField(max_length=choices.max_length(choices.RACE_CHOICES),
                           choices=choices.RACE_CHOICES))

    ethnicity = fields.StringField(
        max_length=choices.max_length(choices.ETHNICITY_CHOICES),
        choices=choices.ETHNICITY_CHOICES)

    gender = fields.StringField(
        max_length=choices.max_length(choices.GENDER_CHOICES),
        choices=choices.GENDER_CHOICES)

    weight = fields.IntField()

    sessions = fields.ListField(field=fields.EmbeddedDocumentField('Session'))

    treatments = fields.ListField(field=fields.EmbeddedDocumentField('Treatment'))

    encounters = fields.ListField(field=fields.EmbeddedDocumentField('Encounter'))

    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this SubjectDetail's sessions."""

        for sess in self.sessions:
            sess.delete()


class Intensity(mongoengine.EmbeddedDocument):
    """The image signal intensities for a given probe."""

    probe = fields.EmbeddedDocumentField('Probe')

    intensities = fields.ListField(field=fields.FloatField())
    """The list of series intensities."""


class Probe(mongoengine.EmbeddedDocument):
    """The image probe to conduct a measurement."""

    description = fields.StringField()
    """The short description, e.g. ``ROI centroid``"""

    location = fields.ListField(field=fields.FloatField())
    """The (x, y, z) probe coordinates"""


class SessionDetail(mongoengine.Document):
    """The MR session detailed content."""

    meta = dict(collection='qiprofile_session_detail')

    bolus_arrival_index = fields.IntField()

    series = fields.ListField(field=mongoengine.EmbeddedDocumentField('Series'))

    scans = fields.DictField(field=mongoengine.EmbeddedDocumentField('Scan'))
    """The scan {name: object} dictionary."""

    def clean(self):
        arv = self.bolus_arrival_index
        if arv:
            if not self.series:
                raise ValidationError("Session is missing any series")
            if arv < 0 or arv >= len(self.series):
                raise ValidationError("Bolus arrival index does not refer"
                                      " to a series")


class Treatment(mongoengine.EmbeddedDocument):
    """The patient therapy, e.g. adjuvant."""

    TYPE_CHOICES = ('Neoadjuvant', 'Primary', 'Adjuvant')

    treatment_type = fields.StringField(
        max_length=choices.max_length(TYPE_CHOICES),
        choices=TYPE_CHOICES)

    begin_date = fields.DateTimeField(required=True)

    end_date = fields.DateTimeField(required=True)
    
    dosages = fields.ListField(
        field=mongoengine.EmbeddedDocumentField('Dosage')
    )


class Dosage(mongoengine.EmbeddedDocument):
    """The agent dosage."""

    agent = fields.EmbeddedDocumentField('Agent', required=True)

    amount = fields.EmbeddedDocumentField('Measurement', required=True)

    start = fields.DateTimeField()
    
    times_per_day = fields.IntField()
    
    days = fields.IntField()


class Agent(mongoengine.EmbeddedDocument):
    """A treatment agent, e.g. drug or radiation."""

    meta = dict(allow_inheritance=True)


class Drug(Agent):
    
    name = fields.StringField(required=True)
    """The official listed drug name."""


class Radiation(Agent):

    FORMS = ['photon', 'proton', 'electron', 'neutron', 'carbon ion', 'radiopharmaceutical']
    """
    The advisory radiation forms list. The client should constraion the radiation
    form choices to this list where possible, but allow for free-form text where
    necessary.
    """
    
    form = fields.StringField()


class OtherAgent(Agent):
    
    name = fields.StringField(required=True)


class Measurement(mongoengine.EmbeddedDocument):
    """
    A scientific measurement.
    
    The measurement is a quantitative amount associated with a unit.
    The unit is the Unit as captured and displayed. The amount is
    expressed as a python Decimal in unscaled units. If the constructor
    is called with a non-Decimal numeric amount, then the value is
    converted to a Decimal, e.g.::
          
        Measurement(amount=0.006, unit=Weight())
    
    is equivalent to::

        from decimal import Decimal
        Measurement(amount=Decimal(0.006), unit=Weight())
    
    :Note: the client is responsible for saving the measurement amount
    in unscaled units and converting the database amount to the preferred
    unit. For example, 40mg is saved as follows::
          
        Measurement(amount=0.04, unit=Volume())
    
    which is equivalent to::

        Measurement(amount=0.04, unit=Volume(scale='m'))
    
    When this measurement is read from the database, the client then
    converts the measurement to the preferred display value ``40mg``.
    
    The measurement unit can be qualified by a second ``per_unit``
    dimension, e.g. 2 mg/kg dosage per patient weight is expressed
    as::

        Measurement(amount=0.002, unit=Weight(), per_unit=Weight(scale='k'))
    
    :Note: the amount is a :class:`Decimal` embedded object rather than
    the broken MongoEngine ``DecimalField`` (see the :class:`Decimal`
    comment).
    """
    
    def __init__(self, *args, **kwargs):
        # Convert the amount to a Decimal, if necessary.
        # The amount can be the first positional argument
        # or a keyword argument.
        if args:
            args = list(args)
            args[0] = self._as_decimal(args[0])
        elif 'amount' in kwargs:
            kwargs['amount'] = self._as_decimal(kwargs['amount'])
        super(Measurement, self).__init__(*args, **kwargs)

    def _as_decimal(self, value):
        if isinstance(value, Number):
            return Decimal(value)
        else:
            return value
    
    amount = fields.EmbeddedDocumentField('Decimal', required=True)
    
    unit = fields.EmbeddedDocumentField('Unit')
    
    per_unit = fields.EmbeddedDocumentField('Unit')


class Decimal(mongoengine.EmbeddedDocument):
    """
    This Decimal document class is a work-around for the broken
    MongoEngine DecimalField
    (cf. https://github.com/MongoEngine/mongoengine/issues?q=is%3Aissue+is%3Aopen+decimal).
    
    Decimal has a float value and an optional precision. The default
    precision is determined as follows:
    
    * If the Decimal value is initialized with a python ``decimal.Decimal``
      or string, then the default precision is the number of decimal places
      expressed in that value, e.g.::
    
          Decimal('1.24').precision #=> 2
          Decimal(decimal.Decimal('1.4')).precision #=> 1
    
    * If the Decimal value is initialized with an integer, then the default
            precision is zero, e.g.::

                Decimal(1).precision #=> 0
    """
    # TODO - migrate to DecimalField when it is fixed in MongoEngine.
    
    def __init__(self, *args, **kwargs):
        # The positional arguments will be replaced by keyword arguments.
        if args:
            value = args[0]
            if len(args) > 1:
                precision = args[1]
            else:
                precision = None
        else:
            value = kwargs.get('value')
            precision = kwargs.get('precision')
        
        # Convert the value to a float, if necessary.
        if value != None:
            value = float(value)
        # Set the value keyword argument.
        kwargs['value'] = value
        
        # If the precision is not specified, then determine a default if
        # possible.
        if precision == None:
            if isinstance(value, decimal.Decimal):
                value_s = str(value)
                if '.' in value_s:
                    _, precision_s = value_s.split('.')
                    precision = int(precision_s)
            elif isinstance(value, int):
                precision = 0

        # Set the precision keyword argument.
        kwargs['precision'] = precision
        
        super(Decimal, self).__init__(**kwargs)

    def canonical(self):
        """
        :return: the python decimal.Decimal equivalent of this Decimal
        """
        return decimal.Decimal(str(value))

    def __repr__(self):
        """
        :return: the value as a string with decimal places truncated
            by the precision
        """
        if self.precision == None:
            return str(self.value)
        elif self.precision == 0:
            return str(int(self.value))
        else:
            pat = '%.' + ("%s" % self.precision) + 'f'
            return pat % self.value
            
    value = fields.FloatField(required=True)
    
    precision = fields.IntField()
    

class Unit(mongoengine.EmbeddedDocument):
    """
    Unit is an abstract class for the supported measurement units.
    Each unit has a scaling factor with the default scaling factor
    defined in the concrete Unit subclass. Each Unit subclass has
    the following class variables:
    
    * ``BASE`` - the standard unscaled metric unit abbreviation,
      e.g. ``m`` for the meter Extent unit.
    
    * ``SCALES`` - the recommended scaling factors, e.g. ``m`` for
       milli and ``c`` for centi.
    
    The scales are a list in preference order, e.g. the ``Extent.SCALES``
    value ``['c', 'm']`` implies that the preferred extent unit display
    is ``cm`` (centimeter) and an edit form should show the scales ``c``
    and ``m``, in that order, defaulting to ``c``. A scale of None
    signifies the scaling factor 1, e.g. the  the ``Radiation.SCALES``
    value ``[None, 'c']`` implies that the preferred radiation unit
    display is ``Gy`` (Gray) and an edit form should show the scales
    blank and ``c``, in that order, defaulting to blank (scaling factor
    1).
    
    These class variables are advisory. The client is responsible for
    displaying the base and scales and converting from a scaled value
    to an unscaled value before saving the measurement to the database.
    """

    meta = dict(allow_inheritance=True)


class Extent(Unit):

    SCALES = ['c', 'm']

    BASE = 'm'
    """The meter designator."""
    
    scale = fields.StringField(default='c')
    """The default extent is centimeter."""


class Weight(Unit):

    SCALES = ['m', 'k']

    BASE = 'g'
    """The gram designator."""
    
    scale = fields.StringField(default='m')
    """The default weight is milligram."""


class Volume(Unit):

    SCALES = ['m']

    BASE = 'l'
    """The liter designator."""
    
    scale = fields.StringField(default='m')
    """The default volume is milliliter."""


class Radiation(Unit):

    SCALES = [None, 'c']
    """The preferred radiation scale factor is 1."""

    BASE = 'Gy'
    """The Gray designator."""
    
    scale = fields.StringField()
    """The default radiation is an unscaled Gray."""


class Encounter(mongoengine.EmbeddedDocument):
    """The patient clinical encounter, e.g. biopsy."""

    meta = dict(allow_inheritance=True)

    date = fields.DateTimeField(required=True)


class Biopsy(Encounter):
    """Non-therapeutic tissue extraction resulting in a pathology report."""

    pathology = fields.EmbeddedDocumentField('Pathology', required=True)


class Surgery(Encounter):
    """Therapeutic tissue extraction which usually results in a pathology report."""

    meta = dict(allow_inheritance=True)

    pathology = fields.EmbeddedDocumentField('Pathology')


class Assessment(Encounter):
    """Generic collection of outcomes."""

    evaluation = fields.EmbeddedDocumentField('GenericEvaluation',
                                              required=True)


class BreastSurgery(Surgery):
    """Breast tumor extraction."""

    TYPE_CHOICES = ('Mastectomy', 'Lumpectomy')
    """
    The advisory surgery types list. The client should include these surgery type
    choices, but allow for free-form text where necessary.
    """

    surgery_type = fields.StringField()
    
    partial = fields.BooleanField(default=False)


class Evaluation(mongoengine.EmbeddedDocument):
    """The patient evaluation holds outcomes."""

    meta = dict(allow_inheritance=True)


class GenericEvaluation(Evaluation):
    """An unconstrained set of outcomes."""

    outcomes = fields.ListField(fields.EmbeddedDocumentField('Outcome'))


class Pathology(Evaluation):
    """The patient pathology summary."""

    meta = dict(allow_inheritance=True)

    tnm = fields.EmbeddedDocumentField('TNM')


class BreastPathology(Pathology):
    """The QIN breast patient pathology summary."""

    HER2_NEU_IHC_CHOICES = [(0, '0'), (1, '1+'), (2, '2+'), (3, '3+')]
    """The HER2 NEU IHC choices are displayed as 0, 1+, 2+, 3+."""

    class KI67Field(fields.IntField):
        def validate(self, value, clean=True):
            return value > 0 and value <= 100

    estrogen = fields.EmbeddedDocumentField('HormoneReceptorStatus')

    progesterone = fields.EmbeddedDocumentField('HormoneReceptorStatus')

    her2_neu_ihc = fields.IntField(choices=HER2_NEU_IHC_CHOICES)

    her2_neu_fish = fields.BooleanField(choices=choices.POS_NEG_CHOICES)

    ki_67 = KI67Field()


class SarcomaPathology(Pathology):
    """The QIN sarcoma patient pathology summary."""

    HISTOLOGY_CHOICES = ('Carcinosarcoma', 'Cerebellar', 'Chondrosarcoma',
                         'Clear Cell', 'Dermatofibrosarcoma', 'Fibrosarcoma',
                         'Leiomyosarcoma', 'Liposarcoma', 'MFH', 'MPNST',
                         'Osteosarcoma', 'Rhabdomyosarcoma', 'Synovial', 'Other')
    """
    The advisory histololgy list. The client should constraion the histology
    choices to this list where possible, but allow for free-form text where
    necessary.
    """

    location = fields.StringField()

    necrosis_pct = fields.EmbeddedDocumentField('NecrosisPercent')

    histology = fields.StringField()


## Clinical metrics ##

class Outcome(mongoengine.EmbeddedDocument):
    """The patient clinical outcome."""

    meta = dict(allow_inheritance=True)


class TNM(Outcome):
    """
    The TNM tumor staging. The TNM fields are as follows:
    
      * size - primary tumor size (T)

      * lymph_status - regional lymph nodes (N)

      * metastasis - distant metastasis (M)

      * grade - tumor grade (G)

      * serum_tumor_markers (S)

      * resection_boundaries (R)

      * lymphatic_vessel_invasion (L)

      * vein_invasion (V)
    
    The size is an aggregate Size field. 
    See http://www.cancer.gov/cancertopics/factsheet/detection/staging for
    an overview. See http://en.wikipedia.org/wiki/TNM_staging_system and
    http://cancerstaging.blogspot.com/ for the value definition.
        
    Note:: The size and lymph_status choices can be further constrained by
        tumor type. Since :class:`TNM` is a generic class, these constraints
        are not enforced in this TNM class. Rather, the REST client is
        responsible for enforcing additional choice constraints. The
        :meth:`TNM.lymph_status_choices` helper method can be used for
        tumor type specific choices. See :class:`TNM.Size`` for a discussion
        of the size constraints.
  """
    class Size(mongoengine.EmbeddedDocument):
        """
        The TNM primary tumor size field.
        
        Note:: The size score choices can be further constrained by tumor
            type. For example, the sarcoma tumor_size choices are 0, 1 or 2
            and suffix choices are ``a`` or ``b``. See :class:`TNM` for a
            discussion of choice constraints. The :meth:`TNM.Size.tumor_size_choices`
            and :meth:`TNM.Size.suffix_choices` helper methods can be used for
            tumor type specific choices.
        """

        PREFIXES = ['c', 'p', 'y', 'r', 'a', 'u']

        SUFFIXES = ['a', 'b', 'c']
        
        SUFFIX_CHOICES = dict(
            Any=['a', 'b', 'c'],
            Sarcoma=['a', 'b']
        )
        
        TUMOR_SIZE_CHOICES = dict(
            Any=range(0, 5),
            Sarcoma=range(0, 3)
        )

        SIZE_PAT = """
            ^(?P<prefix>c|p|y|r|a|u)?   # The prefix modifier
            T                           # The size designator
            (x |                        # Tumor cannot be evaluated
             (?P<in_situ>is) |          # Carcinoma in situ
             ((?P<tumor_size>0|1|2|3|4) # The size
              (?P<suffix>a|b|c)?        # The suffix modifier
             )
            )$
        """

        @staticmethod
        def tumor_size_choices(tumor_type=None):
            """
            @param tumor_type the optional tumor type, e.g. ``Breast``
            @return the tumor_size choices for the given type
            """
            if tumor_type not in TNM.Size.TUMOR_SIZE_CHOICES:
                tumor_type = 'Any'
            
            return TNM.Size.TUMOR_SIZE_CHOICES[tumor_type]

        @staticmethod
        def suffix_choices(tumor_type=None):
            """
            @param tumor_type the optional tumor type, e.g. ``Breast``
            @return the suffix choices for the given type
            """
            if tumor_type not in TNM.Size.SUFFIX_CHOICES:
                tumor_type = 'Any'
            
            return TNM.Size.SUFFIX_CHOICES[tumor_type]

        SIZE_REGEX = re.compile(SIZE_PAT, re.VERBOSE)
        """The TNM size validation regular expression."""

        prefix = fields.StringField(choices=PREFIXES)

        tumor_size = fields.IntField(choices=TUMOR_SIZE_CHOICES['Any'])

        class InSitu(mongoengine.EmbeddedDocument):
            INVASIVE_TYPE_CHOICES = ('ductal', 'lobular')
            """
            The advisory invasive types list. The client should constraion the invasive
            type choices to this list where possible, but allow for free-form text where
            necessary.
            """
            
            invasive_type = fields.StringField()

        in_situ = fields.EmbeddedDocumentField(InSitu)

        suffix = fields.StringField(choices=SUFFIX_CHOICES['Any'])

        def __str__(self):
            prefix = self.prefix or ''
            suffix = self.suffix or ''
            if self.in_situ:
                size = 'is'
            elif self.tumor_size:
                size = str(self.tumor_size)
            else:
                size = 'x'
            
            return "%sT%s%s" % (prefix, size, suffix)
        
        @classmethod
        def parse(klass, value):
          """
          Parses the given string into a new Size.
          
          @param value the input string
          @return the new Size object
          """
          match = klass.SIZE_REGEX.match(value)
          return klass(**match.groupdict())

        def clean(self):
            """
            Peforms document-level validation.

            @raise ValidationError if the in_situ flag is set but there is a
              tumor_size or suffix field
            """
            if self.in_situ:
                if self.tumor_size != None:
                    raise ValidationError("TNM Size with in_situ flag set to"
                                          " True cannot have tumor_size %d" %
                                          self.tumor_size)
                if self.suffix != None:
                    raise ValidationError("TNM Size with in_situ flag set to"
                                          " True cannot have a suffix %s" %
                                          self.suffix)
            return True
        
    LYMPH_STATUS_CHOICES = dict(
        Any=range(0, 4),
        Sarcoma=range(0, 2)
    )

    tumor_type = fields.StringField(required=True)

    size = fields.EmbeddedDocumentField(Size)

    # TODO - make lymph status an aggregate with suffix modifiers,
    # including 'mi'.
    lymph_status = fields.IntField(choices=LYMPH_STATUS_CHOICES['Any'])

    metastasis = fields.BooleanField(choices=choices.POS_NEG_CHOICES)

    grade = fields.EmbeddedDocumentField('Grade')

    serum_tumor_markers = fields.IntField(choices=range(0, 4))

    resection_boundaries = fields.IntField(choices=range(0, 3))

    lymphatic_vessel_invasion = fields.BooleanField()

    vein_invasion = fields.IntField(choices=range(0, 3))

    @staticmethod
    def lymph_status_choices(tumor_type=None):
        """
        @param tumor_type the optional tumor type, e.g. ``Breast``
        @return the lymph_status choices for the given type
        """
        if tumor_type not in TNM.LYMPH_STATUS_CHOICES:
            tumor_type = 'Any'
        
        return TNM.LYMPH_STATUS_CHOICES[tumor_type]


class Grade(Outcome):
    """
    The abstract tumor grade superclass, specialized for each
    tumor type.
    """

    meta = dict(allow_inheritance=True)

    composite = fields.IntField(choices=range(1, 4))


class ModifiedBloomRichardsonGrade(Grade):
    """The ModifiedBloomRichardson breast tumor grade."""

    COMPONENT_CHOICES = range(1, 4)

    tubular_formation = fields.IntField(choices=COMPONENT_CHOICES)
    
    nuclear_pleomorphism = fields.IntField(choices=COMPONENT_CHOICES)
    
    mitotic_count = fields.IntField(choices=COMPONENT_CHOICES)


class HormoneReceptorStatus(Outcome):
    """The patient estrogen/progesterone hormone receptor status."""

    class IntensityField(fields.IntField):
        def validate(self, value, clean=True):
            return value > 0 and value <= 100

    hormone = fields.StringField(required=True)

    positive = fields.BooleanField(choices=choices.POS_NEG_CHOICES)

    quick_score = fields.IntField(choices=range(0, 9))

    intensity = IntensityField()


class FNCLCCGrade(Grade):
    """The FNCLCC sarcoma tumor grade."""

    differentiation = fields.IntField(choices=range(1, 4))

    mitotic_count = fields.IntField(choices=range(1, 4))

    necrosis = fields.IntField(choices=range(0, 3))


class NecrosisPercent(Outcome):
    """The necrosis percent value or range."""
    pass


class NecrosisPercentValue(NecrosisPercent):
    """The necrosis percent absolute value."""

    value = fields.IntField(choices=range(0, 101))


class NecrosisPercentRange(NecrosisPercent):
    """The necrosis percent range."""

    class Bound(mongoengine.EmbeddedDocument):
        """
        Necrosis percent upper or lower bound abstract class.
        The subclass is responsible for adding the ``inclusive``
        field.
        """

        meta = dict(allow_inheritance=True)

        value = fields.IntField(choices=range(0, 101))


    class LowerBound(Bound):
        """Necrosis percent lower bound."""

        inclusive = fields.BooleanField(default=True)


    class UpperBound(Bound):
        """Necrosis percent upper bound."""

        inclusive = fields.BooleanField(default=False)

    start = fields.EmbeddedDocumentField(LowerBound)

    stop = fields.EmbeddedDocumentField(UpperBound)
