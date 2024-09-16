import os
import pickle
import pandas as pd
import numpy as np
from typing import Tuple, Union, List
from datetime import datetime
from sklearn.linear_model import LogisticRegression

class DelayModel:

    def __init__(self):
        self._model = None  # Model should be saved in this attribute.
        # Load the model if it exists
        if os.path.exists('model.pkl'):  # Verifica la ruta correcta aquí
            with open('model.pkl', 'rb') as f:
                self._model = pickle.load(f)
        else:
            self._model = None
    
    @staticmethod
    def get_period_day(date_str: str) -> str:
        date_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').time()
        if datetime.strptime("05:00", '%H:%M').time() <= date_time <= datetime.strptime("11:59", '%H:%M').time():
            return 'mañana'
        elif datetime.strptime("12:00", '%H:%M').time() <= date_time <= datetime.strptime("18:59", '%H:%M').time():
            return 'tarde'
        else:
            return 'noche'

    @staticmethod
    def is_high_season(date_str: str) -> int:
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        date_no_year = date.replace(year=2000)
        ranges = [
            (datetime(2000, 12, 15), datetime(2000, 12, 31)),
            (datetime(2000, 1, 1), datetime(2000, 3, 3)),
            (datetime(2000, 7, 15), datetime(2000, 7, 31)),
            (datetime(2000, 9, 11), datetime(2000, 9, 30))
        ]
        for start, end in ranges:
            if start <= date_no_year <= end:
                return 1
        return 0

    @staticmethod
    def get_min_diff(row: pd.Series) -> float:
        fecha_o = datetime.strptime(row['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(row['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = (fecha_o - fecha_i).total_seconds() / 60
        return min_diff
            
    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.Series], pd.DataFrame]:
        """
        Prepare raw data for training or prediction.
        """
        data = data.copy()

        # Generate date-related features only if 'Fecha-I' and 'Fecha-O' are present
        if 'Fecha-I' in data.columns and 'Fecha-O' in data.columns:
            data['period_day'] = data['Fecha-I'].apply(self.get_period_day)
            data['high_season'] = data['Fecha-I'].apply(self.is_high_season)
            data['min_diff'] = data.apply(self.get_min_diff, axis=1)
            data['delay'] = np.where(data['min_diff'] > 15, 1, 0)
        else:
            # If dates are missing, fill with default values or skip these features
            data['period_day'] = 'mañana'  # or another default value
            data['high_season'] = 0
            data['min_diff'] = 0
            data['delay'] = 0

        # Continue with the rest of the preprocessing
        # One-hot encode 'OPERA', 'TIPOVUELO', 'MES'
        features = pd.concat([
            pd.get_dummies(data['OPERA'], prefix='OPERA'),
            pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO'),
            pd.get_dummies(data['MES'], prefix='MES')
        ], axis=1)

        # Define the top 10 features
        top_10_features = [
            "OPERA_Latin American Wings",
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]

        # Ensure all top 10 features are in the DataFrame
        for feature in top_10_features:
            if feature not in features.columns:
                features[feature] = 0  # Add missing feature with zeros

        # Keep only the top 10 features
        features = features[top_10_features]

        if target_column:
            target = data[target_column]
            return features, target
        else:
            return features

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.Series
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): Preprocessed features.
            target (pd.Series): Target variable.
        """
        # Compute class weights to handle imbalance
        n_y0 = len(target[target == 0])
        n_y1 = len(target[target == 1])
        total = len(target)
        class_weight = {0: n_y1 / total, 1: n_y0 / total}

        # Initialize and train the Logistic Regression model
        self._model = LogisticRegression(class_weight=class_weight, max_iter=1000)
        self._model.fit(features, target)

        # Save the trained model to disk
        with open('model.pkl', 'wb') as f:
            pickle.dump(self._model, f)

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): Preprocessed features.

        Returns:
            List[int]: Predicted targets.
        """
        if self._model is None:
            raise Exception("Model not trained or loaded.")
        predictions = self._model.predict(features)
        return predictions.tolist()