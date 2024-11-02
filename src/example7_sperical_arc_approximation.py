from borehole.borehole import SurveySegment, Casing, Borehole, PathPoint, Interval

def example7_main():
        
    # Example usage
    survey_data = [
        SurveySegment(depth=0, dip=0, azimuth=0),        # Starting point
        SurveySegment(depth=10, dip=45, azimuth=0),     # Segment 1
    ]

    casing_data = [
        Casing(depth_from=2.5, depth_to=10.0, casing_radius=0.2),  # Example casing
    ]

    intervals_data = [
        Interval(depth_from=0,depth_to=3.333,lithology="Sand")
    ]

    borehole = Borehole(
        hole_id="BH-001", 
        easting=500.0, 
        northing=1000.0, 
        elevation=200.0, 
        drilling_radius=0.1, 
        drilling_xyzpath=[], 
        drilling_survey=survey_data,
        casings=casing_data,
        intervals=intervals_data, 
        max_depth=10.0
    )
    borehole._calculate_depths()
    borehole.calculate_drilling_path()

    # Output the drilling path
    for idx, point in enumerate(borehole.drilling_xyzpath):
        if(point.depth is not None):
            print(f"Point {idx}: x={point.x:.2f}, y={point.y:.2f}, z={point.z:.2f} depth={point.depth:.2f}")
        else:
            print(f"Point {idx}: x={point.x:.2f}, y={point.y:.2f}, z={point.z:.2f} depth=None")



if __name__ == '__main__':
    example7_main()