from dataclasses import dataclass
import numpy as np
from typing import List, Optional

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
class Borehole:
    """Represents a borehole with a unique ID, drilling radius, and drilling path."""
    hole_id: str
    easting: float  # Collar's initial X position
    northing: float  # Collar's initial Y position
    elevation: float  # Collar's initial Z position
    drilling_radius: float
    drilling_xyzpath: List[PathPoint]
    drilling_survey: List[SurveySegment]
    casing: List[Casing]

    def calculate_drilling_path(self, interval=0.10):
        """Calculates the drilling path based on the survey data at a given interval,
           including markers at casing start and end depths."""
        # Start at the collar's initial XYZ position
        self.drilling_xyzpath = [PathPoint(self.easting, self.northing, self.elevation, depth=0.0)]
        
        for i in range(1, len(self.drilling_survey)):
            # Get the current and previous survey segments
            prev_segment = self.drilling_survey[i - 1]
            curr_segment = self.drilling_survey[i]
            
            # Calculate total distance between segments
            total_distance = curr_segment.depth - prev_segment.depth
            inclination = np.radians(curr_segment.dip)
            azimuth = np.radians(curr_segment.azimuth)
            
            # Calculate displacement per interval using spherical arc approximation
            dx_per_interval = interval * np.sin(inclination) * np.sin(azimuth)  # y-axis displacement (north-south)
            dy_per_interval = interval * np.sin(inclination) * np.cos(azimuth)  # x-axis displacement (east-west)
            dz_per_interval = -interval * np.cos(inclination)                   # z-axis displacement (depth)

            # Number of intervals between survey points
            num_intervals = int(total_distance / interval)
            
            # Get the last known point
            last_point = self.drilling_xyzpath[-1]
            
            # Generate points at each interval, checking for casing boundaries
            for j in range(num_intervals + 1):
                # Calculate new XYZ position
                new_x = last_point.x + dy_per_interval
                new_y = last_point.y + dx_per_interval
                new_z = last_point.z + dz_per_interval

                # Calculate current measured depth
                current_depth = prev_segment.depth + j * interval
                
                # Check if we need to add a casing start/end point
                for casing in self.casing:
                    # Check if current depth is within a small range of casing start depth
                    if casing.depth_from <= current_depth < casing.depth_from + interval:
                        self.drilling_xyzpath.append(PathPoint(new_x, new_y, new_z, current_depth))  # Add start of casing
                        print(f"Casing starts at depth {casing.depth_from} with radius {casing.casing_radius}")
                        
                    # Check if current depth is within a small range of casing end depth
                    if casing.depth_to - interval < current_depth <= casing.depth_to:
                        self.drilling_xyzpath.append(PathPoint(new_x, new_y, new_z, current_depth))  # Add end of casing
                        print(f"Casing ends at depth {casing.depth_to}")


                # Append the new point and update the last_point reference
                new_point = PathPoint(new_x, new_y, new_z, current_depth)
                self.drilling_xyzpath.append(new_point)
                last_point = new_point

            # If there's a remaining distance less than the interval, add the final point
            remaining_distance = total_distance - (num_intervals * interval)
            if remaining_distance > 0:
                new_x = last_point.x + remaining_distance * np.sin(inclination) * np.cos(azimuth)
                new_y = last_point.y + remaining_distance * np.sin(inclination) * np.sin(azimuth)
                new_z = last_point.z - remaining_distance * np.cos(inclination)
                final_point = PathPoint(new_x, new_y, new_z, current_depth)
                self.drilling_xyzpath.append(final_point)