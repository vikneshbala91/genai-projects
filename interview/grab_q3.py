import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class AnalysisDataAndFitLinearRegression:

    def __init__(self):
        self.version = 1

    def analyse_and_fit_lrm(self, path):
        # a path to a dataset is "./data/realest.csv"
        # dataset can be loaded by uncommenting the line bellow
        data = pd.read_csv(path)

        # logic for statistics
        filtered_df_for_statistics = data[(data['Bathroom'] == 2) & (data['Bedroom'] == 4)]['Tax']

        statistics = [
            filtered_df_for_statistics.mean(),
            filtered_df_for_statistics.std(),
            filtered_df_for_statistics.median(),
            filtered_df_for_statistics.min(),
            filtered_df_for_statistics.max()
        ]

        # logic for data_frame
        data_frame = data[data['Space'] > 800].sort_values(by='Price', ascending=False)

        # logic for number_of_observations
        pct_80 = data['Lot'].quantile(0.8)
        number_of_observations = (data['Lot'] >= pct_80).sum()

        # summary_dict
        summary_dict = {
            'statistics': statistics,
            'data_frame': data_frame,
            'number_of_observations': number_of_observations
        }

        # using already provided function to remove na values 
        cleaned_data = self.__listwise_deletion(data)

        # Prepare features (X) and target (y)
        X = cleaned_data[['Bedroom', 'Space', 'Room', 'Lot', 'Tax', 'Bathroom', 'Garage', 'Condition']]
        y = cleaned_data['Price']

        # Fit the model
        model = LinearRegression()
        model.fit(X, y)

        # logic for model_parameters
        model_parameters = {
            'Intercept': model.intercept_,
            'Bedroom': model.coef_[0],
            'Space': model.coef_[1],
            'Room': model.coef_[2],
            'Lot': model.coef_[3],
            'Tax': model.coef_[4],
            'Bathroom': model.coef_[5],
            'Garage': model.coef_[6],
            'Condition': model.coef_[7]
        }

        # Predicting price for the given parameters
        input_data = np.array([[3, 1500, 8, 40, 1000, 2, 1, 0]])
        price_prediction = model.predict(input_data)[0]

        # regression_dict
        regression_dict = {
            'model_parameters': model_parameters,
            'price_prediction': price_prediction
        }

        return {
            'summary_dict': summary_dict,
            'regression_dict': regression_dict
        }

    def __listwise_deletion(self, data: pd.DataFrame):
        return data.dropna()

if __name__ == "__main__":
    abc = AnalysisDataAndFitLinearRegression()
    abc.analyse_and_fit_lrm(path='data/realest.csv')
    print('completed !!')