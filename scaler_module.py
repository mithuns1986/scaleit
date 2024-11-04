import requests
import time

# Constants for the target CPU utilization and API endpoints
TARGET_CPU_UTILIZATION = 0.80
STATUS_URL = "http://localhost:8123/app/status"  # Update with correct base URL
REPLICAS_URL = "http://localhost:8123/app/replicas"  # Update with correct base URL

class ScalerAPI:
    def __init__(self, status_url, replicas_url):
        self.status_url = status_url
        self.replicas_url = replicas_url

    def get_status(self):
        """
        Retrieves the current app status from the API.
        Returns a dictionary with CPU usage and current replicas.
        """
        headers = {'Accept': 'application/json'}
        try:
            response = requests.get(self.status_url, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching status: {e}")
        except ValueError:
            print("Error parsing JSON response for status.")
        return None

    def update_replicas(self, new_replica_count):
        """
        Sends a PUT request to update the replica count.
        """
        headers = {'Content-Type': 'application/json'}
        data = {"replicas": new_replica_count}
        try:
            response = requests.put(self.replicas_url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            print(f"Replicas successfully updated to {new_replica_count}.")
        except requests.exceptions.RequestException as e:
            print(f"Error updating replicas: {e}")


class ReplicaScaler:
    def __init__(self, api_client, target_cpu):
        self.api_client = api_client
        self.target_cpu = target_cpu

    def calculate_desired_replicas(self, current_cpu, current_replicas):
        """
        Calculates the desired number of replicas based on the target CPU utilization.
        Uses the formula: desired_replicas = current_replicas * (current_cpu / target_cpu)
        """
        return max(1, int(current_replicas * (current_cpu / self.target_cpu)))

    def auto_scale(self):
        """
        Main function that continuously monitors and adjusts replica counts based on CPU usage.
        """
        try:
            while True:
                # Step 1: Get the current status
                status = self.api_client.get_status()
                if status is None:
                    print("Failed to retrieve status, retrying in 30 seconds.")
                    time.sleep(30)
                    continue
                
                try:
                    current_cpu = status['cpu']['highPriority']
                    current_replicas = status['replicas']
                except KeyError:
                    print("Unexpected response format in status, retrying in 30 seconds.")
                    time.sleep(30)
                    continue

                # Step 2: Calculate the desired number of replicas
                desired_replicas = self.calculate_desired_replicas(current_cpu, current_replicas)

                # Step 3: Update replicas if there's a discrepancy
                if desired_replicas != current_replicas:
                    print(f"Adjusting replicas from {current_replicas} to {desired_replicas}")
                    self.api_client.update_replicas(desired_replicas)
                else:
                    print("No adjustment needed.")

                # Wait before the next check
                time.sleep(30)

        except KeyboardInterrupt:
            print("Auto-scaling terminated by user.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


# Instantiate classes and start auto-scaling
if __name__ == "__main__":
    api_client = ScalerAPI(STATUS_URL, REPLICAS_URL)
    scaler = ReplicaScaler(api_client, TARGET_CPU_UTILIZATION)
    scaler.auto_scale()
