import os
import ntpath
import pandas as pd

folder = "test" # must be "OO_output"
PWD = os.getcwd() + "/"
path = PWD + folder + "_output"
csvpath = os.path.join(path, folder + ".csv")



df = pd.read_csv(csvpath, index_col=0)
for i in range(len(df)):
	path_before = df.loc[i, 'image']
	#basename = os.path.basename(path_before)  #from Linux csv
	basename = ntpath.basename(path_before)  #from Windows csv
	df.loc[i, 'image'] = os.path.join(path, basename)
df.to_csv(csvpath)
