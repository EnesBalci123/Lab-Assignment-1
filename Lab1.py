"""
Module: board_game_analyzer

Description: This module contains the implementation of the BoardGameMechanicsAnalyzer class
and associated test cases.
"""

import time

import pandas as pd
from openai import OpenAI


class BoardGameMechanicsAnalyzer:
    """
    BoardGameMechanicsAnalyzer class analyzes board game mechanics using OpenAI's GPT-3.5
    """

    def __init__(self, dataset_path, api_key):
        self.dataset_path = dataset_path
        self.client = OpenAI(api_key=api_key)
        self.data = None  # Internal representation of the dataset
        # Load and preprocess the dataset
        self.load_and_preprocess_dataset()

    def ask_gpt(self, prompt):
        """
        Queries OpenAI GPT-3.5 with the given prompt and returns the response.
        """
        response = self.client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=2000
        )
        time.sleep(20)
        return response.choices[0].text.strip()

    def get_mechanics_for_game(self, game, year=None):
        """ Looks up mechanics in BGG dataset for given game and optional published year """
        if year is not None:
            data = self.data[(self.data['Name'] == game) & (self.data['Year Published'] == year)]['Mechanics']
        else:
            data = self.data[self.data['Name'] == game]['Mechanics']

        return data.iloc[0].split(", ") if len(data) > 0 else []

    def ask_mechanics(self, game):
        """ Returns which of the given mechanics associates with the given game """
        prompt = f"Give a comma separated list of mechanics ({', '.join(self.get_mechanics_for_game(game))}) that are actually associated with the game: {game}. If the game is invalid, return the word 'Nothing'"
        answer = self.ask_gpt(prompt).split(",")
        answer = [x.strip() for x in answer if x.strip() != "Nothing"]
        return answer

    def check_gpt_mechanics_accuracy(self, game):
        """
        Checks the accuracy of mechanics predicted by GPT-3 for the given game.
        """
        gpt_mechanics = self.ask_mechanics(game)
        bgg_mechanics = self.get_mechanics_for_game(game)
        print(game)
        print("gpt", gpt_mechanics)
        print("bgg", bgg_mechanics)
        if len(bgg_mechanics) == 0:
            return 0

        accuracy = len(gpt_mechanics) / len(bgg_mechanics)
        return accuracy

    def check_accuracy_for_games(self, game_list):
        """
        Checks the accuracy for a list of games.
        """
        results = []

        for game_name, year_published in game_list:
            accuracy = self.check_gpt_mechanics_accuracy(game_name)
            results.append((game_name, year_published, accuracy))

        return results

    def check_mechanics_for_games(self, game_list):
        """ Asks GPT mechanics for given list of games [(game_name, published_year)] """
        results = {}
        for game_name, year_published in game_list:
            print(game_name, year_published)
            results[(game_name, year_published)] = self.ask_mechanics(game_name)
            print(game_name, results[(game_name, year_published)])
            time.sleep(20)
        return results

    def load_and_preprocess_dataset(self):
        """
        Loads and preprocesses the dataset into a Pandas DataFrame.
        """
        try:
            self.data = pd.read_csv(self.dataset_path, delimiter=';')
            self.data.dropna(subset=['Name', 'Year Published', 'Mechanics'], inplace=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found at {self.dataset_path}")


def analyze_top_mechanics(board_analyzer: BoardGameMechanicsAnalyzer, games):
    gpt_mechanics_per_game = board_analyzer.check_mechanics_for_games(games)
    top_score = {}
    low_score = {}
    for game_name, published_year in games:
        bbg_mechanics = board_analyzer.get_mechanics_for_game(game_name, published_year)
        gpt_mechanics = gpt_mechanics_per_game[(game_name, published_year)]
        for mechanic in bbg_mechanics:
            if mechanic not in top_score or mechanic not in low_score:
                top_score[mechanic] = 0
                low_score[mechanic] = 0

        for mechanic in gpt_mechanics:
            if mechanic in top_score:
                top_score[mechanic] += 1
        for mechanic in bbg_mechanics:
            if mechanic not in gpt_mechanics:
                low_score[mechanic] += 1

    never_mentioned = [k for k, v in low_score.items() if top_score[k] == 0 and v > 0]

    print("Top 10 mechanics with highest accuracy:", dict(sorted(top_score.items(), key=lambda item: item[1], reverse=True)))
    print("Top 10 mechanics with lowest accuracy:", dict(sorted(low_score.items(), key=lambda item: item[1], reverse=True)))
    print("Mechanics that are never mentioned by GPT:", never_mentioned)


def analyze_mean_accuracy(board_analyzer: BoardGameMechanicsAnalyzer, games):
    accuracy_count = 0
    accuracy_sum = 0
    for game_name, published_year in games:
        accuracy_sum += board_analyzer.check_gpt_mechanics_accuracy(game_name)
        accuracy_count += 1
        print(f"GPT mean after {accuracy_count} games", accuracy_sum/accuracy_count)


if __name__ == '__main__':
    dataset_path = r'C:\Users\Gebruiker\Desktop\bgg_dataset.csv'  # Use a raw string
    api_key = ""
    analyzer = BoardGameMechanicsAnalyzer(dataset_path, api_key)
    n_games = [(x[0], int(x[1])) for x in analyzer.data[["Name", "Year Published"]].values.tolist()[:200]]
    analyze_mean_accuracy(analyzer, n_games)
