from pathlib import Path
import sys
import os

# class101 폴더를 시스템 경로에 추가
sys.path.append(str(Path(__file__).parent))

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(PACKAGE_ROOT, "resources")

from crawler import *
from ai import *

__all__ = ["crawler", "ai", "RESOURCE_DIR"]
