# PJH: Dockerfile Guide 


```bash
# make sure you are in Backend/
sudo docker compose up --build
# this will run a shell that can be interacted with

# in another window, while the docker exec is running:
sudo docker compose exec robot /bin/bash
# this will put you in the shell
```

## Notes on the docker setup:
 - everything in `src/` is a live-editable volume `chess/`
 - the `shared/` library is also forwarded to allow viewing of the IPC `.json` files from the host machine
 - Future work: maybe have a web UI to view 
