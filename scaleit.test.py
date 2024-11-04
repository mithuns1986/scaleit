import unittest
from unittest.mock import patch, Mock
from scaler_module import ScalerAPI, ReplicaScaler  # Assume your code is saved in scaler_module.py

class TestScalerAPI(unittest.TestCase):
    @patch('requests.get')
    def test_get_status_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cpu": {"highPriority": 0.68},
            "replicas": 10
        }
        mock_get.return_value = mock_response

        api = ScalerAPI(STATUS_URL, REPLICAS_URL)
        result = api.get_status()
        self.assertIsNotNone(result)
        self.assertEqual(result["cpu"]["highPriority"], 0.68)
        self.assertEqual(result["replicas"], 10)

    @patch('requests.get')
    def test_get_status_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API failure")

        api = ScalerAPI(STATUS_URL, REPLICAS_URL)
        result = api.get_status()
        self.assertIsNone(result)

    @patch('requests.put')
    def test_update_replicas_success(self, mock_put):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        api = ScalerAPI(STATUS_URL, REPLICAS_URL)
        api.update_replicas(12)
        mock_put.assert_called_once_with(REPLICAS_URL, headers={'Content-Type': 'application/json'}, json={"replicas": 12}, timeout=5)

    @patch('requests.put')
    def test_update_replicas_failure(self, mock_put):
        mock_put.side_effect = requests.exceptions.RequestException("API failure")

        api = ScalerAPI(STATUS_URL, REPLICAS_URL)
        api.update_replicas(12)
        mock_put.assert_called_once()

class TestReplicaScaler(unittest.TestCase):
    def setUp(self):
        self.api_client = Mock()
        self.scaler = ReplicaScaler(self.api_client, TARGET_CPU_UTILIZATION)

    def test_calculate_desired_replicas(self):
        current_cpu = 0.68
        current_replicas = 10
        desired_replicas = self.scaler.calculate_desired_replicas(current_cpu, current_replicas)
        self.assertEqual(desired_replicas, 8)

    @patch.object(ReplicaScaler, 'calculate_desired_replicas')
    def test_auto_scale_adjustment(self, mock_calculate_desired_replicas):
        self.api_client.get_status.return_value = {
            "cpu": {"highPriority": 0.85},
            "replicas": 10
        }
        mock_calculate_desired_replicas.return_value = 11
        self.scaler.auto_scale()
        
        self.api_client.update_replicas.assert_called_with(11)

    @patch.object(ReplicaScaler, 'calculate_desired_replicas')
    def test_auto_scale_no_adjustment(self, mock_calculate_desired_replicas):
        self.api_client.get_status.return_value = {
            "cpu": {"highPriority": 0.8},
            "replicas": 10
        }
        mock_calculate_desired_replicas.return_value = 10
        self.scaler.auto_scale()
        
        self.api_client.update_replicas.assert_not_called()

if __name__ == "__main__":
    unittest.main()
