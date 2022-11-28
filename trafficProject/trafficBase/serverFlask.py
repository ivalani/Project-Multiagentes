# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2021

from flask import Flask, request, jsonify
from agent import *
from model import *

# Size of the board:
number_agents = 10
width = 28
height = 28
random_model = None
current_step = 0

app = Flask("Traffic example")

# @app.route('/', methods=['POST', 'GET'])


@app.route("/init", methods=["POST", "GET"])
def initModel():
    global current_step, random_model, number_agents, width, height

    if request.method == "POST":
        number_agents = int(request.form.get("NAgents"))
        width = int(request.form.get("width"))
        height = int(request.form.get("height"))
        current_step = 0

        print(request.form)
        print(number_agents, width, height)
        random_model = RandomModel(number_agents, width, height)

        return jsonify({"message": "Parameters recieved, model initiated."})


@app.route("/getAgents", methods=["GET"])
def getAgents():
    global random_model

    if request.method == "GET":
        agent_positions = [
            {"id": str(a.unique_id), "x": x, "y": 1, "z": z}
            for (a, x, z) in random_model.grid.coord_iter()
            if isinstance(a, Car)
        ]

        return jsonify({"positions": agent_positions})


@app.route("/getObstacles", methods=["GET"])
def getObstacles():
    global random_model

    if request.method == "GET":
        obstacle_positions = [
            {"id": str(a.unique_id), "x": x, "y": 1, "z": z}
            for (a, x, z) in random_model.grid.coord_iter()
            if isinstance(a, Obstacle)
        ]

        return jsonify({"positions": obstacle_positions})


@app.route("/update", methods=["GET"])
def updateModel():
    global current_step, random_model
    if request.method == "GET":
        random_model.step()
        current_step += 1
        return jsonify(
            {
                "message": f"Model updated to step {current_step}.",
                "currentStep": current_step,
            }
        )


if __name__ == "__main__":
    app.run(host="localhost", port=8585, debug=True)
