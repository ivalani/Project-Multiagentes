# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2021

from flask import Flask, request, jsonify
from agent import *
from model import *
from termcolor import cprint

# Size of the board:
number_agents = 10
width = 28
height = 28
random_model = None
current_step = 0

app = Flask("Traffic example")


@app.route("/init", methods=["POST", "GET"])
def initModel():
    global current_step, random_model, number_agents, width, height

    if request.method == "POST":
        try:
            number_agents = int(request.form.get("NAgents"))
            width = int(request.form.get("width"))
            height = int(request.form.get("height"))
            current_step = 0

            random_model = RandomModel(number_agents)
            cprint("Model initialized successfully!", "green")
            return jsonify({"message": "Parameters recieved, model initiated."})
        except:
            cprint("Failed to initialize model!", "red")
            return jsonify({"message": "Failed to initialize model!"})


@app.route("/getAgents", methods=["GET"])
def getAgents():
    global random_model

    if request.method == "GET":
        try:
            agent_positions = [
                {"id": str(a.unique_id), "x": x, "y": 1, "z": z}
                for (a, x, z) in random_model.grid.coord_iter()
                if isinstance(a, Car)
            ]
            cprint("Agents positions received!", "green")
            return jsonify({"positions": agent_positions})
        except:
            cprint("Failed to receive agent's position!", "red")
            return jsonify({"message": "Failed to get agents positions!"})


@app.route("/getObstacles", methods=["GET"])
def getObstacles():
    global random_model

    if request.method == "GET":
        try:
            obstacle_positions = [
                {"id": str(a.unique_id), "x": x, "y": 1, "z": z}
                for (a, x, z) in random_model.grid.coord_iter()
                if isinstance(a, Obstacle)
            ]
            cprint("Obstacle positions received!", "green")
            return jsonify({"positions": obstacle_positions})
        except:
            cprint("Failed to receive obstacles' position!", "red")
            return jsonify({"message": "Failed to get obstacle positions!"})


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
