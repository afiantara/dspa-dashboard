import pandas as pd

colors = {'first_set':  ['ID.AC', 'ID.BA', 'ID.BB', 'ID.BR', 'ID.BT', 'ID.CA', 'ID.DA', 'ID.EE'],
          'second_set': ['Yellow', 'Yellow', 'Yellow', 'White', 'White', 'Blue', 'Blue', 'Blue']
          }

df = pd.DataFrame(colors)
df['first_set'] = df['first_set'].replace(['.'], '-')
cols = df.columns.tolist() 
cols.append('X')
print(cols)