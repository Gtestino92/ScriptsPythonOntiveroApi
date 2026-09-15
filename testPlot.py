import pandas as pd
import numpy as np
#from matplotlib import pyplot as plt

#file = open('transpByFormato.xlsx','rb')
dfs = pd.read_excel('pedidosByFormato.xlsx')
dfs.dropna(inplace=True)
dfs.set_index('fecha', inplace=True)


#plt.figure(figsize=(10,4))
#plt.plot(dfs["BSQ"])
#plt.show()
    