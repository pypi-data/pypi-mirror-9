"""
The ``interfaces`` module includes the custom QIN Nipype interface classes.
As a convenience, this  ``interfaces`` module imports all of the
non-proprietary interface classes. The proprietary interface class
:class:`qipipe.interfaces.fastfit.Fastfit` must be imported
separately from the :mod:`qipipe.interfaces.fastfit` module, e.g.::

    from qipipe.interfaces.fastfit import Fastfit

Importing ``fastfit`` in an environment that does not provide the
fastfit application will raise an ImportError.
"""

from .compress import Compress
from .copy import Copy
from .fix_dicom import FixDicom
from .gate import Gate
from .group_dicom import GroupDicom
from .lookup import Lookup
from .map_ctp import MapCTP
from .move import Move
from .mri_volcluster import MriVolCluster
from .unpack import Unpack
from .uncompress import Uncompress
from .xnat_copy import XNATCopy
from .xnat_download import XNATDownload
from .xnat_upload import XNATUpload
from .xnat_find import XNATFind
#from .update_qiprofile import UpdateQIProfile
