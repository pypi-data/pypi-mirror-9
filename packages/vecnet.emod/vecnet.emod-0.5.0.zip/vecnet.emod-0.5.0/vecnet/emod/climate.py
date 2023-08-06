#!/usr/bin/python
#
# This file is part of the vecnet.emod package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/vecnet.emod
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import struct
from StringIO import StringIO
import datetime

class ClimateDataFile:
    def __init__(self, metaData=None, nodeIDs=None, climateData=None):
        nodeIDsTypeErrorMessage = "Node id must be an integer, a string that represents an integer, a list, or a tuple."
        self.nodeIDs = []
        if nodeIDs:  # If not empty
            if isinstance(nodeIDs, (list, tuple)):
                for node in range(len(nodeIDs)):
                    try:
                        self.nodeIDs.append(str(int(nodeIDs[node])))
                    except:
                        raise ValueError("Value in nodeIDs is not valid (string or integer)")
            elif isinstance(nodeIDs, (str, unicode)):
                try:
                    int(nodeIDs)
                    self.nodeIDs.append(nodeIDs)
                except ValueError:
                    raise ValueError(nodeIDsTypeErrorMessage)
            elif isinstance(nodeIDs, int):
                self.nodeIDs.append(str(nodeIDs))
            else:
                raise TypeError(nodeIDsTypeErrorMessage)
                
        self.climateData = {}
        if climateData: # If not empty
            if isinstance(climateData, dict):
                for key in climateData:
                    try:
                        self.climateData[str(key)] = climateData[key]
                    except:
                        raise ValueError("Key in climateData is not valid (string or integer)")
            else:
                raise TypeError("Climate data must be a dictionary.")
        self.otherJsonCategories = {}
        self.otherMetaData = {}

        if not self.checkMetaData(metaData):
            self.metaDataIsGood = False
        else:
            self.metaDataIsGood = True


        

            

    # Takes in a json file name and a bin file name and fills the associated properties from the file
    def load(self, inputJson, inputBinary):
        # Check for valid files and return them
        jsonFile = self.returnFile(inputJson, "json")
        jsonData = json.load(jsonFile)
        binFile = self.returnFile(inputBinary, "bin")

        # Check main json sections
        metaData = {}
        self.otherJsonCategories = {}
        self.otherMetaData = {}
        if 'Metadata' in jsonData:
            metaData = jsonData['Metadata']
        else:
            raise KeyError("Metadata not in supplied json file")
        if 'NodeOffsets' in jsonData:
            nodeOffsetsJson = jsonData['NodeOffsets']
        else:
            raise KeyError("NodeOffsets is not in supplied json file")
        for item in jsonData:
            if item != 'Metadata' and item != 'NodeOffsets':
                self.otherJsonCategories[item] = jsonData[item]

        # Check metaData subsections
        self.checkMetaData(metaData)

        self.nodeIDs = []
        for node in range(self.nodeCount):
            try:
                nodeID = nodeOffsetsJson[node*16:node*16+8] # ie 0-7 for first id
            except IndexError:
                raise IndexError("There are more nodes than node offsets in the json.")
            self.nodeIDs.append(self.hexStringToDecimalString(nodeID))

        data = binFile.read()
        self.climateData = {}
        for node in range(self.nodeCount):
            dataSet = []
            for dataPoint in range(self.dataValueCount):
                start = node * self.dataValueCount * 4 + dataPoint * 4
                end = node * self.dataValueCount * 4 + dataPoint * 4 + 4
                if len(data[start:end]) < 4:
                    raise ValueError("Either the json file has too many nodes/values, or bin file has too little data")
                tupleValue = struct.unpack('f', data[start:end])
                if not isinstance(tupleValue[0], float):
                    raise ValueError("Non float found in bin file")
                dataSet.append(tupleValue[0])
            self.climateData[self.nodeIDs[node]] = dataSet
        
        self.metaDataIsGood = True
        jsonFile.close()
        binFile.close()






    # Takes a json file name and creates a json file using the stored metadata and node offsets
    def save(self, jsonFileName, binFileName):
        if not isinstance(jsonFileName, (str, unicode)):
            raise TypeError("jsonFileName must be a string")
        if not isinstance(binFileName, (str, unicode)):
            raise TypeError("binFileName must be a string")

        jsonExtension = jsonFileName.split(".")[-1]
        if jsonExtension != "json":
            raise TypeError("json files must end with .json")
        binExtension = binFileName.split(".")[-1]
        if binExtension != "bin":
            raise TypeError("bin files must end with .bin")
        
        # Check if we can save
        if not self.metaDataIsGood:
            raise ValueError("No data has been loaded or created yet.")
        if not self.areNodesEqualLength():
            raise ValueError("Climate data nodes have a different number of datapoints.")

        # Need to update the node value count before we save
        self.dataValueCount = len(self.climateData[self.nodeIDs[0]])

        # Save json file
        metaData = {}
        metaData['DateCreated'] = self.dateCreated
        metaData['Tool'] = self.tool
        metaData['Author'] = self.author
        metaData['IdReference'] = self.idReference
        metaData['NodeCount'] = self.nodeCount
        metaData['DatavalueCount'] = self.dataValueCount
        metaData['UpdateResolution'] = self.updateResolution
        metaData['OriginalDataYears'] = self.originalDataYears
        metaData['StartDayOfYear'] = self.startDayOfYear
        metaData['DataProvenance'] = self.dataProvenance
        for item in self.otherMetaData:
            metaData[item] = self.otherMetaData[item]

        # Fill node offsets json
        nodeOffsetsJson = ""
        for node in range(self.nodeCount):
            nodeOffset = self.decimalStringToHexString(str(node*self.dataValueCount*4))
            if len(self.nodeIDs) != self.nodeCount:
                raise ValueError("Node count is " + str(self.nodeCount) + ", but there are " + str(len(self.nodeIDs))
                                 + " node ids. Either incorrect metadata was given, some data was not given, or too "
                                 + " much or redundant data was given.")
            nodeOffsetsJson = nodeOffsetsJson + self.decimalStringToHexString(self.nodeIDs[node]) + nodeOffset

        with open(jsonFileName, 'w') as fp:
            jsonFile = fp
            jsonData = {'Metadata':metaData, 'NodeOffsets':nodeOffsetsJson}
            for item in self.otherJsonCategories:
                jsonData[item] = self.otherJsonCategories
            jsonFile.write(json.dumps(jsonData, sort_keys=True, indent=4))
        
        # Save bin file
        with open(binFileName, 'wb') as fp:
            binFile = fp
            for node in range(self.nodeCount):
                for dataPoint in range(self.dataValueCount):
                    target = self.climateData[self.nodeIDs[node]][dataPoint]
                    binFile.write(struct.pack('f',target))
                    





    # Takes a dictionary that should be filled with all the required metadata, and fill the corresponding variables
    def changeMetaData(self, metaData):
        # Empty the old unrequired metadata
        self.otherJsonCategories = {}
        self.otherMetaData = {}
        # If all the metaData is ok, it will set all appropriate variables
        if not self.checkMetaData(metaData):
            raise ValueError("Metadata is empty.")
        else:
            self.metaDataIsGood = True






    # Add a node based on a node id given as either an int or a string
    def addNode(self, nodeID, data):
        # Make sure the nodeID is valid
        newNodeID = self.returnValidNodeID(nodeID)
        
        # Make sure newNodeID doesn't already exist
        if not self.indexOfNodeID(newNodeID) == -1:
            raise ValueError("Node was not added. Node id already exists. Try adding new data to it, or removing it first.")
        
        # Make sure the data is valid
        # https://github.com/vecnet/emod.weather/issues/9 - tuples are indeed ordered
        if isinstance(data, (list, tuple)):
            self.nodeIDs.append(newNodeID)
            self.climateData[newNodeID] = list(data)
            self.nodeCount = self.nodeCount + 1
        else:
            raise TypeError("Data must be a list or a tuple.")

        if not self.areNodesEqualLength():
            self.dataValueCount = "NA until nodes have equal datapoints."
        else:
            self.dataValueCount = len(self.climateData[self.nodeIDs[0]])






    # Remove a node based on node id given as either an int or a string
    def removeNode(self, nodeID):
        # Check for valid node id
        targetNodeID = self.returnValidNodeID(nodeID)
        nodeIDIndex = self.indexOfNodeID(targetNodeID)
        if nodeIDIndex == -1:
            raise ValueError("Node id " + targetNodeID + " does not exist.")
        del self.nodeIDs[nodeIDIndex]
        try:
            del self.climateData[targetNodeID]
        except KeyError:
            raise KeyError("Node id " + targetNodeID + " has not been added to climateData.") # This should not happen unless you manually add the node id instead of using addNode or something similar.
        
        self.nodeCount = self.nodeCount - 1
        
        if not self.areNodesEqualLength():
            self.dataValueCount = "NA until nodes have equal datapoints."
        else:
            self.dataValueCount = len(self.climateData[self.nodeIDs[0]])
            





    # Add data to an existing node using nodeID to determine which node and startingIndex to determine where to place
    # the data (-1 means the end). Data can be a float, list, or tuple.
    def addDataToNode(self, nodeID, data, startingIndex=-1):
        # Check for valid node id
        targetNodeID = self.returnValidNodeID(nodeID)

        # Check if node id has yet to be added
        if self.indexOfNodeID(targetNodeID) == -1:
            raise LookupError("Node id " + targetNodeID + " does not exist yet. Use addNode(nodeID, data).")

        if startingIndex == -1: # Aka the end
            startingIndex = len(self.climateData[targetNodeID])
        elif startingIndex > len(self.climateData[targetNodeID]):
            raise ValueError("Starting index is too large.")
        elif startingIndex < 0:
            raise ValueError("Starting index is negative.")

        # Make sure the data is valid
        if isinstance(data, (list, tuple)):
            # Take everything before startingIndex, then add data, and then add everything else that was in climateData
            self.climateData[targetNodeID] = self.climateData[targetNodeID][0:startingIndex] + list(data) + \
                                             self.climateData[targetNodeID][startingIndex:len(self.climateData[targetNodeID])]
        elif isinstance(data, float):
            # Basically the same as above
            self.climateData[targetNodeID] = self.climateData[targetNodeID][0:startingIndex] + [data] + \
                                             self.climateData[targetNodeID][startingIndex:len(self.climateData[targetNodeID])]
        else:
            raise TypeError("Data must be a list, tuple, or float.")

        if not self.areNodesEqualLength():
            self.dataValueCount = "NA until nodes have equal datapoints."
        else:
            self.dataValueCount = len(self.climateData[self.nodeIDs[0]])





    # Remove data from an existing node using nodeID to determine which node and startingIndex and
    # endingIndex (-1 means the end) to determine what data to remove
    def removeDataFromNode(self, nodeID, startingIndex, endingIndex=-1):
        # Check for valid node id
        targetNodeID = self.returnValidNodeID(nodeID)

        # Check if node id has yet to be added
        if self.indexOfNodeID(targetNodeID) == -1:
            raise LookupError("Node id " + targetNodeID + " does not exist yet. Use addNode(nodeID, data).")

        if startingIndex == -1: # Aka the end
            startingIndex = len(self.climateData[targetNodeID]) - 1
        elif startingIndex > len(self.climateData[targetNodeID]) - 1:
            raise ValueError("Starting index is too large.")
        elif startingIndex < 0:
            raise ValueError("Starting index is negative.")
        
        if endingIndex == -1: # Aka the end
            endingIndex = len(self.climateData[targetNodeID]) - 1
        elif endingIndex > len(self.climateData[targetNodeID]) - 1:
            raise ValueError("Ending index is too large.")
        elif endingIndex < startingIndex:
            raise ValueError("Ending index is less than starting index.")

        while startingIndex <= endingIndex:
            self.climateData[targetNodeID].pop(startingIndex)
            endingIndex = endingIndex - 1

        if not self.areNodesEqualLength():
            self.dataValueCount = "NA until nodes have equal datapoints."
        else:
            self.dataValueCount = len(self.climateData[self.nodeIDs[0]])





    # Replace data in an existing node with new data, using nodeID to determine which node and
    # startingIndex to determine where to start replacing at
    def replaceDataInNode(self, nodeID, data, startingIndex):
        # Check for valid node id
        targetNodeID = self.returnValidNodeID(nodeID)

        # Check if node id has yet to be added
        if self.indexOfNodeID(targetNodeID) == -1:
            raise LookupError("Node id " + targetNodeID + " does not exist yet. Use addNode(nodeID, data).")

        if startingIndex > len(self.climateData[targetNodeID]) - 1:
            raise ValueError("Starting index is too large.")
        elif startingIndex < 0:
            raise ValueError("Starting index is negative.")

        # Make sure the data is valid
        if isinstance(data, (list, tuple)):
            for dataPoint in data:
                try:
                    self.climateData[targetNodeID][startingIndex] = dataPoint
                except IndexError:
                    self.climateData[targetNodeID].append(dataPoint)
                startingIndex = startingIndex + 1
        elif isinstance(data, float):
            self.climateData[targetNodeID][startingIndex] = data
        else:
            raise TypeError("Data must be a list, tuple, or float.")

        if not self.areNodesEqualLength():
            self.dataValueCount = "NA until nodes have equal datapoints."
        else:
            self.dataValueCount = len(self.climateData[self.nodeIDs[0]])


    # Returns the an array of the dates based on number of dataValueCount, startDayOfYear, and originalDataYears
    def getDates(self):
        startDayOfYear = self.startDayOfYear
        dataValueCount = self.dataValueCount
        originalDataYears = self.originalDataYears

        months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
        startDayOfYearArray = startDayOfYear.split(" ")
        for month in range(len(months)):
            if startDayOfYearArray[0] == months[month]:
                startMonth = month
                break
        else:
            raise ValueError("Month name in StartDayOfYear must be in it's full name (ie January, not Jan or Jan.) "
                             "StartDayOfYear was " + startDayOfYearArray[0])
        startYear = originalDataYears.split("-")[0]  # Gets first year of year range (ie 1950 if it is 1950-2000)
        # This needs to be here to prevent it from incorrectly reading a date like 1955101 as 10/1/1955 instead of 1/01/1955
        if startMonth < 10:
            startMonth = "0" + str(startMonth)
        fullStartDate = str(startYear) + str(startMonth) + str(startDayOfYearArray[1])
        startDate = datetime.datetime.strptime(fullStartDate, '%Y%m%d')
        startDate = datetime.date(startDate.year, startDate.month, startDate.day)
        dates = []
        dates.append(startDate.strftime('%m/%d/%Y'))
        for i in range(dataValueCount-1):
            newDate = startDate + datetime.timedelta(i+1)
            dates.append(newDate.strftime('%m/%d/%Y'))

        return dates




# IMPLICITLY CALLED FUNCTIONS
# IMPLICITLY CALLED FUNCTIONS
# IMPLICITLY CALLED FUNCTIONS

    def __str__(self):
        output = "\nDateCreated: " + self.dateCreated
        output = output + "\nTool: " + self.tool
        output = output + "\nAuthor: " + self.author
        output = output + "\nIdReference: " + self.idReference
        output = output + "\nNodeCount: " + str(self.nodeCount)
        output = output + "\nDatavalueCount: " + str(self.dataValueCount)
        output = output + "\nUpdateResolution: " + self.updateResolution
        output = output + "\nOriginalDataYears: " + self.originalDataYears
        output = output + "\nStartDayOfYear: " + self.startDayOfYear
        output = output + "\nDataProvenance: " + self.dataProvenance
        return output





# PRIVATE FUNCTIONS
# PRIVATE FUNCTIONS
# PRIVATE FUNCTIONS

    # Takes an item (string of data, filename, or file) and returns an open file. This is not to be called by a user, so fileType will be passed in as either "json" or "bin". StringIO is used to convert a string of data into a file stream.
    def returnFile(self, item, fileType):
        # Check if it is a valid fileType.
        if fileType != "json" and fileType != "bin":
            raise ValueError("fileType must be either \"json\" or \"bin\"")
        # If it's an open file
        if isinstance(item, file):
            return item
        elif isinstance(item, (str, unicode)):
            extension = item.split(".")[-1]
            if extension != fileType:  # If item is string of data instead of filename
                # If it's a json string, make sure it's valid
                if fileType == "json":
                    try:
                        json.loads(item)
                        return StringIO(item)
                    except ValueError:
                        raise ValueError("Bad json data in string or bad filename. Json should be passed in as an "
                                         "open file, a string that contains json, or a filename that ends in \".json\".")
                else:  # Else bin as bytes
                    return StringIO(item)
            else:
                # If it's a json filename
                if fileType == "json":
                    fileToReturn = open(item, 'r')
                    try:  # Check if it's a valid json file
                        json.load(fileToReturn)
                        fileToReturn.close()
                        return open(item, 'r')
                    except ValueError:
                        raise ValueError("Bad json data in file.")
                else:  # Else bin filename
                    return open(item, 'rb')
        else:
            raise TypeError(fileType + " must be passed in as either an open file, a filename, or the data as a string.")
            




    # Check and fill metaData variables and return True if everything went ok, and return False if empty, otherwise it raises an error
    def checkMetaData(self, metaData):
        # If empty, return False. Sometimes False means an error, sometimes it is ok. We return it back so it can be decided which to do where it's called.
        if not metaData:
            return False
        elif isinstance(metaData, dict): # Check that all required metadata is here
            if 'DateCreated' in metaData:
                self.dateCreated = metaData['DateCreated']
            else:
                raise KeyError("DateCreated is not in supplied metaData")
            if 'Tool' in metaData:
                self.tool = metaData['Tool']
            else:
                raise KeyError("Tool is not in supplied metaData")
            if 'Author' in metaData:
                self.author = metaData['Author']
            else:
                raise KeyError("Author is not in supplied metaData")
            if 'IdReference' in metaData:
                self.idReference = metaData['IdReference']
            else:
                raise KeyError("IdReference not in supplied metaData")
            if 'NodeCount' in metaData:
                self.nodeCount = metaData['NodeCount']
            else:
                raise KeyError("NodeCount is not in supplied metaData")
            if 'DatavalueCount' in metaData:
                self.dataValueCount = metaData['DatavalueCount']
            else:
                raise KeyError("DatavalueCount is not in supplied metaData")
            if 'UpdateResolution' in metaData:
                self.updateResolution = metaData['UpdateResolution']
            else:
                raise KeyError("UpdateResolution is not in supplied metaData")
            if 'OriginalDataYears' in metaData:
                self.originalDataYears = metaData['OriginalDataYears']
            else:
                raise KeyError("OriginalDataYears is not in supplied metaData")
            if 'StartDayOfYear' in metaData:
                self.startDayOfYear = metaData['StartDayOfYear']
            else:
                raise KeyError("StartDayOfYear is not in supplied metaData")
            if 'DataProvenance' in metaData:
                self.dataProvenance = metaData['DataProvenance']
            else:
                raise KeyError("DataProvenance is not in supplied metaData")
            # If there is anything extra that is not required, keep track of it so we can put it back in the new file.
            for item in metaData:
                if item != 'DateCreated' and item != 'Tool' and item != 'Author' and item != 'IdReference' and item != 'NodeCount' and item != 'DatavalueCount' and item != 'UpdateResolution' and item != 'OriginalDataYears' and item != 'StartDayOfYear' and item != 'DataProvenance':
                    self.otherMetaData[item] = metaData[item]
        else:
            raise TypeError("Metadata must be a dictionary.")
        return True


    # Check if node id is already in the list. Returns -1 if not in the list, otherwise returns the index.
    def indexOfNodeID(self, nodeID):
        # Check for valid node id
        targetNodeID = self.returnValidNodeID(nodeID)
        for node in range(len(self.nodeIDs)):
            if targetNodeID == self.nodeIDs[node]:
                return node
        return -1

    

    # Check if node id is valid, and if so, return it in as a string
    def returnValidNodeID(self, nodeID):
        nodeIDErrorMessage = "Node id must be either an integer or string that represents an integer."
        # Check for valid node id
        if isinstance(nodeID, (str, unicode)):
            try:
                int(nodeID)
                return nodeID
            except ValueError:
                raise ValueError(nodeIDErrorMessage)
        elif isinstance(nodeID, int):
            return str(nodeID)
        else:
            raise TypeError(nodeIDErrorMessage)



    # Check if all nodes have the same number of datapoints
    def areNodesEqualLength(self):
        count = len(self.climateData[self.nodeIDs[0]])
        for node in range(self.nodeCount):
            if count != len(self.climateData[self.nodeIDs[node]]):
                return False
        return True



    # Takes a string of hex and converts to an int
    def hexStringToDecimalString(self, hexString):
        try:
            return str(int(hexString, 16))
        except TypeError:
            raise TypeError("hexString must be a string of hexadecimal.")
        except ValueError:
            raise ValueError("hexString contains invalid hexadecimal.")



    # Takes an int and converts to a string of hex without the "0x" at the beginning
    def decimalStringToHexString(self, decimalString, length=8):
        decimalStringError = "decimalString must be an integer represented as a string."
        if not isinstance(decimalString, (str, unicode)):
            raise TypeError(decimalStringError)
        if not isinstance(length, int):
            raise TypeError("length must be an integer")
        try:
            hexString = hex(int(decimalString)).split('x')[1]
            while len(hexString) < length:
                hexString = "0" + hexString
        except:
            raise ValueError(decimalStringError)
        return hexString






# DEBUG FUNCTIONS
# DEBUG FUNCTIONS
# DEBUG FUNCTIONS

    # Takes a node id and returns an array of floats
    def getNodeData(self, nodeID):
        return self.climateData[nodeID]



    # Prints all the the climateData
    def printClimateData(self):
        for node in range(self.nodeCount):
            print "Node ID: " + self.nodeIDs[node]
            print self.climateData[self.nodeIDs[node]]



    # Prints all node IDs
    def printNodeIDs(self):
        for node in self.nodeIDs:
            print node
