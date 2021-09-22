import pandas as pd
import re
import seaborn
import matplotlib.pyplot as plt
import numpy as np

table_corres = pd.read_excel('data/Tableau_de_correspondance_communes_cantons_circonscriptions_2012.xls', header=1)
dpt = table_corres['Code département'].astype(str)
canton = table_corres['Code canton'].astype(str)
table_corres['dept_canton'] = dpt.str.cat(canton, sep='_')
table_corres = table_corres.drop_duplicates(subset=['dept_canton', 'Nom commune'], keep='first')

file_cols = {'cantonales_2011': [7, ['Sexe', 'Nom', 'Prénom', 'Nuance', 'Voix',
                                     '% Voix/Ins', '% Voix/Exp']],
             'cantonales_2008': [0, ['Sexe', 'Nom', 'Prénom', 'Nuance', 'Voix',
                                     '% Voix/Ins', '% Voix/Exp']],
             'europeennes_2009': [4, ['N°Liste', 'Nuance Liste',
                                      'Libellé Abrégé Liste',
                                      'Nom Tête de Liste', 'Voix',
                                      '% Voix/Ins', '% Voix/Exp']],
             'legislatives_2012': [7, ['Code Nuance', 'Voix', '% Voix/Ins',
                                       '% Voix/Exp']],
             'municipales_2008': [0, ['Code Nuance', 'Sexe', 'Nom', 'Prénom',
                                      'Liste', 'Sieges', 'Voix', '% Voix/Ins',
                                      '% Voix/Exp']],
             'regionales_2010': [0, ['Nuance Liste', 'Libellé Abrégé Liste',
                                     'Libellé Etendu Liste', 'Voix',
                                     '% Voix/Ins', '% Voix/Exp']]}

election_results = dict()
nuance_results = dict()
for filename, characteristics in file_cols.items():
    df = pd.read_excel('data/{}.xls'.format(filename),
                       sheet_name=characteristics[0])
    unnamed_cols = [c for c in df.columns if 'Unnamed' in c]
    tmp_max_num_candidate = len([c for c in df.columns
                                 if c.startswith('% Voix/Exp.')])
    if len(unnamed_cols):
        new_unnamed_colnames = ['{}.{}'.format(c, i) for i in
                                range(tmp_max_num_candidate + 1,
                                      tmp_max_num_candidate +
                                      int(len(unnamed_cols) /
                                          len(characteristics[1])) + 1)
                                for c in characteristics[1]]
        new_colnames = [c for c in df.columns if 'Unnamed' not in c] + \
            new_unnamed_colnames
        df.columns = new_colnames

    df = df.rename({c: '{}.0'.format(c) for c in characteristics[1]}, axis=1)
    max_num_candidate = len([c for c in df.columns
                             if c.startswith('% Voix/Exp.')])
    df.columns = pd.MultiIndex.from_tuples([
                (c.split('.')[::-1] if ('.' in c) else ('general', c))
                for c in df.columns
            ])

    # Unstack: go from wide to long
    df_long = df[
        ['%i' % i for i in range(max_num_candidate)]].unstack()\
        .unstack(level=1)
    # Work on the index
    df_long = df_long.reset_index()
    df_long = df_long.rename({
                        'level_0': 'Candidate number',
                        'level_1': 'index',
                        }, axis=1)

    df_long = pd.merge(left=df['general'],
                       right=df_long,
                       right_on='index',
                       left_index=True)
    # rename columns
    df_long.columns = [re.sub(".*Nuance.*", "Nuance", c) for c in
                       df_long.columns]
    if filename == 'municipales_2008':
        df_long = df_long.assign(new_code_commune=df_long['Code de la commune'].replace({r'0*([1-9][0-9]*)[A-Z]+.*': r'\1'}, regex=True).astype(int))
        df_long = df_long.drop_duplicates(subset=['Code du département', 'new_code_commune', 'Candidate number'], keep='first')
    if 'Code du canton' not in df_long.columns:
        df_long_canton = pd.merge(df_long,
                                  table_corres[['Nom commune', 'dept_canton']],
                                  left_on='Libellé de la commune',
                                  right_on='Nom commune',
                                  how='left')
    else:
        df_long_canton = df_long.copy()
        dpt = df_long_canton['Code du département'].astype(str)
        canton = df_long_canton['Code du canton'].astype(str)
        df_long_canton['dept_canton'] = dpt.str.cat(canton, sep='_')
    df_long_canton['election'] = filename



    if filename in ('municipales_2008', 'regionales_2010', 'cantonales_2008'):
        df_long_canton_gr = df_long_canton.groupby(
            ['Code du département', 'Libellé du département',
             'Code de la commune', 'Inscrits',
             'Abstentions', '% Abs/Ins', 'Votants', '% Vot/Ins',
             'Blancs et nuls', '% BlNuls/Ins', '% BlNuls/Vot', 'Exprimés',
             '% Exp/Ins', '% Exp/Vot', 'Nuance', 'dept_canton',
             'election'], as_index=False)['Voix'].sum()
        #df_long_canton_gr = df_long_canton_gr[df_long_canton_gr.Voix>0]

        full_df = df_long_canton_gr.groupby(["dept_canton", "Nuance"], as_index=False)['Inscrits', 'Abstentions', 'Blancs et nuls', 'Exprimés', 'Voix'].sum().reset_index()
        full_df = full_df.assign(**{"% Voix/Exp": full_df['Voix'] / full_df['Exprimés'] * 100,
                                    "% Abs/Ins": full_df['Abstentions'] / full_df['Inscrits'] * 100})

        full_df['election'] = filename
    else:
        full_df = df_long_canton.copy()

    full_df = full_df.assign(Nuance=full_df.Nuance.str.replace('^L', ''))
    election_results[filename] = full_df

common_cols = ['election', 'Nuance', '% Voix/Exp', "% Abs/Ins", 'dept_canton']
all_elec = pd.concat([df[common_cols] for df in election_results.values()], axis=0)
vote_per_nuance = all_elec.groupby(['election', 'dept_canton', 'Nuance'])['% Voix/Exp'].sum()
vote_per_nuance = vote_per_nuance.to_frame().reset_index()
vote_per_nuance.to_csv('results/concatenate_all_election.csv', index=False)

seaborn.catplot(data=vote_per_nuance, y='Nuance', x='% Voix/Exp', orient='h', col='election', kind='box', col_wrap=3)
plt.savefig('results/vote_per_nuance.pdf', bbox_inches='tight')
