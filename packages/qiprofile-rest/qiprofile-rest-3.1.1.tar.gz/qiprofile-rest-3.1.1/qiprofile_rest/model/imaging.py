"""
The qiprofile imaging Mongodb data model.
"""

import re
import decimal
from numbers import Number
import mongoengine
from mongoengine import (fields, signals, ValidationError)
from .. import choices

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


class Volume(mongoengine.EmbeddedDocument):
    """The MR volume."""

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

    registration = fields.DictField(
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
        the Configuration objects are embedded in the Subject.
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


class Intensity(mongoengine.EmbeddedDocument):
    """The image signal intensities for a given probe."""

    probe = fields.EmbeddedDocumentField('Probe')

    intensities = fields.ListField(field=fields.FloatField())
    """The list of volume intensities."""


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

    volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField(Volume))

    scans = fields.DictField(field=mongoengine.EmbeddedDocumentField(Scan))
    """The scan {name: object} dictionary."""

    def clean(self):
        arv = self.bolus_arrival_index
        if arv:
            if not self.volumes:
                raise ValidationError("Session does not have a volume")
            if arv < 0 or arv >= len(self.volumes):
                raise ValidationError(("Bolus arrival index does not refer"
                                       " to a valid volume index: %d") % arv)
