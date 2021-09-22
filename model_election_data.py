
import pandas as pd
from sklearn.experimental import enable_hist_gradient_boosting  # noqa
from sklearn import model_selection, ensemble

df = pd.read_csv('results/concatenate_all_election.csv')
dd = df.set_index(['election', 'Nuance', 'dept_canton'])

