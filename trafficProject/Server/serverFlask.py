# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2021

from flask import Flask, request, jsonify
from agent import *
from model import *
from termcolor import cprint

# Size of the board:
number_agents = 10
random_model = None
current_step = 0

app = Flask("Traffic example")


@app.route("/init", methods=["POST", "GET"])
def initModel():
    global current_step, random_model, number_agent

    if request.method == "POST":
        try:
            current_step = 0

            random_model = RandomModel(number_agents)
            cprint("Model initialized successfully!", "green")
            return jsonify({"message": "Parameters recieved, model initiated."})
        except:
            cprint("Failed to initialize model!", "red")
            return jsonify({"message": "Failed to initialize model!"})


@app.route("/getCars", methods=["GET"])
def getCar():
    global random_model

    carPositions = []
    if request.method == "GET":
        try:
            for (contents, x, z) in random_model.grid.coord_iter():
                for i in contents:
                    if isinstance(i, Car):
                        carPositions.append(
                            {
                                "id": str(i.unique_id),
                                "x": x,
                                "y": 1,
                                "z": z,
                            }
                        )

            cprint("Cars positions received!", "green")
            return jsonify({"positions": carPositions})
        except:
            cprint("Failed to receive cars position!", "red")
            return jsonify({"message": "Failed to get cars positions!"})


@app.route("/getBuses", methods=["GET"])
def getBus():
    global random_model

    busPosition = []
    if request.method == "GET":
        try:
            for (contents, x, z) in random_model.grid.coord_iter():
                for i in contents:
                    if isinstance(i, Bus):
                        busPosition.append(
                            {"id": str(i.unique_id), "x": x, "y": 1, "z": z}
                        )

            cprint("Buses positions received!", "green")
            return jsonify({"positions": busPosition})
        except:
            cprint("Failed to receive buses position!", "red")
            return jsonify({"message": "Failed to get buses positions!"})


@app.route("/getPedestrians", methods=["GET"])
def getPedestrians():
    global random_model

    pedestrianPosition = []
    if request.method == "GET":
        try:

            for (contents, x, z) in random_model.grid.coord_iter():
                for i in contents:
                    if isinstance(i, Pedestrian):
                        pedestrianPosition.append(
                            {
                                "id": str(i.unique_id),
                                "x": x,
                                "y": 1,
                                "z": z,
                            }
                        )
            cprint("Pedestrians positions received!", "green")
            return jsonify({"positions": pedestrianPosition})
        except:
            cprint("Failed to get pedestrians positions", "red")
            return jsonify({"message": "Failed get pedestrians positions"})


@app.route("/trafficLightState", methods=["GET"])
def getTrafficLightState():
    global random_model

    trafficLights = []

    if request.method == "GET":
        try:
            for (contents, x, z) in random_model.grid.coord_iter():
                for i in contents:
                    if isinstance(i, Traffic_Light):
                        print(i)
                        trafficLights.append(
                            {
                                "id": str(i.unique_id),
                                "x": x,
                                "y": 1,
                                "z": z,
                                "state": i.state,
                            }
                        )
            cprint("Traffic lights state received!", "green")
            return jsonify({"positions": trafficLights})
        except:
            cprint("Failed to get traffic lights state!", "red")
            return jsonify({"message": "Failed to get traffic lights state"})


@app.route("/update", methods=["GET"])
def updateModel():
    global current_step, random_model
    if request.method == "GET":
        try:
            random_model.step()
            current_step += 1
            cprint("Model updated!", "green")
            return jsonify(
                {
                    "message": f"Model updated to step {current_step}.",
                    "currentStep": current_step,
                }
            )
        except:
            cprint("Failed to update model!", "red")
            return jsonify({"message": "Failed to update model!"})


if __name__ == "__main__":
    app.run(host="localhost", port=8585, debug=True)
