from borehole.borehole import SurveySegment, Casing, Borehole, PathPoint

def example7_main():
        
    # Example usage
    survey_data = [
        SurveySegment(depth=0, dip=0, azimuth=0),        # Starting point
        SurveySegment(depth=10, dip=10, azimuth=30),     # Segment 1
    ]

    casing_data = [
        Casing(depth_from=2.5, depth_to=10.0, casing_radius=0.2),  # Example casing
    ]

    borehole = Borehole(
        hole_id="BH-001", 
        easting=500.0, 
        northing=1000.0, 
        elevation=200.0, 
        drilling_radius=0.1, 
        drilling_xyzpath=[], 
        drilling_survey=survey_data,
        casing=casing_data
    )
    borehole.calculate_drilling_path(interval=1)

    # Output the drilling path
    for idx, point in enumerate(borehole.drilling_xyzpath):
        print(f"Point {idx}: x={point.x:.2f}, y={point.y:.2f}, z={point.z:.2f} depth={point.depth:.2f}")



if __name__ == '__main__':
    example7_main()