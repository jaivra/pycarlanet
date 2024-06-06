import abc
import enum

class AgentManager(abc.ABC):
    #_agents = dict(int, ?actor)

    # INIT PHASE
    def omnet_init_completed(self, run_id, carla_configuration, user_defined):
        """
        After Omnet, WorldManager INIT
        :param run_id: id corresponding to the one in OMNeT++
        :param carla_configuration:
        :param user_defined:
        :return: current carla world, current simulator status
        """
        ...
    
    # RUN PHASE
    def before_world_tick(self, timestamp) -> None:
        """
        Method called before a world tick called by OMNeT++
        :param timestamp
        :return: current simulator status
        """
        ...