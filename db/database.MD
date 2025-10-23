## Steps to dockerize db

```
docker compose up -d
docker exec -it image_detection_db mysql -u root -p

SHOW DATABASES;
USE image_detection;
SHOW TABLES;
```
