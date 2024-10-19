#-------------------------------------------------------------------------------
# Name:        Generate Unique Transects
# Purpose:      Connecting sample points to create unique transect polylines for
#               each survey
#
# Author:      alz5215
#
# Created:     01/08/2024
# Copyright:   (c) alz5215 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import csv
import pandas
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\alz5215\OneDrive - The Pennsylvania State University\Documents\Research\GIS\Year2ForestData\Transects"

# function to add keys to dictionary, appending value rather than replacing if key already exists
def addToDict(Dict,key,value):
    if key in Dict:
        Dict[key].append(value)
    else:
        Dict[key] = [value]

# bring in csv for start/end coordinates
startend = r"C:\Users\alz5215\OneDrive - The Pennsylvania State University\Documents\Research\GIS\Year2ForestData\Transects\Final_StudyArea_EndPoints.csv"

with open(startend, "r") as startEnd:

    # open the csv reader
    csvReader = csv.reader(startEnd)

    # use next() to get first line - the header
    header = next(csvReader)

    # get the indexes for each needed field
    saIndex = header.index("StudyAreaNumber")
    tranIndex = header.index("TransectNumber")
    sideIndex = header.index("Side")
    latIndex = header.index("Latitude")
    lonIndex = header.index("Longitude")

    # empty dictionary to hold the coordinates for each point
    startEndDict = {}

    # for each row in the csv file
    for row in csvReader:

        # get the required values
        sa = row[saIndex]
        tran = row[tranIndex]
        side = row[sideIndex]
        lat = float(row[latIndex])
        lon = float(row[lonIndex])

        # create single fields for the point coords and the transect ID
        coords = tuple([lon,lat])
        tranID = "-".join([sa,tran,side])

        # add to the dictionary
        addToDict(startEndDict,tranID,coords)

# testing
print(startEndDict["46-12-B"])

# bring in csv for samples
samplesFile = r"C:\Users\alz5215\OneDrive - The Pennsylvania State University\Documents\Research\Chapter 2\SnowshoeHare-Density\data\DetectionLocations_DNA_Censored_m.csv"

#convert csv to data frame
samplesDF = pandas.read_csv(samplesFile)

# sort data frame by latitude, descending, so that points are in order between start and end points
samplesDF = samplesDF.sort_values(by = ["Location_Latitude"], ascending = False)

# empty dictionary to hold the coordinates for each transect
sampleDict = {}

# go through each sample collected during surveys
for index, row in samplesDF.iterrows():

    # get the required columns
    sa = str(row["Study_Area"])
    tran = str(row["Transect_Number"])
    vis = str(row["Visit_Number"])
    lat = float(row["Location_Latitude"])
    lon = float(row["Location_Longitude"])
    censor = int(row["Censor"])

    # do not consider censored (censor = 1) points
    if censor == 0:

        # create single fields for the point coords and the transect ID
        coords = tuple([lon,lat])
        surveyID = "-".join([sa,tran,vis])

        # add to the list of coordinates for that transect
        addToDict(sampleDict,surveyID,coords)

# testing
print(sampleDict["46-2-3"])

# Create a new, empty feature class to hold transect polylines
folderName = r"C:\Users\alz5215\OneDrive - The Pennsylvania State University\Documents\Research\GIS\Year2ForestData\Transects"
tranPolyline = "unique_transects_PAmeters.shp"
sr = arcpy.SpatialReference(6562) # NAD 1983 (2011) PA state plane N meters
arcpy.management.CreateFeatureclass(folderName,tranPolyline,"POLYLINE","","","",sr)
arcpy.management.AddField(tranPolyline,"SurveyID","TEXT") # field for unique survey ID

# loop through each transect, then each occasion
studyareas = ["14","33","39","44","45","46","49","50","51","52"]
transects = ["1","2","3","4","5","6","7","8","9","10","11","12"]
visits = ["1","2","3","4"]
surveyDict = {} # empty dictionary to hold all points for each survey

for studyarea in studyareas:

    for tran in transects:

        # grab the start point and end point
        startPoint = "-".join([studyarea,tran,"A"])
        endPoint = "-".join([studyarea,tran,"B"])

        # grab samples
        for vis in visits:
            # empty list to hold all point coordinates within the transect
            coordsList = []

            # add start point
            coordsList.append(startEndDict[startPoint])

            surveyID = "-".join([studyarea,tran,vis])

            # if there are samples from that survey, add the points to the coords list
            if surveyID in sampleDict:
                sampCoords = sampleDict[surveyID]
                coordsList.append(sampCoords)

            # add end point
            coordsList.append(startEndDict[endPoint])

            # flatten the coords list
            coordsList = [val for sublist in coordsList for val in sublist]

            # add to survey dictionary
            addToDict(surveyDict,surveyID,coordsList)

print(surveyDict["46-2-3"])

# connect the points into polyline and label with survey ID
for surv in surveyDict:
    with arcpy.da.InsertCursor(tranPolyline, ("SurveyID","SHAPE@")) as cursor:
        cursor.insertRow((surv,surveyDict[surv][0]))

