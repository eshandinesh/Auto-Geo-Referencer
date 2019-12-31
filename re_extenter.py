from osgeo import ogr, gdal, osr
import os
from tqdm import tqdm


class Reextenter:
    def __init__(self):
        self.non_ref_longList = []
        self.non_ref_latList = []
        self.longList = []
        self.latList = []
        self.lonDict = {}
        self.latDict = {}

    # This method is used for calculating extent of a raster file
    def getExtent(self, gt, cols, rows):
        ext = []
        xarr = [0, cols]
        yarr = [0, rows]

        for px in xarr:
            for py in yarr:
                x = gt[0] + (px * gt[1]) + (py * gt[2])
                y = gt[3] + (px * gt[4]) + (py * gt[5])
                ext.append([x, y])
            yarr.reverse()
        return ext

    # This method is for creating raster format file from a geojson format.
    # Rasterization of geo-referenced geojson file
    def createFullRaster(self, pathJSON, pathRASTER):
        os.system('gdal_rasterize -of gtiff -ot byte -co alpha=yes -burn 255 -burn 0 -burn 0 -burn 100 -ts 5000 5000 -q ' + pathJSON + ' ' + pathRASTER)
        ds = gdal.Open(pathRASTER)
        gt = ds.GetGeoTransform()
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        ext = self.getExtent(gt, cols, rows)
        long = ext[0][0]
        lat = ext[0][1]
        self.longList.append(long)
        self.latList.append(lat)
        for i in range(cols):
            long = long + gt[1]
            self.longList.append(long)
            lat = lat + (gt[5])
            self.latList.append(lat)

    # This method is for creating raster format file from a geojson format.
    # Rasterization of non geo-referenced geojson file
    def createNonRefFullRaster(self, pathJSON, pathRASTER):
        os.system('gdal_rasterize -of gtiff -ot byte -co alpha=yes -burn 255 -burn 0 -burn 0 -burn 100 -ts 5000 5000 -q ' + pathJSON + ' ' + pathRASTER)
        ds = gdal.Open(pathRASTER)
        gt = ds.GetGeoTransform()
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        ext = self.getExtent(gt, cols, rows)
        long = ext[0][0]
        lat = ext[0][1]
        self.non_ref_longList.append(long)
        self.non_ref_latList.append(lat)
        for i in range(cols):
            long = long + gt[1]
            self.non_ref_longList.append(long)
            lat = lat + (gt[5])
            self.non_ref_latList.append(lat)

    # This method is used to create an updated geo-referenced geojson file.
    def generateGeoReferencedGeoJSON(self, pathNonGeoRef, georefpath):
        id_val = None
        driver = ogr.GetDriverByName("geojson")
        spatialReference = osr.SpatialReference()
        spatialReference.SetWellKnownGeogCS("WGS84")
        dataSource = driver.CreateDataSource(georefpath)

        dataSource_layer = dataSource.CreateLayer("feature", spatialReference)

        id = ogr.FieldDefn("id", ogr.OFTString)
        dataSource_layer.CreateField(id)

        uid = ogr.FieldDefn("UNQID", ogr.OFTString)
        dataSource_layer.CreateField(uid)

        did = ogr.FieldDefn("DISTRICT_ID", ogr.OFTString)
        dataSource_layer.CreateField(did)

        tid = ogr.FieldDefn("TEHSIL_ID", ogr.OFTString)
        dataSource_layer.CreateField(tid)

        rid = ogr.FieldDefn("R_I_ID", ogr.OFTString)
        dataSource_layer.CreateField(rid)

        hid = ogr.FieldDefn("HALKA_ID", ogr.OFTString)
        dataSource_layer.CreateField(hid)

        vid = ogr.FieldDefn("VILLAGE_ID", ogr.OFTString)
        dataSource_layer.CreateField(vid)

        kid = ogr.FieldDefn("KHASRA_ID", ogr.OFTString)
        dataSource_layer.CreateField(kid)

        bcode = ogr.FieldDefn("BHUCODE", ogr.OFTString)
        dataSource_layer.CreateField(bcode)

        kd = ogr.FieldDefn("KID", ogr.OFTString)
        dataSource_layer.CreateField(kd)

        featureDefn = dataSource_layer.GetLayerDefn()
        feat = ogr.Feature(featureDefn)

        driver = ogr.GetDriverByName("geojson")
        datasource = driver.Open(pathNonGeoRef)
        layer = datasource.GetLayer(0)

        for feature in tqdm(layer):
            id_val = feature.GetField("id")
            UNQID = feature.GetField("UNQID")
            DISTRICT_ID = feature.GetField("DISTRICT_ID")
            TEHSIL_ID = feature.GetField("TEHSIL_ID")
            R_I_ID = feature.GetField("R_I_ID")
            HALKA_ID = feature.GetField("HALKA_ID")
            VILLAGE_ID = feature.GetField("VILLAGE_ID")
            KHASRA_ID = feature.GetField("KHASRA_ID")
            BHUCODE = feature.GetField("BHUCODE")
            KID = feature.GetField("KID")

            geom = feature.GetGeometryRef()
            poly = ogr.Geometry(ogr.wkbMultiPolygon)
            poly1 = ogr.Geometry(ogr.wkbPolygon)
            for i in geom:

                pointCount = i.GetPointCount()
                ring = ogr.Geometry(ogr.wkbLinearRing)
                for j in range(pointCount):
                    point = i.GetPoint(j)
                    error = []
                    for k in range(len(self.non_ref_longList)):
                        error.append(abs(self.non_ref_longList[k]-point[0]))
                    index = error.index(min(error))
                    x = self.lonDict[self.non_ref_longList[index]]

                    error.clear()
                    for l in range(len(self.non_ref_latList)):
                        error.append(abs(self.non_ref_latList[l] - point[1]))
                    index = error.index(min(error))
                    y = self.latDict[self.non_ref_latList[index]]
                    ring.AddPoint(x, y, 0.0)
                poly1.AddGeometry(ring)
            poly.AddGeometry(poly1)
            feat.SetField("id", id_val)
            feat.SetField("UNQID", UNQID)
            feat.SetField("DISTRICT_ID", DISTRICT_ID)
            feat.SetField("TEHSIL_ID", TEHSIL_ID)
            feat.SetField("R_I_ID", R_I_ID)
            feat.SetField("HALKA_ID", HALKA_ID)
            feat.SetField("VILLAGE_ID", VILLAGE_ID)
            feat.SetField("KHASRA_ID", KHASRA_ID)
            feat.SetField("BHUCODE", BHUCODE)
            feat.SetField("KID", KID)
            feat.SetGeometry(poly)
            dataSource_layer.CreateFeature(feat)

    def reextenter(self, geo_ref_json_path, non_geo_ref_json_path, temp_result_path, temp_non_result_path, updated_geo_ref_json_path):
        self.non_ref_longList = []
        self.non_ref_latList = []
        self.longList = []
        self.latList = []
        self.lonDict = {}
        self.latDict = {}

        self.createFullRaster(geo_ref_json_path, temp_result_path)
        self.createNonRefFullRaster(non_geo_ref_json_path, temp_non_result_path)

        for m in range(len(self.non_ref_longList)):
            self.lonDict[self.non_ref_longList[m]] = self.longList[m]

        for n in range(len(self.non_ref_latList)):
            self.latDict[self.non_ref_latList[n]] = self.latList[n]

        self.generateGeoReferencedGeoJSON(non_geo_ref_json_path, updated_geo_ref_json_path)

