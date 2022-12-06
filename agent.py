from typing import Union
from typing_extensions import Self
from mesa.space import Coordinate
import networkx as nx
import numpy as np
from enum import IntEnum
from mesa import Agent
from copy import deepcopy
from utils import get_random_id
import random


def get_line(start, end):
    """
    Implementation of Bresenham's Line Algorithm
    Returns a list of tuple coordinates from starting tuple to end tuple (and including them)
    """
    # Break down start and end tuples
    x1, y1 = start
    x2, y2 = end

    # Calculate differences
    diff_x = x2 - x1
    diff_y = y2 - y1

    # Check if the line is steep
    line_is_steep = abs(diff_y) > abs(diff_x)

    # If the line is steep, rotate it
    if line_is_steep:
        # Swap x and y values for each pair
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # If the start point is further along the x-axis than the end point, swap start and end
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Calculate the differences again
    diff_x = x2 - x1
    diff_y = y2 - y1

    # Calculate the error margin
    error_margin = int(diff_x / 2.0)
    step_y = 1 if y1 < y2 else -1

    # Iterate over the bounding box, generating coordinates between the start and end coordinates
    y = y1
    path = []

    for x in range(x1, x2 + 1):
        # Get a coordinate according to if x and y values were swapped
        coord = (y, x) if line_is_steep else (x, y)
        path.append(coord)  # Add it to our path
        # Deduct the absolute difference of y values from our error_margin
        error_margin -= abs(diff_y)

        # When the error margin drops below zero, increase y by the step and the error_margin by the x difference
        if error_margin < 0:
            y += step_y
            error_margin += diff_x 

    # The the start and end were swapped, reverse the path
    if swapped:
        path.reverse()

    return path


"""
FLOOR OBJECTS
"""
class FloorObject(Agent):
    def __init__(
        self,
        pos: Coordinate,
        traversable: bool,
        model = None,
    ):
        rand_id = get_random_id()
        super().__init__(rand_id,model)
        self.pos = pos
        self.traversable = traversable
        
    def get_position(self):
        return self.pos

class Sight(FloorObject):
    def __init__(self, pos, model):
        super().__init__(
            pos, traversable=True,model=model
        )

    def get_position(self):
        return self.pos

class Door(FloorObject):
    def __init__(self,pos,model):
        super().__init__(pos,traversable=True,model=model)


class EmergencyExit(FloorObject):
    def __init__(self, pos, model):
        super().__init__(
            pos, traversable=True,model=model
        )

class Wall(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=False, model=model)

class Furniture(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=False, model=model)

class Tree(FloorObject):
    def __init__(self,pos,model):
        super().__init__(pos,traversable=False,model=model)

class Bridge(FloorObject):
    def __init__(self,pos,model):
        super().__init__(pos,traversable=True,model=model)

class DeadHuman(FloorObject):
    def __init__(self,pos,model):
        super().__init__(pos,traversable=True,model=model)

class Tile(FloorObject):
    def __init__(self,pos,elevation,model):
        super().__init__(pos,traversable=True,model=model)
        self.elevation = elevation
        
class Highway(FloorObject):
    def __init__(self,pos,model):
        super().__init__(pos,traversable=True,model=model)
        
class Path(FloorObject):
    def __init__(self,pos,model):
        super().__init__(pos,traversable=True,model=model)
        
class AgricultureField(FloorObject):
    def __init__(self,pos,model):
        super().__init__(pos,traversable=True,model=model)



        



"""
WATER STUFF
"""

class Water(FloorObject):  #step for water needs to look like step for raindrop
#in real space scenario water will be treated as a GeoAgent

 # def step(self):
 #        if self.is_at_boundary:
 #            self.model.schedule.remove(self)
 #        else:
 #            lowest_pos = min(
 #                self.model.space.raster_layer.get_neighboring_cells(
 #                    pos=self.pos, moore=True, include_center=True
 #                ),
 #                key=lambda cell: cell.elevation + cell.water_level,
 #            ).pos
 #            if not lowest_pos == self.pos:
 #                self.model.space.move_raindrop(self, lowest_pos)

    def __init__(self,pos,model):
        super().__init__(
            pos,
            traversable=True,
            model=model,
        )
        self.elevation = 6

    def step(self):
        dont_spread = [Water,Furniture,Wall,Bridge,FirstResponder]
        neighborhood = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False,radius=1)
        own_contents = self.model.grid.get_cell_list_contents(self.pos)
        own_elevation = 0 
        
        
        for agent in own_contents:
            if isinstance(agent,Tile):
                own_elevation = agent.elevation
                
        for cell in neighborhood:
            cont = self.model.grid.get_cell_list_contents((cell[0],cell[1])) #x and y coordinates of the neighbouring cells, get contents of neighbouring cells
            flag = False
            for agent in cont:
                for i in dont_spread:
                    if isinstance(agent,i):
                        flag = True
                        break
                    
            if flag == False:
                neighbour_elevation = 0
                for agent in cont:
                    if isinstance(agent,Tile):
                        neighbour_elevation = agent.elevation
                        
                if neighbour_elevation <= own_elevation:  
                        
                    water = Water((cell[0],cell[1]),self.model)
                    water.unique_id = get_random_id()
                    self.model.schedule.add(water)
                    self.model.grid.place_agent(water,(cell[0],cell[1]))

    def get_position(self):
        return super().get_position()

class Government(Agent):
    def __init__(self,
                 #unique_id,
                 #initial_risk,
                activates: bool,
                pos: Coordinate,
                #response,
                model):
        
        rand_id = get_random_id()
        super().__init__(rand_id, model)
        
        
        self.activates = activates
        self.pos = pos
        #self.vision = vision
        #self.planned_response : tuple[Agent,Coordinate] = (None,None,)
        #self.visible_area : tuple[Coordinate, tuple[Agent]] = []
        
    def get_position(self):
        return self.pos
        
 
class Forecaster(Government):
    def __init__(self, initial_risk,
                 #activation_threshold,
                pos,activates,model):
        super().__init__(activates,pos,model)
        
        self.initial_risk = initial_risk
        #self.activation_threshold = activation_threshold
        #what the agent does at each step
    def step(self):
        if random.uniform(0,1) > self.initial_risk: #if number greater than initial risk then agent gets activated
            self.activates = True
        
        #immediate activation
        if self.activates == True: ##and the threshold is a certain value but action isn't taken 
            self.take_action()
        
        #delayed activation
        # if self.activates == True and random.uniform(0,1) > self.activation_threshold:
        #     self.take_action = True
            
    def take_action(self):
        # for agents in self.visible_tiles:
        #     for agent in agents:
        #         if isinstance(agent,Human):
                    self.model.alarm = True 
                    print('Alarm activated')#how will this alarm be released, maybe only available as information to agents
        # add threshold to take action or do nothing, low and high threshold 
                    
class FirstResponder(Government):
    
    def __init__(self,vision,activates,pos, model):
        super().__init__(activates,pos, model)
        self.traversable = True
        self.vision = vision
        #self.level_of_movement = level_of_movement
        self.planned_target : tuple[Agent,Coordinate] = (None,None)
        self.possible_locations = []
        
        self.visible_tiles : tuple[Coordinate, tuple[Agent]] = []    #Think how this will play out in water context

        self.known_tiles: dict[Coordinate, set[Agent]] = {}

        self.visited_tiles: set[Coordinate] = {self.pos}

        self.knowledge = 0 


    def update_sight_tiles(self, visible_neighborhood):
        if len(self.visible_tiles) > 0:
            # Remove old vision tiles
            for pos, _ in self.visible_tiles:
                contents = self.model.grid.get_cell_list_contents(pos)
                for agent in contents:
                    if isinstance(agent, Sight):
                        self.model.grid.remove_agent(agent)
                        print("sight removed")

        # Add new vision tiles
        for contents, tile in visible_neighborhood:
            # Don't place if the tile has contents but the agent can't see it
            if self.model.grid.is_cell_empty(tile) or len(contents) > 0:
                sight_object = Sight(tile, self.model)
                self.model.grid.place_agent(sight_object, tile)

    # A strange implementation of ray-casting, using Bresenham's Line Algorithm, which takes into account smoke and visibility of objects
    
    def get_visible_tiles(self) -> tuple[Coordinate, tuple[Agent]]:
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius=self.vision
        )
        visible_neighborhood = set()

        # A set of already checked tiles, for avoiding repetition and thus increased efficiency
        checked_tiles = set()

        # Reverse the neighborhood so we start from the furthest locations and work our way inwards
        for pos in reversed(neighborhood):
            if pos not in checked_tiles:
                blocked = False
                try:
                    path = get_line(self.pos, pos)

                    for i, tile in enumerate(path):
                        contents = self.model.grid.get_cell_list_contents(tile)
                        visible_contents = []
                        for obj in contents:
                            if isinstance(obj, Sight):
                                # ignore sight tiles
                                continue
                            elif isinstance(obj, Wall):
                                # We hit a wall, reject rest of path and move to next
                                blocked = True
                                break
                            if not isinstance(obj,Sight):
                                visible_contents.append(obj)

                        if blocked:
                            checked_tiles.update(
                                path[i:]
                            )  # Add the rest of the path to checked tiles, since we now know they are not visible
                            break
                        else:
                            # If a wall didn't block the way, add the visible agents at this location
                            checked_tiles.add(
                                tile
                            )  # Add the tile to checked tiles so we don't check it again
                            visible_neighborhood.add((tile, tuple(visible_contents)))

                except Exception as e:
                    print(e)

        if self.model.visualise_vision:
            self.update_sight_tiles(visible_neighborhood)

        return tuple(visible_neighborhood)

    def location_is_traversable(self, pos) -> bool:
        if not self.model.grid.is_cell_empty(pos):
            contents = self.model.grid.get_cell_list_contents(pos)
            for agent in contents:
                if not agent.traversable:
                    return False

        return True

    def get_path(self, graph, target, include_target=True) -> list[Coordinate]:
        path = []
        visible_tiles_pos = [pos for pos, _ in self.visible_tiles]

        try:
            if target in visible_tiles_pos:  # Target is visible, so simply take the shortest path
                path = nx.shortest_path(graph, self.pos, target)
            else:  # Target is not visible, so do less efficient pathing
                # TODO: In the future this could be replaced with a more naive path algorithm
                path = nx.shortest_path(graph, self.pos, target)

                if not include_target:
                    del path[
                        -1
                    ]  # We don't want the target included in the path, so delete the last element

            return list(path)
        except nx.exception.NodeNotFound as e:
            graph_nodes = graph.nodes()

            if target not in graph_nodes:
                contents = self.model.grid.get_cell_list_contents(target)
                print(f"Target node not found! Expected {target}, with contents {contents}")
                return path
            elif self.pos not in graph_nodes:
                contents = self.model.grid.get_cell_list_contents(self.pos)
                raise Exception(
                    f"Current position not found!\nPosition: {self.pos},\nContents: {contents}"
                )
            else:
                raise e

        except nx.exception.NetworkXNoPath as e:
            print(f"No path between nodes! ({self.pos} -> {target})")
            return path

    def get_next_location(self, path):
        path_length = len(path)
        #speed_int = int(np.round(self.speed))

        speed_int = 3
        try:
            if path_length <= speed_int:
                next_location = path[path_length - 1]
            else:
                next_location = path[speed_int]

            next_path = []
            for location in path:
                next_path.append(location)
                if location == next_location:
                    break

            return (next_location, next_path)
        except Exception as e:
            raise Exception(
                f"Failed to get next location: {e}\nPath: {path},\nlen: {len(path)},\nSpeed: {self.speed}"
            )

    def get_random_target(self, allow_visited=True):
        graph_nodes = self.model.graph.nodes() #perform set like operations, finds shortest path 

        known_pos = set(self.known_tiles.keys())

        # If we are excluding visited tiles, remove the visited_tiles set from the available tiles
        if not allow_visited:
            known_pos -= self.visited_tiles

        traversable_pos = [pos for pos in known_pos if self.location_is_traversable(pos)]

        while not self.planned_target[1]:
            i = np.random.choice(len(traversable_pos))
            target_pos = traversable_pos[i]
            if target_pos in graph_nodes and target_pos != self.pos:
                self.planned_target = (None, target_pos)


    def update_target(self):
        # If there was a target agent, check if target has moved or still exists
        planned_agent = self.planned_target[0]
        if planned_agent:
            current_pos = planned_agent.get_position()
            if current_pos and current_pos != self.planned_target[1]:  # Agent has moved
                self.planned_target = (planned_agent, current_pos)
                # print("Target agent moved. Updating current position:", self.planned_target)
            elif not current_pos:  # Agent no longer exists
                # print("Target agent no longer exists. Dropping.", self.planned_target, current_pos)
                self.planned_target = (None, None)
                self.planned_action = None
    

    def move_toward_target(self):
        next_location: Coordinate = None
        pruned_edges = set()
        graph = deepcopy(self.model.graph)

        self.update_target()  # Get the latest location of a target, if it still exists
        # if self.planned_action:  # And if there's an action, check if it's still possible
        #     self.update_action()

        while self.planned_target[1] and not next_location:
            if self.location_is_traversable(self.planned_target[1]):
                # Target is traversable
                path = self.get_path(graph, self.planned_target[1])
            else:
                # Target is not traversable (e.g. we are going to another Human), so don't include target in the path
                path = self.get_path(graph, self.planned_target[1], include_target=False)

            if len(path) > 0:
                next_location, next_path = self.get_next_location(path)

                if next_location == self.pos:
                    continue

                if next_location == None:
                    raise Exception("Next location can't be none")

                # if self.check_retreat(next_path, next_location):
                #     # We are retreating and therefore need to try a totally new path, so continue from the start of the loop
                #     continue

                # Test the next location to see if we can move there
                if self.location_is_traversable(next_location):
                    # Move normally
                    self.previous_pos = self.pos
                    self.model.grid.move_agent(self, next_location)
                    self.visited_tiles.add(next_location)

                    # if self.carrying:
                    #     agent = self.carrying
                    #     if agent.get_status() == Human.Status.DEAD:
                    #         # Agent is dead, so we can't carry them any more
                    #         self.stop_carrying()
                    #     else:
                    #         # Agent is alive, so try to move them
                    #         try:
                    #             self.model.grid.move_agent(self.carrying, self.pos)
                    #         except Exception as e:
                    #             agent = self.carrying
                    #             raise Exception(
                    #                 f"Failed to move carried agent:\nException:{e}\nAgent: {agent}\nAgent Position: {agent.get_position()}\nSelf Agent Positon: {self.pos}"
                    #             )

                elif self.pos == path[-1]:
                    # The human reached their target!

                    # if self.planned_action:
                    #     self.perform_action()

                    self.planned_target = (None, None)
                    self.planned_action = None
                    break

                # else:
                #     # We want to move here but it's blocked

                #     # check if the location is blocked due to a Human agent
                #     pushed = False
                #     contents = self.model.grid.get_cell_list_contents(next_location)
                #     for agent in contents:
                #         # Test the panic value to see if this agent "pushes" the blocking agent aside
                #         if (
                #             isinstance(agent, Human)
                #             and agent.mobility != Human.Mobility.INCAPACITATED
                #         ) and (
                #             (
                #                 self.get_panic_score() >= self.PANIC_THRESHOLD
                #                 and self.mobility == Human.Mobility.NORMAL
                #             )
                #             or self.mobility == Human.Mobility.PANIC
                #         ):
                #             # push the agent and then move to the next_location
                #             self.push_human_agent(agent)
                #             self.previous_pos = self.pos
                #             self.model.grid.move_agent(self, next_location)
                #             self.visited_tiles.add(next_location)
                #             pushed = True
                #             break
                #     if pushed:
                #         continue

                #     # Remove the next location from the temporary graph so we can try pathing again without it
                #     edges = graph.edges(next_location)
                #     pruned_edges.update(edges)
                #     graph.remove_node(next_location)

                #     # Reset planned_target if the next location was the end of the path
                #     if next_location == path[-1]:
                #         next_location = None
                #         self.planned_target = (None, None)
                #         self.planned_action = None
                #         break
                #     else:
                #         next_location = None

            else:  # No path is possible, so drop the target
                self.planned_target = (None, None)
                self.planned_action = None
                break

        if len(pruned_edges) > 0:
            # Add back the edges we removed when removing any non-traversable nodes from the global graph, because they may be traversable again next step
            graph.add_edges_from(list(pruned_edges))

   
    def check_for_incapacitation(self) :
        
        num_incap = 0
        coord = []
        self.planned_target = (None, None)
        
        for _, agents in self.visible_tiles:
            for agent in agents:
                if isinstance(agent, Human) and agent.get_mobility() == Human.Mobility.INCAPACITATED:
                    print(f'agent {agent.unique_id} is incap with panic score {agent.get_panic_score()}, health {agent.health}')
                    num_incap += 1
                    x = agent.get_position()
                    coord.append(x)
                    print("this is the incap agents location", coord)
        
        self.possible_locations = coord
        return coord, num_incap


    def get_best(self):
        coord = self.possible_locations

        if len(coord) == 0:
            print("length of coord is 0")
            pass

        elif len(coord) == 1:
            print("length of cooord is 1")
            self.planned_target = (None,coord[0])

        else:
            print("length of coord is greater than 1")
            dist = 100000
            curr = coord[0]
            for cell in coord:
                x = cell[0]
                y = cell[1]

                diff = abs(self.pos[0]-x) + abs(self.pos[1]-y)

                if diff < dist:
                    curr = cell
                    dist = diff 

            new_pos = curr
            self.planned_target = (None,new_pos)


        return self.planned_target[1]
    
    
    
    
    def attempt_rescue_plan(self):
        
        coord, num_incap = self.check_for_incapacitation()
        self.possible_locations = coord
        
        next_pos = self.get_best()


        self.move_toward_target()
    
    # def move_towards_incap_agent(self,location):
        
    #     x = self.check_for_incapacitation()
        
    #     path = get_line(self.pos, x)
        
        # incap_num = 0
        # possible_area = self.model.grid.get_neighborhood(
        #     self.pos, moore = True, include_center = False)
        
        # for cell in possible_area:
        #     #contents = self.model.grid.get_cell_list_contents(next_location)
        
        #     cont = self.model.grid.get_cell_list_contents((cell[0],cell[1])) #x and y coordinates of the neighbouring cells, get contents of neighbouring cells
            
        #     for agent in cont:
        #         if isinstance(agent,Human) and agent.get_mobility() == Human.Mobility.INCAPACITATED:
        #             print('Found in cap Agent') 
        #             incap_num += 1
                
        
    def learn_environment(self):
        if self.knowledge < 1:  # If there is still something to learn
            new_tiles = 0

            for pos, agents in self.visible_tiles:
                if pos not in self.known_tiles.keys():
                    new_tiles += 1
                self.known_tiles[pos] = set(agents)

            # update the knowledge Attribute accordingly
            total_tiles = self.model.grid.width * self.model.grid.height
            new_knowledge_percentage = new_tiles / total_tiles
            self.knowledge = self.knowledge + new_knowledge_percentage
        
        
    def step(self):
        
        if self.model.alarm == True:
            self.activates = True
            
        self.visible_tiles = self.get_visible_tiles()
        self.learn_environment()
            
        if self.activates == True:
            planned_pos = self.planned_target[1]
            
            if not planned_pos:
                self.get_random_target()
            
            else:
                print("attempting rescue plan")
                self.attempt_rescue_plan()
            #self.take_action()
            #self.visible_area = self.get_visible_area()
        
            
    def move(self):
        
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore = True, include_center = False)
    
        new_position = random.choice(possible_steps)
      
        self.model.grid.move_agent(self, new_position)
        
    def get_position(self):
        return super().get_position()
    
    
    
    def take_action(self):
        neighbourhood_area = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False,radius=1)
                
        for cell in neighbourhood_area:
            contents = self.model.grid.get_cell_list_contents((cell[0], cell[1]))
            for agent in contents:
                if isinstance(agent,Human):
                    if agent.get_mobility() == Human.Mobility.INCAPACITATED:
                        path = get_line(self.pos, (cell[0], cell[1]))
                        self.model.grid.move_agent(self, path)
                        
   

class Human(Agent):
    """
    A human agent, which will attempt to escape from the grid.

    Attributes:
        ID: Unique identifier of the Agent
        Position (x,y): Position of the agent on the Grid
        Health: Health of the agent (between 0 and 1)
        ...
    """
    class Mobility(IntEnum):
        INCAPACITATED = 0
        NORMAL = 1
        PANIC = 2

    class Status(IntEnum):
        DEAD = 0
        ALIVE = 1
        ESCAPED = 2

    class Action(IntEnum):
        PHYSICAL_SUPPORT = 0
        MORALE_SUPPORT = 1
        VERBAL_SUPPORT = 2
        RETREAT = 3


    MIN_HEALTH = 0.0
    MAX_HEALTH = 5.0

    MIN_EXPERIENCE = 1
    MAX_EXPERIENCE = 10

    MIN_SPEED = 0.0
    MAX_SPEED = 8.0

    MIN_KNOWLEDGE = 0
    MAX_KNOWLEDGE = 1

    MAX_SHOCK = 1.0
    MIN_SHOCK = 0.0
    # Shock modifiers when encountering certain objects per object, per step
    DEFAULT_SHOCK_MODIFIER = -0.1  # The default amount the shock value will change per step
    SHOCK_MODIFIER_DEAD_HUMAN = 1.0
    SHOCK_MODIFIER_WATER = 0.8   #changing the shock modifier for testing
    SHOCK_MODIFIER_AFFECTED_HUMAN = 0.1

    # The value the panic score must reach for an agent to start panic behaviour
    PANIC_THRESHOLD = 0.9             #modifying the panic threshold to 0.9

    HEALTH_MODIFIER_WATER = 0.5

    SPEED_MODIFIER_WATER = 0.1  #Think about this, depending on elevation diff speed modifiers

    # When the health value drops below this value, the agent will being to slow down
    SLOWDOWN_THRESHOLD = 0.5

    MIN_PUSH_DAMAGE = 0.01
    MAX_PUSH_DAMAGE = 0.2

    def __init__(
        self,
        pos: Coordinate,
        health: float,
        speed: float,
        collaborates: bool,
        vision,
        nervousness,
        experience,
        believes_alarm: bool,
        model,
    ):
        rand_id = get_random_id()
        super().__init__(rand_id, model)
        
        self.traversable = False

        self.pos = pos
        self.health = health
        self.mobility: Human.Mobility = Human.Mobility.NORMAL
        self.shock: int = self.MIN_SHOCK
        self.speed = speed
        self.vision = vision
        self.collaborates = collaborates
        self.nervousness = nervousness

        self.verbal_collaboration_count: int = 0
        self.morale_collaboration_count: int = 0
        self.physical_collaboration_count: int = 0

        self.morale_boost: bool = False
        self.carried: bool = False
        self.carrying: Union(Human,None) = None

        self.knowledge = self.MIN_KNOWLEDGE
        self.nervousness = self.nervousness
        self.experience = experience
        self.believes_alarm = believes_alarm
        self.escaped: bool = False

        self.planned_target: tuple[Agent,Coordinate] = (
            None,
            None,
        )

        self.planned_action: Human.Action = None

        self.visible_tiles : tuple[Coordinate, tuple[Agent]] = []    #Think how this will play out in water context

        self.known_tiles: dict[Coordinate, set[Agent]] = {}

        self.visited_tiles: set[Coordinate] = {self.pos}

    ##why is this done ? 
    def update_sight_tiles(self, visible_neighborhood):
        if len(self.visible_tiles) > 0:
            # Remove old vision tiles
            for pos, _ in self.visible_tiles:
                contents = self.model.grid.get_cell_list_contents(pos)
                for agent in contents:
                    if isinstance(agent, Sight):
                        self.model.grid.remove_agent(agent)
                        print("sight removed")

        # Add new vision tiles
        for contents, tile in visible_neighborhood:
            # Don't place if the tile has contents but the agent can't see it
            if self.model.grid.is_cell_empty(tile) or len(contents) > 0:
                sight_object = Sight(tile, self.model)
                self.model.grid.place_agent(sight_object, tile)

    # A strange implementation of ray-casting, using Bresenham's Line Algorithm, which takes into account 
    #smoke and visibility of objects
    
    def get_visible_tiles(self) -> tuple[Coordinate, tuple[Agent]]:
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius=self.vision
        )
        visible_neighborhood = set()

        # A set of already checked tiles, for avoiding repetition and thus increased efficiency
        checked_tiles = set()

        # Reverse the neighborhood so we start from the furthest locations and work our way inwards
        for pos in reversed(neighborhood):
            if pos not in checked_tiles:
                blocked = False
                try:
                    path = get_line(self.pos, pos)

                    for i, tile in enumerate(path):
                        contents = self.model.grid.get_cell_list_contents(tile)
                        visible_contents = []
                        for obj in contents:
                            if isinstance(obj, Sight):
                                # ignore sight tiles
                                continue
                            elif isinstance(obj, Wall):
                                # We hit a wall, reject rest of path and move to next
                                blocked = True
                                break
                            if not isinstance(obj,Sight):
                                visible_contents.append(obj)

                        if blocked:
                            checked_tiles.update(
                                path[i:]
                            )  # Add the rest of the path to checked tiles, since we now know they are not visible
                            break
                        else:
                            # If a wall didn't block the way, add the visible agents at this location
                            checked_tiles.add(
                                tile
                            )  # Add the tile to checked tiles so we don't check it again
                            visible_neighborhood.add((tile, tuple(visible_contents)))

                except Exception as e:
                    print(e)

        if self.model.visualise_vision:
            self.update_sight_tiles(visible_neighborhood)

        return tuple(visible_neighborhood)


    def get_random_target(self, allow_visited=True):
        graph_nodes = self.model.graph.nodes() #perform set like operations, finds shortest path 

        known_pos = set(self.known_tiles.keys())

        # If we are excluding visited tiles, remove the visited_tiles set from the available tiles
        if not allow_visited:
            known_pos -= self.visited_tiles

        traversable_pos = [pos for pos in known_pos if self.location_is_traversable(pos)]

        while not self.planned_target[1]:
            i = np.random.choice(len(traversable_pos))
            target_pos = traversable_pos[i]
            if target_pos in graph_nodes and target_pos != self.pos:
                self.planned_target = (None, target_pos)


    def attempt_exit_plan(self):
        #print(f"agent with id {self.unique_id} is attempting to exit")
        self.planned_target = (None, None)
        emergency_exits = set()

        #print(self.known_tiles)
        for pos, agents in self.known_tiles.items():
            for agent in agents:
                if isinstance(agent, EmergencyExit):
                    emergency_exits.add((agent, pos))

        if len(emergency_exits) > 0:
            if len(emergency_exits) > 1:  # If there is more than one exit known
                best_distance = None
                for exit, exit_pos in emergency_exits:
                    length = len(
                        get_line(self.pos, exit_pos)
                    )  # Let's use Bresenham's to find the 'closest' exit
                    if not best_distance or length < best_distance:
                        best_distance = length
                        self.planned_target = (exit, exit_pos)

            else:
                self.planned_target = emergency_exits.pop() #removes item at a given index

            #print(f"Agent {self.unique_id} found an emergency exit.", self.planned_target)
        else:  # If there's a flood and no emergency-exit in sight, try to head for an unvisited door, if no door in sight, move randomly (for now)
            found_door = False
            #print(self.visible_tiles)
            for pos, contents in self.visible_tiles:
                for agent in contents:
                    if isinstance(agent, Door):
                        found_door = True
                        self.planned_target = (agent, pos)
                        break

                if found_door:
                    break

            # Still didn't find a planned_target, so get a random unvisited target
            if not self.planned_target[1]:
                #print("getting random target to move")
                self.get_random_target(allow_visited=False)

    def get_panic_score(self):
        # adding a new component to panic, if there is water around person he will definitely panic
        # neighborhood = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=True,radius=1)
        # flag = False 
        # for cell in neighborhood:
        #     cont = self.model.grid.get_cell_list_contents((cell[0],cell[1])) #for x,y coordinates
        #     for agent in cont:
        #         if isinstance(agent,Water):
        #             flag = True
        #             break
        # if flag == True:
        #     #panic_score = 0.9
        #     panic_score = 0.9
        #     return panic_score
        

        health_component = 1.50 / np.exp(self.health / (self.nervousness))
        experience_component = 1 / np.exp(self.experience / self.nervousness)

        # Calculate the mean of the components
        panic_score = (health_component + experience_component + self.shock) / 3

        #print("Panic score:", panic_score, "Health Score:", health_component, "Experience Score:", experience_component, "Shock score:", self.shock)

        return panic_score


    def incapacitate(self):
        self.stop_carrying()
        self.mobility = Human.Mobility.INCAPACITATED
        self.traversable = True
        print(self.get_panic_score(), self.health, self.nervousness, self.experience)

    def die(self):
        # Store the agent's position of death so we can remove them and place a DeadHuman
        pos = self.pos
        self.model.grid.remove_agent(self)
        dead_self = DeadHuman(pos, self.model)
        self.model.grid.place_agent(dead_self, pos)
        print("Agent died at", pos)

    def health_mobility_rules(self):
        
        contents = self.model.grid.get_cell_list_contents(self.pos)
        for content in contents:
            if isinstance(content,Water):
                self.health -= self.HEALTH_MODIFIER_WATER
                self.speed -= self.SPEED_MODIFIER_WATER

        if self.health < self.MIN_HEALTH:
            self.health = self.MIN_HEALTH
        
        if self.speed < self.MIN_SPEED:
            self.speed = self.MIN_SPEED

        if self.health == self.MIN_HEALTH:
            self.stop_carrying()
            self.die()
        elif self.speed == self.MIN_SPEED:
            print("Incap due to speed becoming min")
            self.incapacitate()

    def panic_rules(self):
        if self.morale_boost:
            return

        shock_modifier = self.DEFAULT_SHOCK_MODIFIER

        for _,agents in self.visible_tiles:
            for agent in agents:
                if isinstance(agent,Water):
                    shock_modifier += self.SHOCK_MODIFIER_WATER - self.DEFAULT_SHOCK_MODIFIER
                if isinstance(agent,DeadHuman):
                    shock_modifier += self.SHOCK_MODIFIER_DEAD_HUMAN - self.DEFAULT_SHOCK_MODIFIER
                if isinstance(agent,Human) and agent.get_mobility() != Human.Mobility.NORMAL:
                    shock_modifier += (
                        self.SHOCK_MODIFIER_AFFECTED_HUMAN - self.DEFAULT_SHOCK_MODIFIER
                    )

        if not self.believes_alarm and shock_modifier != self.DEFAULT_SHOCK_MODIFIER:
            #print(f"Agent {self.unique_id} now believes the flood is real!")
            self.believes_alarm = True

        self.shock += shock_modifier

        # Keep the shock value between 0 and 1
        if self.shock > self.MAX_SHOCK:
            self.shock = self.MAX_SHOCK
        elif self.shock < self.MIN_SHOCK:
            self.shock = self.MIN_SHOCK

        panic_score = self.get_panic_score()

        if panic_score >= self.PANIC_THRESHOLD:
            print("Agent is panicking! Score:", panic_score, "Shock:", self.shock)
            self.stop_carrying()
            self.mobility = Human.Mobility.PANIC

            # when an agent panics, clear known tiles
            # this represents the agent forgetting all logical information about their surroundings,
            # and having to rebuild it once they stop panicking
            # self.known_tiles = {}                    have commented this to let the agent remember the surroundings
            # self.knowledge = 0
        elif panic_score < self.PANIC_THRESHOLD and self.mobility == Human.Mobility.PANIC:
            print("Agent stopped panicking! Score:", panic_score, "Shock:", self.shock)
            self.mobility = Human.Mobility.NORMAL

            
    def learn_environment(self):
        if self.knowledge < self.MAX_KNOWLEDGE:  # If there is still something to learn
            new_tiles = 0

            for pos, agents in self.visible_tiles:
                if pos not in self.known_tiles.keys():
                    new_tiles += 1
                self.known_tiles[pos] = set(agents)

            # update the knowledge Attribute accordingly
            total_tiles = self.model.grid.width * self.model.grid.height
            new_knowledge_percentage = new_tiles / total_tiles
            self.knowledge = self.knowledge + new_knowledge_percentage
            # print("Current knowledge:", self.knowledge)

    def verbal_collaboration(self, target_agent: Self, target_location: Coordinate):
        success = False
        for _, agents in self.visible_tiles:
            for agent in agents:
                if isinstance(agent, Human) and agent.get_mobility() == Human.Mobility.NORMAL:
                    if not agent.believes_alarm:
                        agent.set_believes(True)

                    # Inform the agent of the target location
                    if not target_location in agent.known_tiles:
                        agent.known_tiles[target_location] = set()

                    agent.known_tiles[target_location].add(target_agent)
                    success = True

        if success:
            #print("Agent informed others of an emergency exit!")
            self.verbal_collaboration_count += 1

    def check_for_collaboration(self):
        # If the agent is carrying someone, they are too occupied to do other collaboration
        if self.carrying:
            return

        # if self.test_collaboration():
        for location, visible_agents in self.visible_tiles:
            if self.planned_action:
                break

            for agent in visible_agents:
                if self.planned_action:
                    break
                if isinstance(agent, Human) and not self.planned_action:
                    if agent.get_mobility() == Human.Mobility.INCAPACITATED:
                        # If the agent is incapacitated, help them
                        # Physical collaboration
                        # Plan to move toward the target
                        self.planned_target = (
                            agent,
                            location,
                        )
                        # Plan to carry the agent
                        self.planned_action = Human.Action.PHYSICAL_SUPPORT
                        print(f"Agent {self.unique_id} planned physical collaboration at", location)
                        break
                    elif (
                        agent.get_mobility() == Human.Mobility.PANIC
                        and not self.planned_action
                    ):
                        # Morale collaboration
                        # Plan to move toward the target
                        self.planned_target = (
                            agent,
                            location,
                        )
                        # Plan to do morale collaboration with the agent
                        self.planned_action = Human.Action.MORALE_SUPPORT
                        print("Agent planned morale collaboration at", location)
                        break
                elif isinstance(agent, EmergencyExit):
                    # Verbal collaboration
                    self.verbal_collaboration(agent, location)


    def get_next_location(self, path):
        path_length = len(path)
        speed_int = int(np.round(self.speed))

        try:
            if path_length <= speed_int:
                next_location = path[path_length - 1]
            else:
                next_location = path[speed_int]

            next_path = []
            for location in path:
                next_path.append(location)
                if location == next_location:
                    break

            return (next_location, next_path)
        except Exception as e:
            raise Exception(
                f"Failed to get next location: {e}\nPath: {path},\nlen: {len(path)},\nSpeed: {self.speed}"
            )

    def get_path(self, graph, target, include_target=True) -> list[Coordinate]:
        path = []
        visible_tiles_pos = [pos for pos, _ in self.visible_tiles]

        try:
            if target in visible_tiles_pos:  # Target is visible, so simply take the shortest path
                path = nx.shortest_path(graph, self.pos, target)
            else:  # Target is not visible, so do less efficient pathing
                # TODO: In the future this could be replaced with a more naive path algorithm
                path = nx.shortest_path(graph, self.pos, target)

                if not include_target:
                    del path[
                        -1
                    ]  # We don't want the target included in the path, so delete the last element

            return list(path)
        except nx.exception.NodeNotFound as e:
            graph_nodes = graph.nodes()

            if target not in graph_nodes:
                contents = self.model.grid.get_cell_list_contents(target)
                print(f"Target node not found! Expected {target}, with contents {contents}")
                return path
            elif self.pos not in graph_nodes:
                contents = self.model.grid.get_cell_list_contents(self.pos)
                raise Exception(
                    f"Current position not found!\nPosition: {self.pos},\nContents: {contents}"
                )
            else:
                raise e

        except nx.exception.NetworkXNoPath as e:
            print(f"No path between nodes! ({self.pos} -> {target})")
            return path

    def location_is_traversable(self, pos) -> bool:
        if not self.model.grid.is_cell_empty(pos):
            contents = self.model.grid.get_cell_list_contents(pos)
            for agent in contents:
                if not agent.traversable:
                    return False

        return True


    def update_target(self):
        # If there was a target agent, check if target has moved or still exists
        planned_agent = self.planned_target[0]
        if planned_agent:
            current_pos = planned_agent.get_position()
            if current_pos and current_pos != self.planned_target[1]:  # Agent has moved
                self.planned_target = (planned_agent, current_pos)
                # print("Target agent moved. Updating current position:", self.planned_target)
            elif not current_pos:  # Agent no longer exists
                # print("Target agent no longer exists. Dropping.", self.planned_target, current_pos)
                self.planned_target = (None, None)
                self.planned_action = None

    def update_action(self):
        planned_agent, _ = self.planned_target

        if planned_agent:
            # Agent had planned morale collaboration, but the agent is no longer panicking or no longer alive, so drop it.
            if self.planned_action == Human.Action.MORALE_SUPPORT and (
                planned_agent.get_mobility() != Human.Mobility.PANIC
                or not planned_agent.get_status() == Human.Status.ALIVE
            ):
                # print("Target agent no longer panicking. Dropping action.")
                self.planned_target = (None, None)
                self.planned_action = None
            # Agent had planned physical collaboration, but the agent is no longer incapacitated or has already been carried or is not alive, so drop it.
        elif self.planned_action == Human.Action.PHYSICAL_SUPPORT and (
            (planned_agent.get_mobility() != Human.Mobility.INCAPACITATED)
            or planned_agent.is_carried()
            or planned_agent.get_status() != Human.Status.ALIVE
        ):
            self.planned_target = (None, None)
            self.planned_action = None
            print(f"{self.unique_id} dropped the physical collaboration idea")
        elif self.planned_action == Human.Action.RETREAT:
            return
        else:  # Can no longer perform the action
            self.planned_target = (None, None)
            self.planned_action = None

    def perform_action(self):
        agent, _ = self.planned_target

        if self.planned_action == Human.Action.PHYSICAL_SUPPORT:
            if not agent.is_carried():
                self.carrying = agent
                agent.set_carried(True)
                self.physical_collaboration_count += 1
                print("Agent started carrying another agent")
        elif self.planned_action == Human.Action.MORALE_SUPPORT:
            # Attempt to give the agent a permanent morale boost according to your experience score
            if agent.attempt_morale_boost(self.experience):
                print("Morale boost succeeded")
            else:
                print("Morale boost failed")

            self.morale_collaboration_count += 1

        self.planned_action = None

    def push_human_agent(self, agent: Self):
        # push the agent to a random 1 square away traversable Coordinate
        neighborhood = self.model.grid.get_neighborhood(
            agent.get_position(),
            moore=True,
            include_center=False,
            radius=1,
        )
        traversable_neighborhood = [
            neighbor_pos
            for neighbor_pos in neighborhood
            if self.location_is_traversable(neighbor_pos)
        ]

        if len(traversable_neighborhood) > 0:
            # push the human agent to a random traversable position
            i = np.random.choice(len(traversable_neighborhood))
            push_pos = traversable_neighborhood[i]
            print(
                f"Agent {self.unique_id} pushed agent {agent.unique_id} from {agent.pos} to {push_pos}"
            )
            self.model.grid.move_agent(agent, push_pos)

            # inure the pushed agent slightly
            current_health = agent.get_health()
            damage = np.random.uniform(self.MIN_PUSH_DAMAGE, self.MAX_PUSH_DAMAGE)
            agent.set_health(current_health - damage)
        else:
            neighborhood_contents = {}
            for pos in neighborhood:
                neighborhood_contents[pos] = self.model.grid.get_cell_list_contents(pos)
            print(
                f"Could not push agent due to no traversable locations.\nNeighborhood Contents: {neighborhood_contents}"
            )

    def move_toward_target(self):
        next_location: Coordinate = None
        pruned_edges = set()
        graph = deepcopy(self.model.graph)

        self.update_target()  # Get the latest location of a target, if it still exists
        if self.planned_action:  # And if there's an action, check if it's still possible
            self.update_action()

        while self.planned_target[1] and not next_location:
            if self.location_is_traversable(self.planned_target[1]):
                # Target is traversable
                path = self.get_path(graph, self.planned_target[1])
            else:
                # Target is not traversable (e.g. we are going to another Human), so don't include target in the path
                path = self.get_path(graph, self.planned_target[1], include_target=False)

            if len(path) > 0:
                next_location, next_path = self.get_next_location(path)

                if next_location == self.pos:
                    continue

                if next_location == None:
                    raise Exception("Next location can't be none")

                # if self.check_retreat(next_path, next_location):
                #     # We are retreating and therefore need to try a totally new path, so continue from the start of the loop
                #     continue

                # Test the next location to see if we can move there
                if self.location_is_traversable(next_location):
                    # Move normally
                    self.previous_pos = self.pos
                    self.model.grid.move_agent(self, next_location)
                    self.visited_tiles.add(next_location)

                    if self.carrying:
                        agent = self.carrying
                        if agent.get_status() == Human.Status.DEAD:
                            # Agent is dead, so we can't carry them any more
                            self.stop_carrying()
                        else:
                            # Agent is alive, so try to move them
                            try:
                                self.model.grid.move_agent(self.carrying, self.pos)
                            except Exception as e:
                                agent = self.carrying
                                raise Exception(
                                    f"Failed to move carried agent:\nException:{e}\nAgent: {agent}\nAgent Position: {agent.get_position()}\nSelf Agent Positon: {self.pos}"
                                )

                elif self.pos == path[-1]:
                    # The human reached their target!

                    if self.planned_action:
                        self.perform_action()

                    self.planned_target = (None, None)
                    self.planned_action = None
                    break

                else:
                    # We want to move here but it's blocked

                    # check if the location is blocked due to a Human agent
                    pushed = False
                    contents = self.model.grid.get_cell_list_contents(next_location)
                    for agent in contents:
                        # Test the panic value to see if this agent "pushes" the blocking agent aside
                        if (
                            isinstance(agent, Human)
                            and agent.mobility != Human.Mobility.INCAPACITATED
                        ) and (
                            (
                                self.get_panic_score() >= self.PANIC_THRESHOLD
                                and self.mobility == Human.Mobility.NORMAL
                            )
                            or self.mobility == Human.Mobility.PANIC
                        ):
                            # push the agent and then move to the next_location
                            self.push_human_agent(agent)
                            self.previous_pos = self.pos
                            self.model.grid.move_agent(self, next_location)
                            self.visited_tiles.add(next_location)
                            pushed = True
                            break
                    if pushed:
                        continue

                    # Remove the next location from the temporary graph so we can try pathing again without it
                    edges = graph.edges(next_location)
                    pruned_edges.update(edges)
                    graph.remove_node(next_location)

                    # Reset planned_target if the next location was the end of the path
                    if next_location == path[-1]:
                        next_location = None
                        self.planned_target = (None, None)
                        self.planned_action = None
                        break
                    else:
                        next_location = None

            else:  # No path is possible, so drop the target
                self.planned_target = (None, None)
                self.planned_action = None
                break

        if len(pruned_edges) > 0:
            # Add back the edges we removed when removing any non-traversable nodes from the global graph, because they may be traversable again next step
            graph.add_edges_from(list(pruned_edges))

    def step(self):
        
        #print("Hi, I am agent " + str(self.unique_id) + ".")

        if not self.escaped and self.pos:
            self.health_mobility_rules()

            if self.mobility == Human.Mobility.INCAPACITATED or not self.pos:
                # Incapacitated or died, so return already
                return

            self.visible_tiles = self.get_visible_tiles()

            self.panic_rules()

            self.learn_environment()

            planned_target_agent = self.planned_target[0]

            # If a flood has started and the agent believes it, attempt to plan an exit location if we haven't already and we aren't performing an action
            if self.model.alarm and self.believes_alarm:
                if not isinstance(planned_target_agent, EmergencyExit) and not self.planned_action:
                    self.attempt_exit_plan()

                # Check if anything in vision can be collaborated with, if the agent has normal mobility
                if self.mobility == Human.Mobility.NORMAL and self.collaborates:
                    self.check_for_collaboration()

            planned_pos = self.planned_target[1]
            if not planned_pos:
                self.get_random_target()
            elif self.mobility == Human.Mobility.PANIC:  # Panic
                panic_score = self.get_panic_score()

                if panic_score >= 0.9: #and np.random.random() < panic_score:
                    # If they have above 90% panic score, test the score to see if they faint
                    print("Agent fainted!")
                    self.incapacitate()
                    print("agent is incapacitated")
                    return
                # if (
                #     np.random.random() < panic_score
                # ):  # Test their panic score to see if they will move randomly, or keep their original target
                #     print("Agent moving randomly in panic!")
                #     self.planned_action = None
                #     self.planned_target = (None, None)
                #     self.get_random_target()

            self.move_toward_target()

            # Agent reached a fire escape, proceed to exit
            if self.model.fire_started and self.pos in self.model.fire_exits.keys():
                if self.carrying:
                    carried_agent = self.carrying
                    carried_agent.escaped = True
                    self.model.grid.remove_agent(carried_agent)

                self.escaped = True
                self.model.grid.remove_agent(self)

    def get_status(self):
        if self.health > self.MIN_HEALTH and not self.escaped:
            return Human.Status.ALIVE
        elif self.health <= self.MIN_HEALTH and not self.escaped:
            return Human.Status.DEAD
        elif self.escaped:
            return Human.Status.ESCAPED

        return None

    def get_speed(self):
        return self.speed

    def get_mobility(self):
        return self.mobility

    def get_health(self):
        return self.health

    def get_position(self):
        return self.pos

    def get_plan(self):
        return (self.planned_target, self.planned_action)

    def set_plan(self, agent, location):
        self.planned_action = None
        self.planned_target = (agent, location)

    def set_health(self, value: float):
        self.health = value

    def set_believes(self, value: bool):
        if value and not self.believes_alarm:
            print("Agent told to believe the alarm!")

        self.believes_alarm = value

    def attempt_morale_boost(self, experience: int):
        rand = np.random.random()
        if rand < (experience / self.MAX_EXPERIENCE):
            self.morale_boost = True
            self.mobility = Human.Mobility.NORMAL
            return True
        else:
            return False

    def stop_carrying(self):
        if self.carrying:
            carried_agent = self.carrying
            carried_agent.set_carried(False)
            self.carrying = None
            self.planned_action = None
            print("Agent stopped carrying another agent")

    def set_carried(self, value: bool):
        self.carried = value

    def is_carried(self):
        return self.carried

    def is_carrying(self):
        if self.carrying:
            return True
        else:
            return False

    def get_verbal_collaboration_count(self):
        return self.verbal_collaboration_count

    def get_morale_collaboration_count(self):
        return self.morale_collaboration_count

    def get_physical_collaboration_count(self):
        return self.physical_collaboration_count



    


    