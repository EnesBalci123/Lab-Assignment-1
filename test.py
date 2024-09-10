# Test Cases
import unittest
from unittest.mock import patch, MagicMock

from Lab1 import BoardGameMechanicsAnalyzer


class TestBoardGameMechanicsAnalyzer(unittest.TestCase):
    """
    Test cases for BoardGameMechanicsAnalyzer class.
    """

    def setUp(self):
        """
        Set up any common elements or configurations needed for the tests.
        """
        self.dataset_path = r'C:\Users\Gebruiker\Desktop\bgg_dataset.csv'
        self.api_key = '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'
        self.analyzer = BoardGameMechanicsAnalyzer(self.dataset_path, self.api_key)

    def tearDown(self):
        """
        Clean up any resources or configurations after each test.
        """
        pass

    def test_successful_accuracy_check(self):
        """
        Test the accuracy check for a successful response from GPT-3.
        """
        # Mock the OpenAI API call to simulate a successful response
        with patch.object(self.analyzer, 'ask_gpt', MagicMock(return_value="Area-Impulse, Delayed Purchase, Dice Rolling")):
            # Test steps
            game_name = 'Star Wars: Rebellion'
            print("Mock check")
            accuracy = self.analyzer.check_gpt_mechanics_accuracy(game_name)
            print("Done")
            # Assertions
            self.assertEqual(accuracy, 0.375)

    def test_invalid_game_name(self):
        """
        Test the accuracy check for an invalid game name.
        """
        # Test steps
        game_name = 'InvalidGameName'
        accuracy = self.analyzer.check_gpt_mechanics_accuracy(game_name)

        # Assertions
        self.assertEqual(accuracy, 0.0)

    def test_missing_dataset_scenario(self):
        """
        Test the accuracy check for a missing dataset scenario.
        """
        # Simulate a scenario where the dataset is not available
        self.analyzer.dataset_path = 'nonexistent_path.csv'
        self.assertRaises(FileNotFoundError, self.analyzer.load_and_preprocess_dataset)

