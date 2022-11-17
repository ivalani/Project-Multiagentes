"""
Flask server for robot visualization

"""

from flask import Flask, request, jsonify
from Robot import *

# Initialize values

numberAgents = 0
width = 0
height = 0
randomModel = None
currentStep = 0

app = Flask("Order warehouse")

@app.route('/init', methods = ['POST', 'GET'])
def initModel():
    global numberAgents, width, height, randomModel, currentStep
    if request.method == 'POST':
        numberAgents = int(request.form.get('NumberAgents'))
        width = int(request.form.get('CanvasWidth'))
        height = int(request.form.get('CanvasHeight'))
        currentStep = 0

        print(request.form)
        print(numberAgents, width, height)
        randomModel = RandomModel(numberAgents, width, height)

        return jsonify({"message": "Parameters received. Model initiated"})
@app.route('/getRobots', methods = 'GET')
def getRobots():
    global randomModel

    if request.method == 'GET':
        robotPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, RobotAgent)]

        return jsonify({"positions": robotPositions})

@app.route('/getWall', methods = 'GET')
def getWall():
    global randomModel

    if request.method == 'GET':
        wallPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, wallAgent)]

        return jsonify({"postions": wallPositions})

@app.route('/getBoxes', methods = 'GET')
def getBoxes():
    global randomModel

    if request.method == 'GET':
        boxPosition = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, Box)]

        return jsonify({"positions": boxPosition})

@app.route('/update', methods = ['GET'])
def updateModel():

    global currentStep, randomModel

    if request.method == 'GET':
        randomModel.step()
        currentStep += 1

        return jsonify({'message': f'Model updated to step {currentStep}.', 'currentStep':currentStep})


if __name__ == '__main__':
    app.run(host = 'localhost', port = 8000, debug = True)