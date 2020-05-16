import ray
import traceback

from .config import MuZeroConfig
from .storage import SharedStorage, ReplayBuffer
from .selfplay import run_selfplay
from .train import train_network

# MuZero training is split into two independent parts: Network training and
# self-play data generation.
# These two parts only communicate by transferring the latest network checkpoint
# from the training to the self-play, and the finished games from the self-play
# to the training.
class Muzero(object):
    def __init__(self, config: MuZeroConfig):
        self.config = config
        self.storage = SharedStorage()
        self.replay_buffer = ReplayBuffer(config)
        
    def launch_job(self, f, *args):
    #   f(*args)
        f.remote(*args)
    
    def run(self):
        for _ in range(self.config.num_actors):
            self.launch_job(run_selfplay, self.config, self.storage, self.replay_buffer)
        self.launch_job(train_network, self.config, self.storage, self.replay_buffer)
#         best_network = self.storage.latest_network()