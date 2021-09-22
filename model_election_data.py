"""
Our statistical modeling
"""

#######################################################################################
# Load and wrangle the data
import pandas as pd

df = pd.read_csv('results/concatenate_all_election.csv')
df_wide = df.set_index(['election', 'Nuance', 'dept_canton']).unstack(level=0).unstack(level=0)
# Drop the columns where there is no data
df_wide = df_wide.dropna(axis=1, how='all')
df_wide = df_wide.droplevel(level=0, axis=1)

outcomes = df_wide['legislatives_2012']

print("Number of times a party did not present a candidate as the legislatives_2012")
print(outcomes.isna().sum())

outcomes = outcomes.fillna(value=0)

data = df_wide.drop('legislatives_2012', axis=1)

#######################################################################################
# Fit a model predicting the major parties
from sklearn.experimental import enable_hist_gradient_boosting  # noqa
from sklearn import model_selection, ensemble

model = ensemble.HistGradientBoostingRegressor()
cv = model_selection.ShuffleSplit(test_size=.2, n_splits=10)

prediction_scores = dict()

# Interesting outcomes
# FG = "Front de Gauche"
# EXG = "Extreme Gauche"
target_nuances = ['FN', 'SOC', 'UMP', 'FG', 'EXG']
for target_nuance in target_nuances:
    y = outcomes[target_nuance]

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


#######################################################################################
# Feature importance for various parties
from sklearn.inspection import permutation_importance
for target_nuance in target_nuances:
    y = outcomes[target_nuance]

    X_train, X_val, y_train, y_val = model_selection.train_test_split(data, y)
    model.fit(X_train, y_train)
    r = permutation_importance(model, X_val, y_val,
                            n_repeats=30,
                            random_state=0)

    importances = pd.DataFrame(r['importances'].T)
    importances.columns = data.columns

    avg_importance_per_party = importances.mean().unstack().fillna(value=0).mean()

    # To lighten up the plot, don't display parties for which the average
    # importance is below the median
    select_party = avg_importance_per_party > avg_importance_per_party.median()
    select_party = select_party[select_party].index

    importances = importances.unstack().rename('importance').reset_index().drop('level_2', axis=1)

    importances = importances.query('Nuance in @select_party')

    # Work on the name of the election to have better ordering
    elections = importances['election'].str.split('_')
    importances['election'] = elections.str[1].str.cat(elections.str[0], sep=' ')
    importances = importances.sort_values('election')

    plt.figure(figsize=(6, 12))
    seaborn.boxplot(data=importances, x='importance', y='Nuance', hue='election', orient='h',
                    fliersize=1)
    plt.title(f'Feature import ({target_nuance} prediction)')
    plt.savefig(f'results/feature_import_{target_nuance}.png',
                bbox_inches='tight', dpi=200)
