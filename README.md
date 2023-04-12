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
