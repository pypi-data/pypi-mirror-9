import fiona, rasterio, mercantile, tools, json, click
from rasterio import features, Affine, coords
import numpy as np

def filterBadJSON(feat):
    for f in feat:
        try:
            yield json.loads(f)
        except:
            pass

def getBounds(features):
    xy = np.vstack(list(x['geometry']['coordinates'][0] for x in features))
    return coords.BoundingBox(xy[:,0].min(), xy[:,1].min(), xy[:,0].max(), xy[:,1].max())

def getGJSONinfo(geoJSONinfo):
    """
    Loads a lattice of GeoJSON, bounds, and creates a list mapping an on-the-fly UID w/ the actual index value.
    """
    features = list(i for i in filterBadJSON(geoJSONinfo))
    UIDs = list(feat['properties']['quadtree'] for feat in features)
    bounds = getBounds(features)
    featDimensions = int(np.sqrt(len(features)/2.0))
    
    return features, UIDs, bounds, featDimensions

def getRasterInfo(filePath):
    """
    Load the raster, and get the crs (geoJSON needs to be projected into this crs to know what part of the raster to extract)
    """
    with rasterio.open(filePath, 'r') as src:
        return src.crs, src.bounds

def loadRaster(filePath, band, bounds):
    """

    """
    with rasterio.drivers():
        with rasterio.open(filePath,'r') as src:
            oaff = src.affine
            upperLeft = src.index(bounds.left, bounds.top)
            lowerRight = src.index(bounds.right, bounds.bottom)

            return src.read_band(band, window=((upperLeft[0], lowerRight[0]),(upperLeft[1], lowerRight[1]))), oaff

def addGeoJSONprop(feat, propName, propValue):
    feat['properties'][propName] = propValue
    return feat

def getCenter(feat):
    point = np.array(feat)
    return np.mean(point[0:-1,0]), np.mean(point[0:-1,1])

def getRasterValues(geoJSON, rasArr, UIDs, bounds):
    rasInd = tools.rasterIndexer(rasArr.shape, bounds)

    indices = list(rasInd.getIndices(getCenter(feat['geometry']['coordinates'][0])) for feat in geoJSON)

    return list(
        {
            UIDs[i]: {
                'value': rasArr[inds[0], inds[1]]
            }
        } for i, inds in enumerate(indices)
    )

def batchStride(output, batchsize):
    return list(
        {
            d.keys()[0]: d[d.keys()[0]] for d in output[i:i+batchsize]
        } for i in range(0, len(output), batchsize)
    )

def upsampleRaster(rasArr, featDims, zooming=None):
    from scipy.ndimage import zoom
    if zooming and type(zooming) == int:
        zoomFactor = zooming
    else:
        zoomFactor = int(featDims / min(rasArr.shape)) * 4
    return zoom(rasArr, zoomFactor, order=1)

def projectBounds(bbox, toCRS):
    import pyproj
    toProj = pyproj.Proj(toCRS)
    xCoords = (bbox[0], bbox[2], bbox[2], bbox[0])
    yCoords = (bbox[1], bbox[1], bbox[3], bbox[1])
    outBbox = toProj(xCoords, yCoords)
    return (min(outBbox[0]),
            min(outBbox[1]),
            max(outBbox[0]),
            max(outBbox[1]))

def projectShapes(features, toCRS):
    import pyproj
    from functools import partial
    import fiona.crs as fcrs
    from shapely.geometry import shape, mapping
    from shapely.ops import transform as shpTrans

    project = partial(
        pyproj.transform,
        pyproj.Proj(fcrs.from_epsg(4326)),
        pyproj.Proj(toCRS))

    return list(
        {'geometry': mapping(
            shpTrans(
                project,
                shape(feat['geometry']))
        )} for feat in features)

def fillFacets(geoJSONpath, rasterPath, noProject, output, band, zooming, batchprint):

    geoJSON, uidMap, bounds, featDims = getGJSONinfo(geoJSONpath)

    rasCRS, rasBounds = getRasterInfo(rasterPath)

    if noProject:
        pass
    else:
        geoJSON = projectShapes(geoJSON, rasCRS)
        bounds =  projectBounds(bounds, rasCRS)

    rasArr, oaff = loadRaster(rasterPath, band, bounds)

    if min(rasArr.shape) < 4 * featDims or zooming:
        rasArr = upsampleRaster(rasArr, featDims, zooming)

    sampleVals = getRasterValues(geoJSON, rasArr, uidMap, bounds)

    if batchprint:
        sampleVals = batchStride(sampleVals, int(batchprint))

    if output:
        with open(output, 'w') as oFile:
            oFile.write(json.dumps(sampleVals))
    else:
        for feat in sampleVals:
            click.echo(json.dumps(feat))
