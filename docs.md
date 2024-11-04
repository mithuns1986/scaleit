Here's the complete README.md file with all the details consolidated for easy copying:

markdown
Copy code
# Auto-Scaler Application

This application is designed to automatically adjust the number of replicas of a service based on its current CPU utilization. It continuously monitors the service’s CPU usage and adjusts the replica count to keep the CPU utilization at or near a target value.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Classes and Methods](#classes-and-methods)
- [Error Handling](#error-handling)
- [Stopping the Application](#stopping-the-application)
- [Notes](#notes)

## Requirements
- Python 3.6+
- Internet connection (for accessing the REST API)
- API endpoints configured in `STATUS_URL` and `REPLICAS_URL` (see configuration in the code)

## Installation
1. Clone the repository or copy the code into your local environment.
2. Install required libraries (if not already installed):
   ```bash
   pip install requests
Usage
Update the API endpoint URLs in the code to point to your service’s status and replica endpoints. Ensure the port is set to 8123:
python
Copy code
STATUS_URL = "http://localhost:8123/app/status"  # Updated port to 8123
REPLICAS_URL = "http://localhost:8123/app/replicas"  # Updated port to 8123
Run the script using Python:
bash
Copy code
python main.py
The application will now start and continuously check the CPU utilization and adjust replicas every 30 seconds.
Classes and Methods
This application consists of two main classes: ScalerAPI and ReplicaScaler.

ScalerAPI
ScalerAPI is responsible for interacting with the REST API endpoints for fetching the current CPU status and updating the replica count.

__init__(self, status_url, replicas_url)
Initializes the ScalerAPI with the specified status_url and replicas_url.

get_status(self)
Fetches the current CPU status and replica count from the /status API endpoint.

Returns: A dictionary containing cpu and replicas data, or None if the request fails.
Error Handling: Prints an error message if the request fails due to a connection issue or if the response format is invalid.
update_replicas(self, new_replica_count)
Sends a PUT request to update the replica count at the /replicas API endpoint.

Parameters: new_replica_count - the desired replica count (integer).
Error Handling: Prints an error message if the request fails due to a connection issue.
ReplicaScaler
ReplicaScaler contains the scaling logic that calculates and applies the desired replica count based on current CPU utilization and a target CPU utilization value.

__init__(self, api_client, target_cpu)
Initializes the ReplicaScaler with an api_client (an instance of ScalerAPI) and a target_cpu value.

calculate_desired_replicas(self, current_cpu, current_replicas)
Calculates the desired replica count based on the formula:

desired_replicas
=
current_replicas
×
current_cpu
target_cpu
desired_replicas=current_replicas× 
target_cpu
current_cpu
​
 
Parameters:
current_cpu: The current CPU utilization (float).
current_replicas: The current number of replicas (integer).
Returns: The desired number of replicas, ensuring a minimum of 1 replica.
auto_scale(self)
Main function that continuously checks and adjusts the replica count every 30 seconds.

Steps:
Retrieves the current CPU utilization and replica count using get_status.
Calculates the desired number of replicas based on the target CPU utilization.
Updates the replica count if the calculated value differs from the current count.
Loop: Runs indefinitely until stopped manually. Each iteration has a 30-second delay to avoid excessive API calls.
Error Handling: If an API request fails, the application logs an error message and waits 30 seconds before retrying.
Exit: Can be exited gracefully by pressing Ctrl+C (KeyboardInterrupt), which will terminate the loop.
Error Handling
The application includes error handling for:

Connection Errors: If there’s an issue connecting to the API endpoints (e.g., network issues, endpoint down), the error is logged, and the application retries after 30 seconds.
Invalid Response Formats: If the response from the /status API doesn’t include the expected keys (cpu and replicas), it logs a message and retries after 30 seconds.
Unexpected Errors: Any unexpected exceptions during runtime are caught, logged, and the loop continues.
Stopping the Application
To stop the application, press Ctrl+C in the terminal. This will trigger a KeyboardInterrupt, which the application catches to stop gracefully, logging "Auto-scaling terminated by user."

Notes
The STATUS_URL and REPLICAS_URL endpoints should be configured according to your server environment, with the port set to 8123 in both URLs.
The target CPU utilization (TARGET_CPU_UTILIZATION) is set to 0.80 (80%) by default. You can adjust this value to fit your scaling requirements.
