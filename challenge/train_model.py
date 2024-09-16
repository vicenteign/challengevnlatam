import pandas as pd
from model import DelayModel

# Load the data
data = pd.read_csv('../data/data.csv', low_memory=False)

# Initialize the model
model = DelayModel()

# Preprocess the data
features, target = model.preprocess(data, target_column='delay')

# Fit the model
model.fit(features, target)

print("Model training completed and saved to 'model.pkl'.")