"""
DONE:
- To implement the adjusted cosine similarity
- To implement similarities pre-calculation
- To implement the rating prediction based on similarities
- To implement the recommendation system

TODO:
- To refactor
- To optimize
"""
import os 

import pandas as pd
import numpy as np
from tqdm import tqdm


ROOT = 'Ecommerce-website/recommender'

class RecommendationSystem(object):
    def __init__(self, category=None):
        self.rating_data = None
        self.rating_matrix = None
        self.similarities_matrix = None
        self.min_rating_counts = 1
        self.senior_users = None
        self.item_lists = None
        self.category = category

    def read_csv(self, file):
        """Read the rating data from csv

        Args:
            file (.csv): The file
        """
        self.rating_data = pd.read_csv(file)

    def matrix_construction(self):
        """Generate the rating matrix

        Returns:
            pd.DataFrame: Rating matrix
        """
        # Create a pivot table
        pivot_table = pd.pivot_table(self.rating_data, values='rating', index='customer_id', columns='product_id')
        # Only retain users that voted for at least 10 items
        pivot_table['cnt'] = pivot_table.count(axis=1)
        self.senior_users = pivot_table[pivot_table['cnt'] >= self.min_rating_counts].index.to_list()
        self.item_lists = pivot_table.drop(columns=['cnt']).columns.to_list()
        pivot_table = pivot_table[pivot_table['cnt'] >= self.min_rating_counts].drop(columns=['cnt'])
        pivot_table = pivot_table.fillna(0)
        self.rating_matrix = pivot_table
        return pivot_table

    def high_rating(self):
        """A list of the highest rating items

        Returns:
            List: The list
        """
        sum = self.rating_matrix.sum()
        count = (self.rating_matrix > 0).astype(float).sum(axis=0)
        rating = (sum / count).fillna(0).sort_values(ascending=False)
        return rating.head(10).index.to_list()

    def adjusted_cosine(self, item_i, item_j):
        """Calculate the adjusted cosine between items

        Args:
            item_i (int): The item's index 
            item_j (int): The item's index

        Returns:
            double: The adjusted cosine similarity
        """
        rated_users = self.rating_matrix[
            (self.rating_matrix.iloc[:, item_i] > 0) & (self.rating_matrix.iloc[:, item_j] > 0)]
        numerator = 0
        denominator = 0
        sum_1 = 0
        sum_2 = 0
        for user in rated_users.index:
            user_index = self.senior_users.index(user)
            mean_user_u = self.rating_matrix.iloc[user_index].mean()
            r_ui = self.rating_matrix.iloc[user_index, item_i]
            r_uj = self.rating_matrix.iloc[user_index, item_j]
            numerator += ((r_ui - mean_user_u) * (r_uj - mean_user_u))
            sum_1 += (r_ui - mean_user_u) ** 2
            sum_2 += (r_uj - mean_user_u) ** 2

        denominator = np.sqrt(sum_1) * np.sqrt(sum_2)
        if denominator == 0:
            return 0

        return numerator / denominator

    def similarities(self):
        """Generate the similarities matrix

        Returns:
            pd.DataFrame: The similarities matrix
        """
        if self.similarities_matrix:
            return self.similarities_matrix
        
        target = f'recommender/similarities_matrices/{self.category}.csv'
        if os.path.exists(target):
            matrix = pd.read_csv(target)
            self.similarities_matrix = matrix
            return matrix 
        
        n_items = len(self.rating_matrix.columns)
        matrix = np.zeros((n_items, n_items))
        for item_i in tqdm(range(n_items)):
            for item_j in range(n_items):
                matrix[item_i, item_j] = self.adjusted_cosine(item_i, item_j)
        pd.DataFrame(matrix).to_csv(target, index=False)
        self.similarities_matrix = pd.DataFrame(matrix)
        return matrix
    
    def initialize(self):
        target = f'recommender/processed_data/{self.category}.csv'
        self.read_csv(target)
        self.matrix_construction()
        self.similarities()

    def most_similar(self, iid):
        item_i = self.item_lists.index(iid)
        most_similar = self.similarities_matrix.iloc[item_i].sort_values(ascending=False)
        item_indexes =  most_similar.index.astype(int).to_list()[1:15]
        return [self.item_lists[index] for index in item_indexes]

    def predict(self, uid, item_i):
        """Predict the rating of a user for an item

        Args:
            uid (int): The user's id 
            item_i (int): The item's index in the item list. Shall be fix later

        Returns:
            double: The predicted rating
        """
        if uid not in self.senior_users:
            return None
        user_u = self.senior_users.index(uid)
        user_rating = self.rating_matrix.iloc[user_u].to_list()
        numerator = 0
        denominator = 0
        for item_id in range(len(self.item_lists)):
            if user_rating[item_id] == 0.:
                continue
            numerator += abs(self.similarities_matrix.iloc[item_id, item_i] * user_rating[item_id])
            denominator += abs(self.similarities_matrix.iloc[item_id, item_i])
        if denominator == 0:
            return 0
        return numerator / denominator

    def recommend(self, uid):
        """ Recommend items for a user 

        Args:
            uid (int): user's id

        Returns:
            list: A list of recommended items
        """
        if uid not in self.senior_users:
            return self.high_rating()
        user_u = self.senior_users.index(uid)
        recommend = []
        n_items = len(self.rating_matrix.columns)
        for item_i in range(n_items):
            if self.rating_matrix.iloc[user_u, item_i] == 0:
                recommend.append((self.predict(uid, item_i), item_i))
        recommend.sort(reverse=True)
        recommend = recommend[1:11]
        return [self.item_lists[rcm[1]] for rcm in recommend]


if __name__ == '__main__':
    category = 'bach_hoa_online'
    rcm = RecommendationSystem(category=category)
    rcm.initialize()
    print(rcm.most_similar(15973974))

