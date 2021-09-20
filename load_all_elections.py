import pandas as pd

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
    election_results[filename] = df_long

