from pathlib import Path
import sys
import os

sys.path.append(str(Path(__file__).parent))

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(PACKAGE_ROOT, "resources")

from major_crawler import *
from major_job_matrix_crawler import *

__all__ = ["major_crawler", "major_job_matrix_crawler", "RESOURCE_DIR"]
