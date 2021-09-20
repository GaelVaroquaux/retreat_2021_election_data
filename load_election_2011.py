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

