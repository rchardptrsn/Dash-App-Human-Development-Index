sudo kill -9 `sudo lsof -t -i:80`
docker system prune -f
docker container rm hdiapp
docker build --tag hdiapp .
docker run --name hdiapp -p 80:80 hdiapp