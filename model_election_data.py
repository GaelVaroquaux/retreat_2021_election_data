"""
Our statistical modeling
"""

import pandas as pd

df = pd.read_csv('results/concatenate_all_election.csv')
df_wide = df.set_index(['election', 'Nuance', 'dept_canton']).unstack(level=0).unstack(level=0)
# Drop the columns where there is no data
df_wide = df_wide.dropna(axis=1, how='all')
df_wide = df_wide.droplevel(level=0, axis=1)

outcomes = df_wide['legislatives_2012']

print("Number of times a party did not present a candidate as the legislatives_2012")
print(outcomes.isna().sum())

data = df_wide.drop('legislatives_2012', axis=1)

from sklearn.experimental import enable_hist_gradient_boosting  # noqa
from sklearn import model_selection, ensemble

model = ensemble.HistGradientBoostingRegressor()
cv = model_selection.ShuffleSplit(test_size=.2, n_splits=10)

prediction_scores = dict()

# Interesting outcomes
# FG = "Front de Gauche"
# EXG = "Extreme Gauche"
for target_nuance in ['FN', 'SOC', 'UMP', 'FG', 'EXG']:
    y = outcomes[target_nuance]
    y = y.fillna(value=0)

    prediction_scores[target_nuance] = model_selection.cross_val_score(model, data, y, cv=cv)

prediction_scores = pd.DataFrame(prediction_scores).unstack().reset_index().drop('level_1', axis=1)
prediction_scores = prediction_scores.rename({0: 'prediction score',
                                             'level_0': 'Nuance'}, axis=1)

import seaborn
from matplotlib import pyplot as plt

plt.figure(figsize=(4, 4))
seaborn.boxplot(data=prediction_scores, x='prediction score', y='Nuance', orient='h')
plt.xlabel('Prediction score (r2)')
plt.savefig('results/prediction_scores_per_party.png',
            bbox_inches='tight', dpi=200)

