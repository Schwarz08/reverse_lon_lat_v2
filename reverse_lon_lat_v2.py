import pandas as pd
import requests
from reverse_lon_lat_support import import_rf_db, create_coverage_polygons
import pointpats
import time as timer
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm

'''
Created by Jan Kyle Lewis T. Nolasco
'''

def reverse_lon_lat(coordinates):
    lat=coordinates[1]
    lon=coordinates[0]
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"

    #create dictionary to store api results
    api_result={}

    response = requests.get(url)

    status_code=response.status_code
    api_result["status_code"] = status_code

    #only get results of 200 OK
    if status_code == 200 and response.headers["content-type"].strip().startswith("application/json"):
        request_json=response.json()

        #get necessary api results
        api_result["place_name"]=request_json["name"]
        api_result["osm_type"]=request_json["osm_type"]
        api_result["place_rank"]=request_json["place_rank"]
        api_result["category"]=request_json["category"]
        api_result["type"]=request_json["type"]
        api_result["importance"]=request_json["importance"]
        api_result["addresstype"]=request_json["addresstype"]

    else:
        api_result["place_name"]="Api Error"
        api_result["osm_type"]="Api Error"
        api_result["place_rank"]="Api Error"
        api_result["category"]="Api Error"
        api_result["type"]="Api Error"
        api_result["importance"]="Api Error"
        api_result["addresstype"]="Api Error"

    return api_result

def create_coverage_db(rf_db, n_points, delay):
    coverage_db_rows=[]

    for index in rf_db.index:
        curr_row=list(rf_db.loc[index])
        coverage_polygon=rf_db.loc[index, "Coverage Polygon"]

        sampled_points = pointpats.random.poisson(coverage_polygon, size=n_points)

        for coverage_point in sampled_points:
            append_row=curr_row.copy()

            #append coverage point (reverse lon, lat)
            append_row.append((coverage_point[1], coverage_point[0]))

            coverage_db_rows.append(append_row)

    coverage_db = pd.DataFrame(data=coverage_db_rows, columns=list(rf_db.columns) + ["Coverage Point"])

    #setup geolocator
    geolocator = Nominatim(user_agent="test")
    geo_reverse = RateLimiter(geolocator.reverse, min_delay_seconds=delay)

    #reverse geocoding
    coverage_list=coverage_db["Coverage Point"].to_list()
    api_results=[]
    for point in tqdm(coverage_list, desc="Querying API"):
        try:
            api_results.append(geo_reverse(point).raw)
        except:
            api_results.append("API Error")
    #coverage_db["API Results"]=[geo_reverse(point).raw for point in tqdm(coverage_list)]
    coverage_db["API Results"]=api_results
    #parse api results
    api_data=["name", "addresstype", "importance"]
    for index in coverage_db.index:
        api_results=coverage_db.loc[index, "API Results"]

        if api_results=="API Error":
            pass
        else:
            for data in api_data:
                coverage_db.loc[index, data]=api_results[data]

    return coverage_db

def append_address_type(coverage_db, address_tpye_df):
    coverage_db=coverage_db.join(address_tpye_df.set_index("addresstype"), on="addresstype")

    #remove places with no name
    coverage_db.dropna(subset=["name"], inplace=True)
    #sort
    coverage_db.sort_values(by=["Sector Name", "Classification", "importance"], inplace=True)
    coverage_db.reset_index(drop=True, inplace=True)

    #drop places with importance less than the threshold
    coverage_db.drop(coverage_db.loc[coverage_db["importance"]<coverage_db["Importance Threshold"]].index,
                     inplace=True)

    #coverage_db.to_csv("coverage_db_raw_data.csv", index=False)

    #only keep the most important place and road
    coverage_db.drop_duplicates(subset=["Sector Name", "Classification"], keep="last", inplace=True)
    coverage_db.reset_index(drop=True, inplace=True)

    coverage_db_summary=pd.pivot_table(coverage_db, values=["name"], index="Sector Name", columns=["Classification"], aggfunc=pd.unique)
    coverage_db_summary.columns = coverage_db_summary.columns.droplevel()
    coverage_db_summary.to_csv("coverage_db_summary.csv")

def main():
    rf_db=import_rf_db("RF_database_test.xlsx", "LTE")

    #create coverage polygons
    rf_db=create_coverage_polygons(rf_db.copy(deep=True), 70, 1.5)

    #api query
    n_samples=10
    delay=1.05
    coverage_db=create_coverage_db(rf_db.copy(deep=True), n_samples, delay)

    #import address type data
    address_type_file_path="address_type_classification.xlsx"
    address_tpye_df=pd.read_excel(address_type_file_path, sheet_name="Address Type Classification")

    append_address_type(coverage_db.copy(deep=True), address_tpye_df.copy(deep=True))

if __name__ == "__main__":
    start = timer.time()
    main()
    end = timer.time()
    total_time = (end - start) / 60
    print(f"Elapsed Time: {total_time} mins")