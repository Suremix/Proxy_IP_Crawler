import pandas as pd

ip_data_df = pd.read_csv("/root/myData/ip_open_dataset_old.csv")
print(ip_data_df.shape)

ip_data_df = ip_data_df.loc[0:-1, :]
print(ip_data_df.shape)

