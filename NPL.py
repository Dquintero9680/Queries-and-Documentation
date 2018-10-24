
#Prudential CO 10/22/2018
#python 3.6

import pandas as pd
import numpy as np
import re

def any_non_numerical(word):
    return len(re.findall(r'\D+',word))
def extract_zip(word):
    return ''.join(re.findall(r'\d?',word))

Patron_raw = pd.read_csv('/Users/x208851/Desktop/NPL_project/Patron Profiles File  with barcodes 10-16-18.csv')
Patron = pd.read_excel('/Users/x208851/Desktop/NPL_project/Patron Profiles File  with barcodes 10-16-18.xlsx')

#split zip code to two part, zip and zip+4
Patron_raw = pd.concat([Patron_raw,Patron_raw['postal_code'].str.split('-',expand=True)],axis=1)
Patron_raw = Patron_raw.rename(columns={0:'zip',1:'zip+4'})

Patron_raw['zip'] = Patron_raw['zip'].fillna('00000')
Patron_raw['zip+4'] = Patron_raw['zip+4'].fillna('0000')

#to remove any zip information in wrong format
try:
    Patron_raw['zip'].astype('int64')
    print('All Zip5 code are numerical!')
except ValueError:
    print('Some Zip5 code are non-numerical, assign 00000 as a dummy zip!')
    Patron_raw.loc[Patron_raw['zip'].apply(any_non_numerical)>0,'zip'] = '00000'
    
try:
    Patron_raw['zip+4'].astype('int64')
    print('All Zip+4 code are numerical!')
except ValueError:
    print('Some Zip+4 code are non-numerical, assign 0000 as a dummy zip+4!')
    Patron_raw.loc[Patron_raw['zip+4'].apply(any_non_numerical)>0,'zip+4'] = '0000'

print('Total Row:',Patron_raw.shape[0])
zip5 = (Patron_raw['zip']!='00000').sum()
print('Zip is more than 5 digits:',zip5)
zip5_plus4 = (Patron_raw['zip+4']!='0000').sum()
print('Zip is 9 digits:',zip5_plus4)
zip_null = (Patron_raw['zip']=='00000').sum()
print('No Zip:',zip_null)


Patron_raw['region'] = Patron_raw['region'].fillna('/N/A')
Patron_raw['region'] = Patron_raw['region'].apply(extract_zip)
Patron_raw['region'] = Patron_raw['region'].str[:5]
Patron_raw['region'] = np.where(Patron_raw['region'].str.len()==5,Patron_raw['region'],'N/A')
Patron_raw['zip'] = np.where((Patron_raw['zip']=='00000')&(Patron_raw['region']!='N/A'),Patron_raw['region'],
                            Patron_raw['zip'])

#load zip to state/city table
zip2state = pd.read_csv('/Users/x208851/Downloads/free-zipcode-database-Primary.csv')
zip2state['zip'] = zip2state['Zipcode'].astype(str).str.pad(5, fillchar='0')

#join state and city information 
Patron_raw = pd.merge(Patron_raw,zip2state[['zip','State','City']],how='left',on='zip')

#clean home_library_code data, if there is no info, ==> 'no'
Patron_raw['home_library_code'] = Patron_raw['home_library_code'].str[:2]
Patron_raw['home_library_code'] = Patron_raw['home_library_code'].fillna('no')

del Patron_raw['city']
del Patron_raw['region']
del Patron_raw['postal_code']
del Patron_raw['record_id']
del Patron_raw['id']
del Patron_raw['id.1']

Patron_raw.to_csv('/Users/x208851/Desktop/NPL_Patron_cleaned.csv',index=False)

