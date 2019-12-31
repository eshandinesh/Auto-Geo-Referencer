import os
import shutil
import argparse

from re_extenter import Reextenter


def delete_from(directory):
    for the_file in os.listdir(directory):
        file_path = os.path.join(directory, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Geo-Referencer')
    parser.add_argument('--geo_ref_path', type=str, help='Path of geo-referenced files')
    parser.add_argument('--non_geo_ref_path', type=str, help='Path of non geo-referenced files')
    parser.add_argument('--updated_geo_ref_path', type=str, help='Path of updated geo-referenced files')
    parser.add_argument('--temp_files_path', type=str, help='Path of temporary raster files')

    opt = parser.parse_args()

    georef = str(opt.geo_ref_path).strip("'")
    nongeoref = str(opt.non_geo_ref_path).strip("'")
    updated = str(opt.updated_geo_ref_path).strip("'")
    temp = str(opt.temp_files_path).strip("'")

    rextenter = Reextenter()
    for filename_geo in os.listdir(georef):
        print(filename_geo)
        geo_ref_json_path = georef + filename_geo

        for filename_non_geo in os.listdir(nongeoref):
            if filename_geo != filename_non_geo:
                continue
            else:
                print(f'Geo-Referencing of {filename_non_geo} is in progress. Please wait for a while...')

            if not os.path.exists(temp):
                os.makedirs(temp)

            delete_from(temp)

            non_geo_ref_json_path = nongeoref + filename_non_geo
            updated_geo_ref_json_path = updated + filename_non_geo
            temp_geo_raster_path = temp + "result_" + filename_geo.strip("geojson") + "tif"
            temp_non_geo_raster_path = temp + "non_result_" + filename_non_geo.strip("geojson") + "tif"

            rextenter.reextenter(geo_ref_json_path, non_geo_ref_json_path, temp_geo_raster_path, temp_non_geo_raster_path,
                                 updated_geo_ref_json_path)