from os import listdir, path

from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from model import FloodEvacuation
from agent import EmergencyExit, Wall, Furniture, Water, Human, Sight, Door, DeadHuman, Highway, Path, AgricultureField,Tree, Bridge,Tile, Forecaster, FirstResponder


# Creates a visual portrayal of our model in the browser interface
def fire_evacuation_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    (x, y) = agent.get_position()
    portrayal["x"] = x
    portrayal["y"] = y

    if type(agent) is Human:
        portrayal["scale"] = 1
        portrayal["Layer"] = 5

        if agent.get_mobility() == Human.Mobility.INCAPACITATED:
            # Incapacitated
            portrayal["Shape"] = "resources/incapacitated_human.png"
            portrayal["Layer"] = 6
        elif agent.get_mobility() == Human.Mobility.PANIC:
            # Panicked
            portrayal["Shape"] = "resources/panicked_human.png"
        elif agent.is_carrying():
            # Carrying someone
            portrayal["Shape"] = "resources/carrying_human.png"
        else:
            # Normal
            portrayal["Shape"] = "resources/human.png"
    elif type(agent) is Water:
        portrayal["Shape"] = "resources/water.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 3
    elif type(agent) is EmergencyExit:
        portrayal["Shape"] = "resources/fire_exit.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is Door:
        portrayal["Shape"] = "resources/door.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is Wall:
        portrayal["Shape"] = "resources/wall.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is Furniture:
        portrayal["Shape"] = "resources/building.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is Tree:
        portrayal["Shape"] = "resources/tree.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is Bridge:
        portrayal["Shape"] = "resources/bridge.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is Highway:
        portrayal["Shape"] = "resources/highway.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is Path:
        portrayal["Shape"] = "resources/PATH.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is AgricultureField:
        portrayal["Shape"] = "resources/field.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif type(agent) is DeadHuman:
        portrayal["Shape"] = "resources/dead.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 4
    elif type(agent) is Sight:
        portrayal["Shape"] = "resources/eye.png"
        portrayal["scale"] = 0.8
        portrayal["Layer"] = 7
    elif type(agent) is Tile:
        portrayal["Layer"] = 1
        portrayal["scale"] = 1

    elif type(agent) is Forecaster:
        portrayal["Layer"] = 1
        portrayal["scale"] = 1
        
    elif type(agent) is FirstResponder:
        portrayal["Shape"] = "resources/hospital.png"
        portrayal["Layer"] = 1
        portrayal["scale"] = 1
        
    
    return portrayal


# Was hoping floorplan could dictate the size of the grid, but seems the grid needs to be specified first, so the size is fixed to 50x50
canvas_element = CanvasGrid(fire_evacuation_portrayal, 50, 50, 800, 800)

# Define the charts on our web interface visualisation
status_chart = ChartModule(
    [
        {"Label": "Alive", "Color": "blue"},
        {"Label": "Dead", "Color": "red"},
        {"Label": "Escaped", "Color": "green"},
    ]
)

mobility_chart = ChartModule(
    [
        {"Label": "Normal", "Color": "green"},
        {"Label": "Panic", "Color": "red"},
        {"Label": "Incapacitated", "Color": "blue"},
    ]
)

collaboration_chart = ChartModule(
    [
        {"Label": "Verbal Collaboration", "Color": "orange"},
        {"Label": "Physical Collaboration", "Color": "red"},
        {"Label": "Morale Collaboration", "Color": "pink"},
    ]
)

# Get list of available floorplans
floor_plans = [
    f
    for f in listdir("floorplans")
    if path.isfile(path.join("floorplans", f))
]

# Specify the parameters changeable by the user, in the web interface
model_params = {
    "floor_plan_file": UserSettableParameter(
        "choice", "Floorplan", value=floor_plans[4], choices=floor_plans
    ),
    "human_count": UserSettableParameter("number", "Number Of Human Agents", value=25),
    "collaboration_percentage": UserSettableParameter(
        "slider", "Percentage Collaborating", value=60, min_value=0, max_value=100, step=10
    ),
    "num_of_responders": UserSettableParameter("number", "Number of First Responders", value  = 4),
    "fire_probability": UserSettableParameter(
        "slider", "Probability of Flood", value=0.8, min_value=0, max_value=1, step=0.01
    ),
    "random_spawn": UserSettableParameter(
        "checkbox", "Spawn Agents at Random Locations", value=False
    ),
    "visualise_vision": UserSettableParameter("checkbox", "Show Agent Vision", value=False),
    "save_plots": UserSettableParameter("checkbox", "Save plots to file", value=True),
}

# Start the visual server with the model
server = ModularServer(
    FloodEvacuation,
    [canvas_element, status_chart, mobility_chart, collaboration_chart],
    "Flood Evacuation",
    model_params,
)
