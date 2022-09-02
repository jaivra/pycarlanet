import abc
import enum

from CarlaInetActor import CarlaInetActor

"""
Listener for OMNeT world, note, every parameters gave as in input is a String, so eventually you need to use cast
"""


class SimulatorStatus(enum.Enum):
    RUNNING = 0
    FINISHED_OK = 1
    FINISHED_ERROR = -1


class OMNeTWorldListener(abc.ABC):

    def on_static_actor_created(self, actor_id: str, actor_type: str, actor_config) -> CarlaInetActor:
        """
        Callback called at the beginning of the simulation, OMNeT says which actors it has and communicate
        with carla to create these actors in the world
        :param actor_id:
        :param actor_type:
        :param actor_config:
        :return: new actor created from carlaWorld
        """
        ...
        ##return Actor

    def on_finished_creation_omnet_world(self, run_id, seed, carla_timestep, custom_params) -> (float, SimulatorStatus):
        """
        :param run_id:
        :param seed:
        :param carla_timestep:
        :param custom_params:
        :return: current carla world timestamp (see Snapshot class of CarlaAPI), current simulator status
        """
        ...

    def on_carla_simulation_step(self, timestamp) -> SimulatorStatus:
        """
        Method called every times OMNeT call simulation_step of Carla
        :param timestamp
        :return: current simulator status
        """
        ...

    def on_generic_message(self, timestamp, user_defined_message) -> (SimulatorStatus, dict):
        """
        :param timestamp:
        :param user_defined_message:
        :return: (current simulator status, dict contained custom parameters)
        """
        ...
