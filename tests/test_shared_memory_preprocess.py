from shared_memory_dict import SharedMemoryDict
import os
os.environ["SHARED_MEMORY_USE_LOCK"] = "1"

preprocess_smd = SharedMemoryDict(name="preprocess", size=10000000)
print(preprocess_smd)