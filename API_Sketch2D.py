# Author- Chaitanya Katti
# Description- This script imports 2D sketches from DXF files and extrudes them to create a 3D model.

import adsk.core, adsk.fusion, adsk.cam, traceback, os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from dxf_parser import parse_view

sketchDir = 'Chamfer'

def clearAll(rootComp: adsk.fusion.Component):
    for sketch in rootComp.sketches:
        sketch.deleteMe()
    for body in rootComp.bRepBodies:
        body.deleteMe()
    for plane in rootComp.constructionPlanes:
        plane.deleteMe()
    for axis in rootComp.constructionAxes:
        axis.deleteMe()
    for point in rootComp.constructionPoints:
        point.deleteMe()

def createOffsetPlane(rootComp: adsk.fusion.Component,
                      offset: float,
                      direction: str) -> adsk.fusion.ConstructionPlane:
    # Create offset construction plane
    planes = rootComp.constructionPlanes
    planeInput: adsk.fusion.ConstructionPlaneInput = planes.createInput()
    offsetValue = adsk.core.ValueInput.createByString(str(offset))
    if direction == 'x':
        planeInput.setByOffset(rootComp.yZConstructionPlane, offsetValue)
    elif direction == 'y':
        planeInput.setByOffset(rootComp.xZConstructionPlane, offsetValue)
    elif direction == 'z':
        planeInput.setByOffset(rootComp.xYConstructionPlane, offsetValue)

    constructionPlane =  planes.add(planeInput)
    constructionPlane.isLightBulbOn = False
    return constructionPlane

def loadAndCreateSketches(rootComp: adsk.fusion.Component,
                 importManager: adsk.core.ImportManager,
                 sketchDir: str):
    # Get the sketches collection
    sketches = rootComp.sketches
    planes = rootComp.constructionPlanes

    # Create back plane (offset in Y direction)
    yOffsetPlane = createOffsetPlane(rootComp, 1, 'y')
    # Create top plane (offset in Z direction)
    zOffsetPlane = createOffsetPlane(rootComp, 1, 'z')
    # Create right plane (offset in X direction)
    xOffsetPlane = createOffsetPlane(rootComp, 1, 'x')

    # Import the DXF files and create sketches
    dxfFiles = ['Front.dxf', 'Back.dxf', 'Left.dxf', 'Right.dxf', 'Bottom.dxf', 'Top.dxf']
    planes = [rootComp.xZConstructionPlane, yOffsetPlane, rootComp.yZConstructionPlane, xOffsetPlane, rootComp.xYConstructionPlane, zOffsetPlane]
    names = ['Front', 'Back', 'Left', 'Right', 'Bottom', 'Top']

    # Import the DXF files and create sketches
    for dxfFile, plane, name in zip(dxfFiles, planes, names):
        dxfFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sketches', sketchDir, dxfFile)
        dxfOptions = importManager.createDXF2DImportOptions(dxfFilePath, plane)
        importManager.importToTarget(dxfOptions, rootComp)
        sketch = sketches[-1]
        sketch.name = name

def addBoundingSquareToSketch(sketch: adsk.fusion.Sketch):
    # Get the sketch lines collection
    sketchLines = sketch.sketchCurves.sketchLines
    # Create the square lines
    startPoint = adsk.core.Point3D.create(0, 0, 0)
    if sketch.name in ['Front', 'Back']:
        endPoint = adsk.core.Point3D.create(100, -100, 0)
    else:
        endPoint = adsk.core.Point3D.create(100, 100, 0)
    sketchLines.addTwoPointRectangle(startPoint, endPoint)

def positiveExtrudeSketch(rootComp: adsk.fusion.Component, sketch: adsk.fusion.Sketch):
    # Get the extrudes collection
    extrudes = rootComp.features.extrudeFeatures

    # Extrude all the profiles in the sketch
    for profile in sketch.profiles:
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('1 m'))
        if sketch.name in ['Top', 'Right', 'Back']:
            extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.NegativeExtentDirection)
        else:
            extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extrude = extrudes.add(extrudeInput)
        body = extrude.bodies.item(0)
        body.name = sketch.name + " Positive Extrusion"

def negativeExtrudeSketch(rootComp: adsk.fusion.Component,
                          sketch: adsk.fusion.Sketch):
    # Select the region outside the main sketch area but inside the bounding square
    # Use cut operation to remove the selected region
    selectedProfile = None
    # # Pick the correct profile
    for profile in sketch.profiles:
        # Check if the profile has a closed loop rectangle
        bb = profile.boundingBox
        if bb.minPoint.x == 0 and bb.minPoint.y == 0 and bb.maxPoint.x == 100 and bb.maxPoint.y == 100:
            selectedProfile = profile
            break
        elif bb.minPoint.x == 0 and bb.minPoint.y == -100 and bb.maxPoint.x == 100 and bb.maxPoint.y == 0: # Front and Back
            selectedProfile = profile
            break
    if selectedProfile is not None:
        # Get the extrudes collection
        extrudes = rootComp.features.extrudeFeatures
        # Extrude the sketch
        extrudeInput = extrudes.createInput(selectedProfile, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('1 m'))
        if sketch.name in ['Top', 'Right', 'Back']:
            extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.NegativeExtentDirection)
        else:
            extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        try:
            extrude = extrudes.add(extrudeInput)
            body = extrude.bodies.item(0)
            body.name = sketch.name + " Negative Extrusion"
        except:
            pass
    else:
        ui = adsk.core.Application.get().userInterface
        ui.messageBox('No profile found for sketch: {}'.format(sketch.name))

# def negativeExtrudeSketchProfile(rootComp: adsk.fusion.Component,
#                                     sketch: adsk.fusion.Sketch,
#                                     views: dict):
#     ui = adsk.core.Application.get().userInterface
#     for profile in sketch.profiles:
#         # Check if the profile has a closed loop rectangle
#         bb = profile.boundingBox
#         if bb.minPoint.x == 0 and bb.minPoint.y == 0 and bb.maxPoint.x == 100 and bb.maxPoint.y == 100:
#             continue
#         elif bb.minPoint.x == 0 and bb.minPoint.y == -100 and bb.maxPoint.x == 100 and bb.maxPoint.y == 0: # Front and Back
#             continue
        
#         # Calculate the centroid of the profile using the bounding box
#         centroid = adsk.core.Point3D.create(10*abs(bb.minPoint.x + bb.maxPoint.x) / 2, 10*abs(bb.minPoint.y + bb.maxPoint.y) / 2, 0)
#         ui.messageBox(f'Sketch: {sketch.name}, Centroid: {centroid.x}, {centroid.y}, {centroid.z}')
#         # Calculate the depth of the profile inside the sketch
#         if sketch.name == 'Front':
#             depth = None
#             # Look for all vertical lines in left right views
#             points = views['Left']['Points'] # is a list of tuples (x, y)
#             lines = views['Left']['Lines'] # is a list of tuples index pairs
#             possible_depths = []
#             # Starting from Y=0, find the line that intersects the z-value == (centroid.y)
#             for line in lines:
#                 # Check if line is vertical
#                 if points[line[0]][0] == points[line[1]][0]:
#                     # ui.messageBox('Line: {}, {} is vertical'.format(points[line[0]], points[line[1]]))
#                     # Check if the line intersects the centroid, same y-value, 
#                     if points[line[0]][1] <= centroid.y <= points[line[1]][1] or points[line[1]][1] <= centroid.y <= points[line[0]][1]:
#                         # ui.messageBox('Line: {}, {} intersects centroid'.format(points[line[0]], points[line[1]]))
#                         possible_depths.append(abs(points[line[0]][0]))
#             if len(possible_depths) <= 2:
#                 continue
#             else:
#                 # Select the second smallest depth
#                 depth = sorted(possible_depths)[1]
            
#             points = views['Right']['Points'] # is a list of tuples (x, y)
#             lines = views['Right']['Lines'] # is a list of tuples index pairs


def run(context):
    ui = None
    try:
        app: adsk.core.Application = adsk.core.Application.get()
        ui: adsk.core.UserInterface = app.userInterface
        design: adsk.core.Product = app.activeProduct
        importManager: adsk.core.ImportManager = app.importManager
        rootComp: adsk.fusion.Component = design.rootComponent

        # Clear all existing sketches, bodies, construction planes, construction axes, and construction points
        for _ in range(10):
            clearAll(rootComp)

        # # Get the xy plane
        sketches = rootComp.sketches

        # Create a new sketch on the xy plane
        loadAndCreateSketches(rootComp, importManager, sketchDir)

        # Extrude all the sketches
        for sketch in sketches:
            positiveExtrudeSketch(rootComp, sketch)
            # ui.inputBox('Press Enter to continue')
        # Add a bounding square to the sketch
        for sketch in sketches:
            addBoundingSquareToSketch(sketch)
        # Negative extrude each sketch area outside the main sketch area but inside the bounding square
        for sketch in sketches:
            negativeExtrudeSketch(rootComp, sketch)

        # front, back, left, right, bottom, top = parse_view(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sketches', sketchDir))
        # views = {'Front': front, 'Back': back, 'Left': left, 'Right': right, 'Bottom': bottom, 'Top': top}
        
        # Negative exturde individual profiles by estimating the depth of each profile inside a sketch using other views
        # for sketch in sketches:
            # negativeExtrudeSketchProfile(rootComp, sketch, views)

        # Rename the bodies
        for body in rootComp.bRepBodies:
            if 'Positive Extrusion' in body.name:
                body.name = sketchDir + ' Model'
            elif 'Negative Extrusion' in body.name:
                body.name = sketchDir + ' Model'

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
