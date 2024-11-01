import math
from dataclasses import dataclass
from typing import List, Tuple


# Define a dataclass to hold survey data for each station
@dataclass
class SurveyStation:
    depth: float  # Measured depth in meters
    dip: float  # Dip in degrees
    azimuth: float  # Azimuth in degrees


# Function to convert degrees to radians
def deg_to_rad(degrees: float) -> float:
    return degrees * (math.pi / 180)


# Minimum Curvature Algorithm
def calculate_xyz(survey_data: List[SurveyStation]) -> List[Tuple[float, float, float]]:
    # Check for the number of survey stations
    if len(survey_data) == 0:
        return []

    # Initialize starting position
    x, y, z = 0.0, 0.0, 0.0
    coordinates = [(x, y, z)]  # Starting point

    if len(survey_data) == 1:
        # If there is only one measurement, calculate the endpoint based on dip and azimuth
        first_station = survey_data[0]
        depth = first_station.depth
        dip = deg_to_rad(first_station.dip)
        azi = deg_to_rad(first_station.azimuth)

        # Calculate endpoint coordinates
        delta_x = depth * math.sin(dip) * math.cos(azi)
        delta_y = depth * math.sin(dip) * math.sin(azi)
        delta_z = -depth * math.cos(dip)  # Negative because Z increases downwards

        # Calculate the endpoint based on starting point
        x += delta_x
        y += delta_y
        z += delta_z

        coordinates.append((x, y, z))  # Add endpoint

        return coordinates

    # Process each pair of consecutive survey stations
    for i in range(1, len(survey_data)):
        # Current and previous stations
        station1 = survey_data[i - 1]
        station2 = survey_data[i]

        # Convert dip and azimuth from degrees to radians
        dip1 = deg_to_rad(station1.dip)
        dip2 = deg_to_rad(station2.dip)
        azi1 = deg_to_rad(station1.azimuth)
        azi2 = deg_to_rad(station2.azimuth)

        # Measured depth increment
        delta_md = station2.depth - station1.depth

        # Calculate dogleg severity (DLS)
        cos_dls = math.cos(dip2) * math.cos(dip1) + math.sin(dip2) * math.sin(
            dip1
        ) * math.cos(azi2 - azi1)
        dls = math.acos(
            max(-1, min(1, cos_dls))
        )  # Constrain value between -1 and 1 for safety

        # Radius Factor (RF) based on DLS
        rf = 2 / dls * math.tan(dls / 2) if dls != 0 else 1

        # Calculate the incremental XYZ displacements
        delta_x = (
            rf
            * delta_md
            * (math.sin(dip1) * math.cos(azi1) + math.sin(dip2) * math.cos(azi2))
            / 2
        )
        delta_y = (
            rf
            * delta_md
            * (math.sin(dip1) * math.sin(azi1) + math.sin(dip2) * math.sin(azi2))
            / 2
        )
        delta_z = rf * delta_md * (math.cos(dip1) + math.cos(dip2)) / 2

        # Update XYZ coordinates
        x += delta_x
        y += delta_y
        z += delta_z
        coordinates.append((x, y, z))

    return coordinates


# Main function
def main():

    # Sample survey data (change this for testing)
    survey_data = [
        SurveyStation(depth=0, dip=30, azimuth=40),
        SurveyStation(depth=30, dip=30, azimuth=40),
    ]  # Only one measurement

    # Calculate XYZ coordinates for the borehole path
    xyz_coordinates = calculate_xyz(survey_data)

    # Print the calculated XYZ coordinates
    if len(xyz_coordinates) == 2:
        print(
            f"Single measurement provided. Starting Point: X={xyz_coordinates[0][0]:.3f}, "
            f"Y={xyz_coordinates[0][1]:.3f}, Z={xyz_coordinates[0][2]:.3f}"
        )
        print(
            f"Endpoint: X={xyz_coordinates[1][0]:.3f}, "
            f"Y={xyz_coordinates[1][1]:.3f}, Z={xyz_coordinates[1][2]:.3f}"
        )
    else:
        for idx, (x, y, z) in enumerate(xyz_coordinates):
            print(f"Point {idx}: X={x:.3f}, Y={y:.3f}, Z={z:.3f}")


# Run the main function
if __name__ == "__main__":
    main()
