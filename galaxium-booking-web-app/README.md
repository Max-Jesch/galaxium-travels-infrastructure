# Galaxium Booking System

This is a simple web application for booking flights using the Galaxium Travels Booking API.

This simple web application provides a user-friendly interface for booking flights, viewing available flights, and managing user bookings. The application is containerized using Docker, making it easy to deploy and run in any environment that supports Docker.

![](/images/run-containers-02.gif)

### 1. Project Structure

This is the web application project structure. We'll use a simple structure with the following directories and files:

```sh
galaxium-booking-web-app/
├── app.py
├── Dockerfile
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/
    ├── base.html
    ├── index.html
    ├── flights.html
    ├── bookings.html
    ├── register.html
    └── book_flight.html
```

## 2. Prerequisites

- Docker

## 3. Running the Application locally

1. Navigate to the application folder:
   ```sh
   cd galaxium-booking-web-app
   ```

2. Configure the `BACKEND_URL` in the `.env` file.
   Insert your Code Engine `BACKEND_URL`.
   
   Enable the needed environment by uncomment the BACKEND_URL.

   ```sh
   cat .env-template > .env
   ```

3. Build the Docker image:
   ```sh
   docker build -t galaxium-booking-web-app .
   ```

4. Run the Docker container:
   ```sh
   source .env
   docker run -p 8083:8083 galaxium-booking-web-app -e BACKEND_URL=${BACKEND_URL}
   ```

5. Open your browser and navigate to `http://localhost:8083` to access the application.

## 4. Deploy to IBM Code Engine

![](/images/run-containers-on-code-engine-01.png)

1. Install Jupyter

```sh
python3 -m venv .venv
source ./.venv/bin/activate
pip install jupyter
pip install dotenv
```

2. Start Jupyter Notebook

```sh
jupyter notebook
```

3. Start the `deployment_web_application_server.ipynb` Notebook and follow the steps inside the Notebook

```sh
deployment_web_application_server.ipynb
```