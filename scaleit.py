import requests
import time

# Constants for the target CPU utilization and API endpoints
TARGET_CPU_UTILIZATION = 0.80
STATUS_URL = "http://localhost:5000/app/status"  # Update with correct base URL
REPLICAS_URL = "http://localhost:5000/app/replicas"  # Update with correct base URL

def get_status():
    """
    Retrieves the current app status from the API.
    Returns a dictionary with CPU usage and current replicas.
    """
    headers = {'Accept': 'application/json'}
    response = requests.get(STATUS_URL, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

def update_replicas(new_replica_count):
    """
    Sends a PUT request to update the replica count.
    """
    headers = {'Content-Type': 'application/json'}
    data = {"replicas": new_replica_count}
    response = requests.put(REPLICAS_URL, headers=headers, json=data)
    response.raise_for_status()  # Raise an error for bad responses

def calculate_desired_replicas(current_cpu, current_replicas):
    """
    Calculates the desired number of replicas based on the target CPU utilization.
    Uses the formula: desired_replicas = current_replicas * (current_cpu / target_cpu)
    """
    return max(1, int(current_replicas * (current_cpu / TARGET_CPU_UTILIZATION)))

def auto_scale():
    """
    Main function that continuously monitors and adjusts replica counts based on CPU usage.
    """
    try:
        while True:
            # Step 1: Get the current status
            status = get_status()
            current_cpu = status['cpu']['highPriority']
            current_replicas = status['replicas']

            # Step 2: Calculate the desired number of replicas
            desired_replicas = calculate_desired_replicas(current_cpu, current_replicas)

            # Step 3: Update replicas if there's a discrepancy
            if desired_replicas != current_replicas:
                print(f"Adjusting replicas from {current_replicas} to {desired_replicas}")
                update_replicas(desired_replicas)
            else:
                print("No adjustment needed.")

            # Wait before the next check
            time.sleep(30)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        print("Auto-scaling terminated by user.")

if __name__ == "__main__":
    auto_scale()
