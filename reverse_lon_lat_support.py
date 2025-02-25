import pandas as pd
import math
from shapely import Polygon, Point

'''
Created by Jan Kyle Lewis T. Nolasco j00829503
'''

#this function is not mine
def create_sector(center, start_angle, end_angle, radius, steps=10):
    def polar_point(origin_point, angle,  distance):
        return [origin_point.x + math.sin(math.radians(angle)) * distance, origin_point.y + math.cos(math.radians(angle)) * distance]

    if start_angle > end_angle:
        start_angle = start_angle - 360
    else:
        pass
    step_angle_width = (end_angle-start_angle) / steps
    sector_width = (end_angle-start_angle)
    segment_vertices = []

    segment_vertices.append(polar_point(center, 0,0))
    segment_vertices.append(polar_point(center, start_angle,radius))

    for z in range(1, steps):
        segment_vertices.append((polar_point(center, start_angle + z * step_angle_width,radius)))
    segment_vertices.append(polar_point(center, start_angle+sector_width,radius))
    segment_vertices.append(polar_point(center, 0,0))
    return Polygon(segment_vertices)

def import_rf_db(rf_db_file_path, rf_db_sheet_name):
    use_cols=["Site Code", "Sector Name", "Site Type", "Longitude", "Latitude", "Azimuth"]
    rf_db=pd.read_excel(rf_db_file_path, sheet_name=rf_db_sheet_name, usecols=use_cols)
    #only keep unique sectors
    rf_db.drop_duplicates(subset=["Sector Name"], inplace=True)
    #only get macro and micro sites
    rf_db = rf_db[rf_db["Site Type"].str.contains("macro|micro", case=False, na=False) == True]
    #remove sites without azimuth
    rf_db.dropna(subset=["Azimuth"], inplace=True)
    rf_db.reset_index()

    return rf_db

def create_coverage_polygons(rf_db, coverage_width, coverage_radius):
    #divide coverage width by 2
    coverage_halfwidth=coverage_width/2

    # convert search radius to crs: 4326 and increase search radius by 5% (conversions are just estimates)
    coverage_radius_4326=(coverage_radius/111.321)*1.05

    #create coverage polygons and random sample points
    rf_db["Coverage Polygon"] = ""
    #rf_db["Coverage Points"] = ""
    for index in rf_db.index:
        sector_coordinates = Point(rf_db.loc[index, "Longitude"], rf_db.loc[index, "Latitude"])
        sector_azi=rf_db.loc[index, "Azimuth"]
        coverage_polygon=create_sector(sector_coordinates, sector_azi-coverage_halfwidth, sector_azi+coverage_halfwidth,
                                       coverage_radius_4326)
        rf_db.loc[index, "Coverage Polygon"]=coverage_polygon
        '''
        coverage_points=pointpats.random.poisson(coverage_polygon, size=n_points)
        rf_db.at[index, "Coverage Points"]=coverage_points
        '''
    return rf_db

def main():
    print("")

if __name__ == "__main__":
    main()
