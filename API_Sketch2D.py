#Author- Chaitanya Katti
#Description- This script imports 2D sketches from DXF files and extrudes them to create a 3D model.

import adsk.core, adsk.fusion, adsk.cam, traceback, os
from time import sleep

sketchDir = 'HollowFrame'

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
    planeInput = planes.createInput()
    offsetValue = adsk.core.ValueInput.createByString(str(offset))
    if direction == 'x':
        planeInput.setByOffset(rootComp.yZConstructionPlane, offsetValue)
    elif direction == 'y':
        planeInput.setByOffset(rootComp.xZConstructionPlane, offsetValue)
    elif direction == 'z':
        planeInput.setByOffset(rootComp.xYConstructionPlane, offsetValue)
    return planes.add(planeInput)
        
def createSketch(rootComp: adsk.fusion.Component, 
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
    dxfFiles = ['Front.dxf', 'Back.dxf', 'Bottom.dxf', 'Top.dxf', 'Left.dxf', 'Right.dxf']
    planes = [rootComp.xZConstructionPlane, yOffsetPlane, rootComp.xYConstructionPlane, zOffsetPlane, rootComp.yZConstructionPlane, xOffsetPlane]
    names = ['Front', 'Back', 'Bottom', 'Top', 'Left', 'Right']

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
    # Extrude the sketch
    extrudeInput = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation)
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

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        importManager = app.importManager
        rootComp: adsk.fusion.Component = design.rootComponent
        # Set unit in m
        adsk.fusion.Design.cast(app.activeProduct).fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MeterDistanceUnits

        # Clear all existing sketches, bodies, construction planes, construction axes, and construction points
        for _ in range(10):
            clearAll(rootComp)

        # Get the xy plane
        sketches = rootComp.sketches

        # Create a new sketch on the xy plane
        createSketch(rootComp, importManager, sketchDir)
        
        # Extrude all the sketches
        for sketch in sketches:
            positiveExtrudeSketch(rootComp, sketch)
            ui.inputBox('Press Enter to continue')
        # Add a bounding square to the sketch
        for sketch in sketches:
            addBoundingSquareToSketch(sketch)

        # Negative extrude each sketch area outside the main sketch area but inside the bounding square
        for sketch in sketches:
            negativeExtrudeSketch(rootComp, sketch)
        
        # Rename the bodies
        for body in rootComp.bRepBodies:
            if 'Positive Extrusion' in body.name:
                body.name = sketchDir + ' Model'
            elif 'Negative Extrusion' in body.name:
                body.name = sketchDir + ' Model'

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
