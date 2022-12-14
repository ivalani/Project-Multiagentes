"""
Flask server for robot visualization

"""

from flask import Flask, request, jsonify
from Robot import *
from model_temp import RandomModel

# Initialize values

numberAgents = 0
width = 0
height = 0
randomModel = None
currentStep = 0

app = Flask("Order warehouse")


@app.route("/init", methods=["POST", "GET"])
def initModel():
    global numberAgents, width, height, randomModel, currentStep
    if request.method == "POST":
        try:
            numberAgents = int(request.form.get("NumberAgents"))
            width = int(request.form.get("CanvasWidth"))
            height = int(request.form.get("CanvasHeight"))
            boxesDensity = float(request.form.get("BoxesDensity"))
            currentStep = 0

            print(numberAgents, boxesDensity, width, height)
            randomModel = RandomModel(numberAgents, boxesDensity, width, height)
            return jsonify({"message": "Parameters received. Model initiated"})
        except:
            return jsonify({"message": "Error al iniciar el modelo"})


@app.route("/getRobots", methods=["GET"])
def getRobots():
    global randomModel

    robotPositions = []
    if request.method == "GET":
        for (contents, x, z) in randomModel.grid.coord_iter():
            for i in contents:
                if isinstance(i, RobotAgent):
                    robotPositions.append(
                        {
                            "id": str(i.unique_id),
                            "x": x,
                            "y": 1,
                            "z": z,
                            "has_box": i.with_box,
                        }
                    )
        return jsonify({"data": robotPositions})


@app.route("/getWall", methods=["GET"])
def getWall():
    global randomModel
    wallPositions = []

    if request.method == "GET":
        for (contents, x, z) in randomModel.grid.coord_iter():
            for i in contents:
                if isinstance(i, ObstacleAgent):
                    wallPositions.append(
                        {"id": str(i.unique_id), "x": x, "y": 1, "z": z}
                    )

        return jsonify({"positions": wallPositions})


@app.route("/getBoxes", methods=["GET"])
def getBoxes():
    global randomModel
    boxPosition = []
    if request.method == "GET":

        for (contents, x, z) in randomModel.grid.coord_iter():
            for i in contents:
                if isinstance(i, Box):
                    boxPosition.append(
                        {"id": str(i.unique_id), 
                        "x": x, 
                        "y": 1, 
                        "z": z,
                        "picked": i.pickedUp,
                        })
        return jsonify({"data": boxPosition})


@app.route("/getDropZone", methods=["GET"])
def getDropZone():
    global randomModel
    dropZonePosition = []

    if request.method == "GET":

        for (contents, x, z) in randomModel.grid.coord_iter():
            for i in contents:
                if isinstance(i, dropZone):
                    dropZonePosition.append(
                        {
                            "id": str(i.unique_id),
                            "x": x,
                            "y": 0.5,
                            "z": z,
                            "numberBoxes": i.stacked_boxes,
                        }
                    )

        return jsonify({"data": dropZonePosition})


# @app.route("")
@app.route("/update", methods=["GET"])
def updateModel():

    global currentStep, randomModel

    if request.method == "GET":
        try:
            randomModel.step()
            currentStep += 1

            print("Updated")
            return jsonify(
                {
                    "message": f"Model updated to step {currentStep}.",
                    "currentStep": currentStep,
                }
            )
        except:
            print("Error al actualizar")


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)
