import requests
import json
from geobricks_proj4_to_epsg.core.proj4_to_epsg import get_proj4_json_from_string

epsg_json = []

cached_epsg_codes = []


def create_epsg_json_file():
    with open("../data/epsg.json", "r") as f:
        projection_list = json.load(f)
        for p in projection_list:
            if p["epsg"] not in cached_epsg_codes:
                cached_epsg_codes.append(p["epsg"])
                print p["epsg"]
                proj4_text = get_proj4_from_spatialreference(p["epsg"])
                print proj4_text
                data = get_proj4_epsg_json(p["epsg"], proj4_text)
                if data is not None:
                    epsg_json.append(data)
    print "----"
    # print epsg_json
    write_json_file(epsg_json)

def get_proj4_from_spatialreference(epsg):
    r = requests.get("http://spatialreference.org/ref/epsg/"+ str(epsg) +"/proj4/")
    return r.text


def get_proj4_epsg_json(epsg, proj4_text):
    if "Not found" in proj4_text:
        return None
    return {
        "epsg": epsg,
        "proj4": get_proj4_json_from_string(proj4_text)
    }


def write_json_file(json_data):
    with open('epsg.json', 'w') as outfile:
        json.dump(json_data, outfile)

# this method clean the json produced from create_epsg_json_file(). There are no valid data
# return from the web service
def _clean_epsg_json_data():
    epsg_json_data = []
    with open("epsg.json", "r") as f:
        projection_list = json.load(f)
        for p in projection_list:
            if p is not None and "proj" in p["proj4"]:
                epsg_json_data.append(p)
    write_json_file(epsg_json_data)


#create_epsg_json_file()

#_clean_epsg_json_data()