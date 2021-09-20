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

circo_t1_df = pd.read_excel('data/cantonales_2011.xls', sheet_name=5)

circo_t1_df = circo_t1_df.rename({
                    'Code Nuance': 'Code Nuance.0',
                    'Voix': 'Voix.0',
                    '% Voix/Ins': '% Voix/Ins.0',
                    '% Voix/Exp': '% Voix/Exp.0',
                    }, axis=1)

circo_t1_df.columns = pd.MultiIndex.from_tuples([
                (c.split('.')[::-1] if ('.' in c) else ('general', c))
                for c in circo_t1_df.columns
            ])

circo_t1_long = circo_t1_df[['%i' % i for i in range(14)]].unstack(level=1)

