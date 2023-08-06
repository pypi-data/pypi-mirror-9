import math


def nodeIDToLatLong(nodeID, resolution):
    try:
        nodeID = int(nodeID)
    except ValueError:
        raise ValueError("nodeID must be an integer or a string of an integer")

    resolution = getParsedResolution(resolution)

    return getLatitudeAndLongitude(nodeID, resolution)


def latLongToNodeID(latitude, longitude, resolution):
    try:
        latitude = float(latitude)
    except ValueError:
        raise ValueError("latitude must be a float or a string of a float")
    try:
        longitude = float(longitude)
    except ValueError:
        raise ValueError("longitude must be a float or a string of a float")

    resolution = getParsedResolution(resolution)

    return getNodeID(latitude, longitude, resolution)





def getParsedResolution(resolutionText):
    splitResolution = resolutionText.split(" ")

    if (len(splitResolution) != 2):
        raise ValueError("Resolution is invalid. It must be in the form of: Value Type. Example: 2.5 arcmin")

    try:
        resolution = float(splitResolution[0])
    except ValueError:
        raise ValueError("resolution value must be an integer or float. Example: 2.5 arcmin")

    if (splitResolution[1] == "degree"):
        return resolution
    elif (splitResolution[1] == "arcmin"):
        return resolution / 60.0
    elif (splitResolution[1] == "arcsec"):
        return resolution / 3600.0
    else:
        raise ValueError("resolution type must be degree, arcmin, or arcsec. Example: 2.5 arcmin")


def getLatitudeAndLongitude(nodeID, resolution):
    xFactor = (nodeID - 1) / (2**16)
    yFactor = (nodeID - 1) % (2**16)
    longitude = (xFactor * resolution) - 180
    latitude = (yFactor * resolution) - 90
    return latitude, longitude


def getNodeID(latitude, longitude, resolution):
    xFactor = round((longitude + 180.0) / resolution)
    yFactor = round((latitude + 90.0) / resolution)
    return int(xFactor * (2**16) + yFactor + 1)