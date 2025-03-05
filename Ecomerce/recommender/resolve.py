"""
    To run the recommendation system
    1. Run data_processor.py
    2. Run resolve.py
    3. Enjoy
"""

from os import listdir
from os.path import isfile, join

from recommender import RecommendationSystem
ROOT = './processed_data'

if __name__ == '__main__':
    files = [f for f in listdir(ROOT) if isfile(join(ROOT, f))]
    for file in files:
        category = file.replace('.csv','')
        rcm = RecommendationSystem(category=category)
        rcm.initialize()