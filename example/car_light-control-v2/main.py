import random
import carla

import time

from carla.libcarla import ActorBlueprint, World

import inspect

from pycarlanet.utils import InstanceExist
from pycarlanet.listeners import WorldManager, ActorManager, AgentManager
from pycarlanet.enum import SimulatorStatus, CarlaMaplayers
from pycarlanet import CarlaClient, SocketManager, ActorType, CarlanetActor
from pycarlanet import SimulationManager

import sys
import signal
from functools import partial

import json

# get light control enum from int value
def _str_to_light_control_enum(light_value):
    if light_value == 0:
        return carla.VehicleLightState.NONE
    elif light_value == 1:
        return carla.VehicleLightState.Position
    elif light_value == 2:
        return carla.VehicleLightState.Brake
    elif light_value == 3:
        return carla.VehicleLightState.All

    print("error _str_to_light_control_enum")
    raise SystemError("error _str_to_light_control_enum")
    
# get int value from light control enum
def _light_control_enum_to_str(light_enum):
    if light_enum == carla.VehicleLightState.NONE:
        return 0
    elif light_enum == carla.VehicleLightState.Position:
        return 1
    elif light_enum == carla.VehicleLightState.Brake:
        return 2
    elif light_enum == carla.VehicleLightState.All or light_enum == carla.VehicleLightState(2047):
        return 3
    
    print("error _light_control_enum_to_str")
    raise SystemError("error _light_control_enum_to_str")


class wManager(WorldManager):
    #timestamp = 4.0
    def omnet_init_completed(self, message) -> SimulatorStatus:
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name} -> start")
        super().omnet_init_completed(message=message)
        super().load_world("Town05_opt", [CarlaMaplayers.Buildings, CarlaMaplayers.Foliage])
        self.tick()
        self.world.set_weather(carla.WeatherParameters.ClearNight)
        self.tick()
        traffic_manager = CarlaClient.instance.client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
        traffic_manager.set_random_device_seed(message['carla_configuration']['seed'])
        self.tick()
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name} -> end")        
        return SimulatorStatus.RUNNING

    def after_world_tick(self, timestamp) -> SimulatorStatus:
        return SimulatorStatus.RUNNING
        if timestamp > 20:
           return SimulatorStatus.FINISHED_OK
        else:
            return SimulatorStatus.RUNNING

    #mock for testing purpose
    #def get_elapsed_seconds(self): return self.timestamp
    
    #mock for testing purpose
    #def tick(self): self.timestamp += 0.1
    
    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        return SimulatorStatus.RUNNING, {"message": "from carla"}



class aManager(ActorManager):
    def omnet_init_completed(self, message):
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name} -> start")
        super().omnet_init_completed(message)
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name} -> end")
        #print(f"ActorType from aManager {ActorType.instance.get_available_types()}")
        try:
            raise Exception("test")
            with open(f"./configurations/{message['user_defined']['config_name']}.json", 'r') as file:
                data = json.load(file)
                for actor in data["vehicles"]:
                    print(actor)
                    if actor['actor_type'] == 'car':
                        blueprint: ActorBlueprint = random.choice(CarlaClient.instance.world.get_blueprint_library().filter(actor['model']))
                        spawn_points = CarlaClient.instance.world.get_map().get_spawn_points()
                        spawn_point = random.choice(spawn_points)
                        response = CarlaClient.instance.client.apply_batch_sync([carla.command.SpawnActor(blueprint, spawn_point)])[0]
                        carla_actor: carla.Vehicle = CarlaClient.instance.world.get_actor(response.actor_id)
                        carla_actor.set_simulate_physics(True)
                        carla_actor.set_autopilot(False)
                        self.add_carla_actor_to_omnet(carla_actor, ActorType.instance.get_available_types()[0])
        except Exception as error:
            print(error)
        
        


    @InstanceExist(CarlaClient)
    def create_actors_from_omnet(self, actors):
        print("create_actors_from_omnet")
        print(actors)
        
        for actor in actors:
            if actor['actor_type'] == 'car':
                blueprint: ActorBlueprint = random.choice(CarlaClient.instance.world.get_blueprint_library().filter("vehicle.tesla.model3"))
                spawn_points = CarlaClient.instance.world.get_map().get_spawn_points()
                spawn_point = random.choice(spawn_points)
                response = CarlaClient.instance.client.apply_batch_sync([carla.command.SpawnActor(blueprint, spawn_point)])[0]
                carla_actor: carla.Vehicle = CarlaClient.instance.world.get_actor(response.actor_id)
                carla_actor.set_simulate_physics(True)
                carla_actor.set_autopilot(True)
                if actor['actor_id'] == '':
                    self.add_carla_actor_to_omnet(carla_actor, ActorType.instance.get_available_types()[0])
                else:
                    carlanet_actor = CarlanetActor(carla_actor, ActorType.instance.get_available_types()[0])
                    self._carlanet_actors[actor['actor_id']] = carlanet_actor
            else:
                raise RuntimeError(f"I don\'t know this type {actor['actor_type']}")
    
    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        if not 'msg_type' in message: return SimulatorStatus.RUNNING, {'message': 'from carla'}
        if message['msg_type'] == 'LIGHT_COMMAND':
            next_light_state = _str_to_light_control_enum(int(message['light_next_state']))
            key = next(iter(self._carlanet_actors))
            car: carla.Actor = self._carlanet_actors[key].carla_actor
            car.set_light_state(next_light_state)
            msg_to_send = {
                'msg_type': 'LIGHT_UPDATE',
                'light_curr_state': f'{_light_control_enum_to_str(car.get_light_state())}'
            }
            return SimulatorStatus.RUNNING, msg_to_send
        else:
            raise RuntimeError(f"I don\'t know this type {message['msg_type']}")
    
    @InstanceExist(CarlaClient)
    def before_world_tick(self, timestamp):
        if len(self._carlanet_actors) == 0: return
        # Get the spectator from the world
        spectator = CarlaClient.instance.world.get_spectator()
        # Get the the vehicle
        key = next(iter(self._carlanet_actors))
        car: carla.Actor = self._carlanet_actors[key].carla_actor
        # Set the camera view on top of vehicle
        spectator.set_transform(carla.Transform(
            car.get_transform().location + carla.Location(z=20),
            carla.Rotation(pitch=-90))
        )

class agentManager(AgentManager):
    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        if not 'msg_type' in message: return SimulatorStatus.RUNNING, {'message': 'from carla'}
        if message['msg_type'] == 'LIGHT_UPDATE':
            curr_light_state = _str_to_light_control_enum(int(message['light_curr_state']))
            next_light_state = self.calc_next_light_state(curr_light_state)
            #print("LIGHT CURR STATE: ", curr_light_state, "LIGHT NEXT STATE: ", next_light_state, '\n')
            #print("LIGHT CURR STATE: ", _light_control_enum_to_str(curr_light_state), "LIGHT NEXT STATE: ", _light_control_enum_to_str(next_light_state), '\n')

            msg_to_send = {
                'msg_type': 'LIGHT_COMMAND',
                'light_next_state': f'{_light_control_enum_to_str(next_light_state)}'
            }

            return SimulatorStatus.RUNNING, msg_to_send
        else:
            raise RuntimeError(f"I don\'t know this type {message['msg_type']}")

    def calc_next_light_state(self, light_state: carla.VehicleLightState):
        if light_state == carla.VehicleLightState.Position:
            next_state = carla.VehicleLightState.Brake
        elif light_state == carla.VehicleLightState.Brake:
            next_state = carla.VehicleLightState.All
        elif light_state == carla.VehicleLightState.NONE:
            next_state = carla.VehicleLightState.Position
        else:
            next_state = carla.VehicleLightState.NONE
        return next_state
    
try: ActorType.destroy()
except: ...

try: SimulationManager.destroy()
except: ...

try: CarlaClient.destroy()
except: ...

try: SocketManager.destroy()
except: ...

#starting carla simulator (ps. can be started alone in in differrent way doesn't metter)
SimulationManager(carla_sh_path='/home/stefano/Documents/tesi/CARLA_0.9.15/CarlaUE4.sh')
SimulationManager.instance.reload_simulator()
time.sleep(5)

def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    SimulationManager.instance.close_simulator()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#redirect print on logfile for debug purposes
class TeeOutput:
    def __init__(self, filename):
        self.file = open(filename, 'a')
        self.stdout = sys.stdout
        
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
        
    def flush(self):
        self.file.flush()
        self.stdout.flush()
# Redirect stdout
sys.stdout = TeeOutput('logfile_2.txt')
# Use a partial function to preserve print's other arguments
print = partial(print, flush=True)

#minimal part for co-simulation
ActorType()
CarlaClient(host='localhost', port=2000)
SocketManager(
    listening_port=5555,
    worldManager=wManager(synchronousMode=True, renderingMode=True),
    actorManager=aManager(),
    agentManager=agentManager(),
    log_messages=True
)
SocketManager.instance.start_socket()