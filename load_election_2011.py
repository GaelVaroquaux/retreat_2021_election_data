import pandas as pd


# Sheets in the XLS file:
# 0. France entière
# 1. Région T1
# 2. Région T2
# 3. Départements T1
# 4. Départements T2
# 5. Circo leg T1
# 6. Circo leg T2
# 7. Cantons T1
# 8. Cantons T2
# 9. Elus

circo_t1_df = pd.read_excel('data/cantonales_2011.xls', sheet_name=7)

candidate_vars =  ['Nuance', 'Voix', '% Voix/Ins', '% Voix/Exp',
                   'Sexe', 'Nom', 'Prénom']

circo_t1_df = circo_t1_df.rename({
                    v: v + '.0'
                    for v in candidate_vars
                    }, axis=1)

max_num_candidate = len([c for c in circo_t1_df.columns
                         if c.startswith('% Voix/Exp.')])

circo_t1_df.columns = pd.MultiIndex.from_tuples([
                (c.split('.')[::-1] if ('.' in c) else ('general', c))
                for c in circo_t1_df.columns
            ])

# Unstack: go from wide to long
circo_t1_long = circo_t1_df[['%i' % i for i in range(max_num_candidate)]
                            ].unstack().unstack(level=1)
# Work on the index
circo_t1_long = circo_t1_long.reset_index()
circo_t1_long = circo_t1_long.rename({
                    'level_0': 'Candidate number',
                    'level_1': 'index',
                    }, axis=1)

circo_t1_long = pd.merge(left=circo_t1_df['general'],
                         right=circo_t1_long,
                         right_on='index',
                         left_index=True)

dpt = circo_t1_long['Code du département'].astype(str)
canton = circo_t1_long['Code du canton'].astype(str)
circo_t1_long['dept_canton'] = dpt.str.cat(canton, sep='_')


