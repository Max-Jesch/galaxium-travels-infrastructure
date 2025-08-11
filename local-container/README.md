# Start all server applications

1. Insert followling commands

```sh
cd local-container
bash start-containers.sh
```

* Example output:

```sh
************************************
 Build and start containers with Docker compose 
- 'galaxium travels infrastructure'
************************************
Home path:    ../galaxium-travels-infrastructure/local-container
...
**************** BUILD ******************
WARN[0000] The "APP_USER" variable is not set. Defaulting to a blank string. 
...
 => => naming to docker.io/library/booking_system_rest:1.0.0                                                                 0.0s
 => [booking_system] resolving provenance for metadata file                                                                  0.0s
[+] Building 2/2
 ✔ booking_system  Built                                                                                                     0.0s 
 ✔ hr_database     Built                                                                                                     0.0s 
**************** START ******************
WARN[0000] The "APP_USER" variable is not set. Defaulting to a blank string. 
WARN[0000] The "APP_USER" variable is not set. Defaulting to a blank string. 
WARN[0000] /Users/thomassuedbroecker/Documents/tsuedbro/dev/learning-2024/galaxium-travels-infrastructure/local-container/docker_compose.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
[+] Running 2/2
 ✔ Container hr_database          Created                                                                                    0.0s 
 ✔ Container booking_system_rest  Created                                                                                    0.0s 
Attaching to booking_system_rest, hr_database
booking_system_rest  | /usr/local/lib/python3.11/site-packages/pydantic/_internal/_config.py:373: UserWarning: Valid config keys have changed in V2:
booking_system_rest  | * 'orm_mode' has been renamed to 'from_attributes'
booking_system_rest  |   warnings.warn(message, UserWarning)
booking_system_rest  | INFO:     Started server process [1]
booking_system_rest  | INFO:     Waiting for application startup.
booking_system_rest  | INFO:     Application startup complete.
booking_system_rest  | INFO:     Uvicorn running on http://0.0.0.0:8082 (Press CTRL+C to quit)
hr_database          | INFO:     Started server process [1]
hr_database          | INFO:     Waiting for application startup.
hr_database          | INFO:     Application startup complete.
hr_database          | INFO:     Uvicorn running on http://0.0.0.0:8081 (Press CTRL+C to quit)
booking_system_rest  | Database seeded with elaborate demo data!
booking_system_rest  | INFO:     172.18.0.1:43890 - "GET /docs HTTP/1.1" 200 OK
booking_system_rest  | INFO:     172.18.0.1:43890 - "GET /openapi.json HTTP/1.1" 200 OK
hr_database          | INFO:     172.18.0.1:44656 - "GET /docs HTTP/1.1" 200 OK
hr_database          | INFO:     172.18.0.1:44656 - "GET /openapi.json HTTP/1.1" 200 OK
Gracefully stopping... (press Ctrl+C again to force)
[+] Stopping 2/2
 ✔ Container hr_database          Stopped                                                                                    0.8s 
 ✔ Container booking_system_rest  Stopped  
```

The following image show the running server applications.

![](/images/run-containers-01.png)
