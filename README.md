# Introduction 
This is a preprocessing repo. 

# How It Works

1. Check the config for customer id, subsite id, location id or camera group id
2. Aggregate the camera group and get all the camera config and cache the data
3. Read camera configuration from cache
4. Start preprocessing for camera
5. Check for the update in cache and update the camera configurations

# Architecture
![Architectural Flow](preprocessing/images/preprocess.png)


1. Each topic are executed on process pool for the faster image fetch
2. Each task in process pool have threadpool, and each threadpool is running preprocessor once preprocessing is done, it will be send to the postprocessing api

# Dependency
1. This Module is dependent on the https://tatacommiot@dev.azure.com/tatacommiot/Video%20Based%20IoT/_git/vd-iot-dataapiservice
2. This module also needs kafka broker

# Installation
1. Install Python3.9 
2. Install redis-server
3. poetry install

# Run App
1. chmod +x run.sh
2 ./run.sh

# Docker 
1. Contenirization is enabled
2. change the config.yaml
3. Navigate to the Dockerfile level
4. build the container (sudo docker build -t "preprocess")
5. Run the container (sudo oocker run -t "preprocess")