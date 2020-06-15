import pandas as pd
df = pd.read_csv('result.csv', sep=',')
df = df.sample(frac=1)
df.to_csv('out.csv', index=False)