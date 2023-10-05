"""
Code to start PreProcessing and Cosnumers
"""
import os
from shared_memory_dict import SharedMemoryDict
from src.consumerpool import PoolConsumer
from src.parser import Config
from sourcelogs.logger import create_rotating_log


os.environ["SHARED_MEMORY_USE_LOCK"] = "1"

preprocess_smd = SharedMemoryDict(name="preprocess", size=10000000)
postprocess_smd = SharedMemoryDict(name='postprocess', size=10000000)
boundary_smd = SharedMemoryDict(name='boundary', size=10000000)
if __name__ == "__main__":
    try:
        preprocess_smd.shm.close()
        preprocess_smd.shm.unlink()
        postprocess_smd.shm.close()
        postprocess_smd.shm.unlink()
        boundary_smd.shm.close()
        boundary_smd.shm.unlink()
        del preprocess_smd
        del postprocess_smd
        del boundary_smd
        data = Config.yamlconfig("config/config.yaml")
        # print(data[0]["kafka"])
        logg = create_rotating_log("logs/logs.log")
        cg = PoolConsumer(data[0]["kafka"], logg)
        cg.checkState()
    except KeyboardInterrupt:
        print("=====Removing Shared Memory Refrence=====")
        preprocess_smd.shm.close()
        preprocess_smd.shm.unlink()
        postprocess_smd.shm.close()
        postprocess_smd.shm.unlink()
        boundary_smd.shm.close()
        boundary_smd.shm.unlink()
        del preprocess_smd
        del postprocess_smd
        del boundary_smd
