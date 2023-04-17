# California_housing


Build Docker Image
```
docker build -t <image_name>:<tag_name> .
```

To list Docker images
```
docker images
```

Run Docker Image
```
docker run -p 5000:5000 -e PORT=5000 <IMAGE ID>
```

To check running containers
```
docker ps
```

To stop Docker
```
docker stop <container_id>
```

To run setup.py
```
python setup.py install
```



Create 6 Components
1. Data Ingestion
2. Data Validation
3. Data Transformation
4. Model Trainer
5. Model Evaluation
6. Model Pusher


To have a progress bar while downloading a library
```
pip install --progress-bar=on <library>
```