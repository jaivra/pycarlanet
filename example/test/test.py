import carla
import time

from carla.libcarla import World

import inspect

from pycarlanet.enum import CarlaMaplayers, SimulatorStatus
from pycarlanet.listeners import WorldManager, ActorManager, AgentManager
from pycarlanet import ActorType, CarlanetActor, CarlaClient, SimulationManager, SocketManager
from pycarlanet.utils import InstanceExist


#mock world manager
class wManager(WorldManager):
    timestamp = 4.0
    def omnet_init_completed(self, message) -> SimulatorStatus:
        #super().omnet_init_completed(message=message)
        #super().load_world("Town05_opt", [CarlaMaplayers.Buildings, CarlaMaplayers.Foliage])
        return SimulatorStatus.RUNNING

    def after_world_tick(self, timestamp) -> SimulatorStatus:
        if timestamp > 20:
           return SimulatorStatus.FINISHED_OK
        else:
            return SimulatorStatus.RUNNING

    #mock for testing purpose
    def get_elapsed_seconds(self): return self.timestamp
    
    #mock for testing purpose
    def tick(self): self.timestamp += 0.1
    
    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        return SimulatorStatus.RUNNING, {"message": "from carla"}



class aManager(ActorManager):
    p1 = 10.0
    p2 = 12.0
    v = 0.1
    r = 0.1

    def omnet_init_completed(self, message):
        print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name} -> start")
        super().omnet_init_completed(message)
        print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name} -> end")
        print(f"ActorType from aManager {ActorType.instance.get_available_types()}")

    def create_actors_from_omnet(self, actors):
        print("create_actors_from_omnet")
        print(actors)
    
    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        return SimulatorStatus.RUNNING, {"message": "from carla"}
    
    def _generate_carla_nodes_positions(self):
      self.p1 += 1
      self.p2 += 1
      return [
        {
          "actor_id": "1",
          "position": [
            self.p1,
            200.0,
            0
          ],
          "velocity": [
            self.v,
            self.v,
            self.v
          ],
          "rotation": [
            self.r,
            self.r,
            self.r
          ],
          "type": "Vehicle"
        },
        {
          "actor_id": "2",
          "position": [
            self.p2,
            250.0,
            0
          ],
          "velocity": [
            self.v,
            self.v,
            self.v
          ],
          "rotation": [
            self.r,
            self.r,
            self.r
          ],
          "type": "Vehicle"
        }
      ]
    
try: ActorType.destroy()
except: ...

try: SimulationManager.destroy()
except: ...

try: CarlaClient.destroy()
except: ...

try: SocketManager.destroy()
except: ...

#SimulationManager(carla_sh_path='/home/stefano/Documents/tesi/CARLA_0.9.15/CarlaUE4.sh')
#SimulationManager.instance.reload_simulator()
#time.sleep(5)
ActorType()
#CarlaClient(host='localhost', port=2000)

SocketManager(
    listening_port=5555,
    worldManager=wManager(synchronousMode=True, renderingMode=False),
    actorManager=aManager(),
    log_messages=True
)
#SocketManager(listening_port=5555, worldManager=wManager(synchronousMode=True, renderingMode=False), log_messages=True)


SocketManager.instance.start_socket()
