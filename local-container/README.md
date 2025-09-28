# Start all server applications

* Simplified Architecture local containers in compose

![](/images/run-containers-03.png)

1. Insert followling commands

```sh
cd local-container
bash start-containers.sh
```

* Example output:

```sh
...
[+] Running 3/3
 ✔ Container web_app              Created                                                                  0.0s 
 ✔ Container booking_system_rest  Created                                                                  0.0s 
 ✔ Container hr_database          Created                                                                  0.0s 
Attaching to booking_system_rest, hr_database, web_app
web_app              |  * Serving Flask app 'app'
web_app              |  * Debug mode: on
web_app              | WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
web_app              |  * Running on all addresses (0.0.0.0)
web_app              |  * Running on http://127.0.0.1:8083
web_app              |  * Running on http://172.18.0.2:8083
web_app              | Press CTRL+C to quit
web_app              |  * Restarting with stat
web_app              |  * Debugger is active!
web_app              |  * Debugger PIN: 626-306-471
booking_system_rest  | INFO:     Started server process [1]
booking_system_rest  | INFO:     Waiting for application startup.
booking_system_rest  | INFO:     Application startup complete.
booking_system_rest  | INFO:     Uvicorn running on http://0.0.0.0:8082 (Press CTRL+C to quit)
hr_database          | INFO:     Started server process [1]
hr_database          | INFO:     Waiting for application startup.
hr_database          | INFO:     Application startup complete.
hr_database          | INFO:     Uvicorn running on http://0.0.0.0:8081 (Press CTRL+C to quit)
...
```

The following image show the running server applications.

![](/images/run-containers-01.png)

* Simplified Architecture on Code Engine

![](/images/run-containers-on-code-engine-01.png)
