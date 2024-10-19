# transect-polylines
Using point locations from field surveys to build polyline shapefiles that track the route walked during each survey.

Surveys done Jan-April 2024. 10 study areas, each 4 sq km, each either 12 transects 2 km long. Each transect surveyed 3-4 times. Start and end points were provided but surveyors deviated from linear transect, which will cause problems with later analysis. Goal is to create a line for each survey that connects the samples collected to show the line the surveyor walked.

DetectionLocations_DNA_Censored_m: 
This csv contains the coordinates of snowshoe hare fecal pellets collected during each survey. DNA identification to species is included. Some samples are marked as "censored" because they were not collected during a standard survey, and will not be considered when connecting points into survey tracks.

Final_StudyArea_EndPoints: 
This csv contains the start and end coordinates for each transect that the surveyors were supposed to walk.
