# import Libraries of other lib packages
import bob.ip.base
import bob.io.base
import bob.learn.boosting

from ._library import FeatureExtractor, BoundingBox, prune_detections, overlapping_detections
from .detector import Sampler, Cascade
from .train import TrainingSet, expected_eye_positions, bounding_box_from_annotation, read_annotation_file

from .detect import default_cascade, best_detection, detect_single_face, detect_all_faces

def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources
#  from .version import externals

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
#  retval += "  - c/c++ dependencies:\n"
#  for k in sorted(externals): retval += "    - %s: %s\n" % (k, externals[k])
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
