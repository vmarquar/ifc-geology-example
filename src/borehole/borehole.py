"""
References:
- https://www.drillingformulas.com/minimum-curvature-method/
"""

from dataclasses import dataclass
import numpy as np
from typing import List, Optional
import wellpathpy as wp

def count_significant_figures(number):
    # Convert the number to a string
    num_str = str(number)

    # Remove leading and trailing zeros
    if '.' in num_str:
        num_str = num_str.rstrip('0').rstrip('.')  # Remove trailing zeros and decimal point if necessary
        num_str = num_str.lstrip('0')  # Remove leading zeros
    else:
        num_str = num_str.lstrip('0')  # Only remove leading zeros for integers

    # Count significant figures
    if num_str == '':
        return 0  # This would happen for 0

    # Count non-zero digits
    return len(num_str)

@dataclass
class PathPoint:
    x: float
    y: float
    z: float
    depth: Optional[float] = None  # Optional measured depth

@dataclass
class SurveySegment:
    depth: float  # Measured depth in meters
    dip: float  # Dip in degrees, 0° = horizontal, 90° = vertical down
    azimuth: float  # Azimuth in degrees, 0° = North, 90° = East, 180° = South, 270° = West

@dataclass
class Casing:
    depth_from: float  # measured depth in meters, where the casing starts
    depth_to: float    # measured depth in meters, where the casing ends
    casing_radius: float  # the radius of the casing

@dataclass
class Interval:
    depth_from: float  # measured depth in meters, where the casing starts
    depth_to: float    # measured depth in meters, where the casing ends
    lithology: str  # the radius of the casing

@dataclass
class Borehole:
    """Represents a borehole with a unique ID, drilling radius, and drilling path."""
    hole_id: str
    easting: float  # Collar's initial X position
    northing: float  # Collar's initial Y position
    elevation: float  # Collar's initial Z position
    max_depth: float
    drilling_radius: float
    drilling_xyzpath: List[PathPoint]
    drilling_survey: List[SurveySegment]
    casings: Optional[List[Casing]] = None
    intervals: Optional[List[Interval]] = None
    _drilling_depths: Optional[List[float]] = None

    def _calculate_depths(self, spacing=1):
        """
        This function calculates all necessary / relevant depths
            - at fixed spacings, to descretize the drilling path with high accuracy
            - at casing start or end points
            - at lithology boundaries / interval boundary
        """

        # 1) Add fixed spacings
        digits = max(count_significant_figures(spacing), count_significant_figures(self.max_depth))
        depths = []
        depths += list(np.arange(0.0, self.max_depth, spacing))
        depths.append(self.max_depth)
        depths = [round(d, digits) for d in depths]

        # 2) add casing start- or endpoints (if not yet in depths)
        for invl in self.casings if self.casings is not None else []:
            if(invl.depth_from not in depths):
                depths.append(invl.depth_from)
            if(invl.depth_to not in depths):
                depths.append(invl.depth_to)

        # 3) add lithology interval start- or endpoints (if not yet in depths)
        for invl in self.intervals if self.intervals is not None else []:
            if(invl.depth_from not in depths):
                depths.append(invl.depth_from)
            if(invl.depth_to not in depths):
                depths.append(invl.depth_to)

        self._drilling_depths = sorted(depths)

    def calculate_drilling_path(self, spacing=1.0):
        """
        This is a class-specific wrapper for the wellpathpy API.
        The function obtains the XYZ delta for the wellpath.
        By Default the 'minimum_curvature' algorithm is used to determine 
        the xyz values from the depth, azi, dip measurements.
        """
        # 1) Extract measured-depth, inclination (dip), and azimuth
        md = [segment.depth for segment in self.drilling_survey]
        inc = [segment.dip for segment in self.drilling_survey]
        azi = [segment.azimuth for segment in self.drilling_survey]

        # 2) Create a deviation object and calculate positional data
        dev = wp.deviation(md=md, inc=inc, azi=azi)
        pos = dev.minimum_curvature(course_length=30)

        # 3) Resample xyz positions to the relevant depths
        if(self._drilling_depths is None):
            self._calculate_depths(spacing=spacing)
        resampled = pos.resample(depths = self._drilling_depths)

        # 4) Translate the resampled positions to the georeferenced position of the collar
        georef_pos = resampled.to_wellhead(surface_easting=self.easting, surface_northing=self.northing)
        georef_pos = georef_pos.to_tvdss(datum_elevation=self.elevation)

        # 5) Convert positional data to PathPoint instances
        self.drilling_xyzpath = [PathPoint(x,y,z,md) for x,y,z,md in zip(georef_pos.easting, georef_pos.northing, georef_pos.depth, self._drilling_depths)]

pass