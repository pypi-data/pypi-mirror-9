"""
The tumor type utility classes. Every tumor type must be represented with
a utility class accessed by the :meth:`TumorType.for` method.
"""

from .models import BreastSurgery

class Breast(object):
    