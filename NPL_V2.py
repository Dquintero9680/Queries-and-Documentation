
# coding: utf-8

import pandas as pd
import numpy as np
import re

def any_non_numerical(word):
    return len(re.findall(r'\D+',word))
def extract_zip(word):
    return ''.join(re.findall(r'\d?',word))
def find_box(word):
    return len(re.findall(r'([P]{1}[.]?[O]{1}[\W])|(BOX)',word))
def find_start_az(word):
    return len(re.findall(r'^[A-Za-z]',word))
def find_start_symble(word):
    return len(re.findall(r'^\W',word))
def find_combined_add(word):
    return len(re.findall(r'^\d+\-\d+',word))

def swap_2digit(word):
    word = list(word)
    temp = word[1]
    word[1] = word[2]
    word[2] = temp
    return ''.join(word)

Patron_raw = pd.read_csv('/Users/x208851/Desktop/NPL_project/Patron Profiles File  with barcodes 10-16-18.csv')
z_plus4 = pd.read_excel('/Users/x208851/Desktop/NPL_project/Copy of SampleAddr_Finalized.xlsx')
#Patron = pd.read_excel('/Users/x208851/Desktop/NPL_project/Patron Profiles File  with barcodes 10-16-18.xlsx')

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

Patron_raw['D_region'] = Patron_raw['region'].fillna('/N/A')

Patron_raw['D_region'] = Patron_raw['D_region'].apply(extract_zip)

Patron_raw['D_region'] = Patron_raw['D_region'].str[:5]

Patron_raw['D_region'] = np.where(Patron_raw['D_region'].str.len()==5,Patron_raw['D_region'],'N/A')

Patron_raw['zip'] = np.where((Patron_raw['zip']=='00000')&(Patron_raw['D_region']!='N/A'),Patron_raw['D_region'],
                            Patron_raw['zip'])

#load zip to state/city table
zip2state = pd.read_csv('/Users/x208851/Desktop/NPL_project/free-zipcode-database-Primary.csv')
zip2state['zip'] = zip2state['Zipcode'].astype(str).str.pad(5, fillchar='0')

#join state and city information 
Patron_raw = pd.merge(Patron_raw,zip2state[['zip','State','City']],how='left',on='zip')

#clean home_library_code data, if there is no info, ==> 'no'
Patron_raw['home_library_code'] = Patron_raw['home_library_code'].str[:2]
Patron_raw['home_library_code'] = Patron_raw['home_library_code'].fillna('no')

#corrected address and zplus4
Patron_raw['addr1'] = z_plus4['FNL_ADDR_LN_1']
Patron_raw['State'] = z_plus4['FNL_STATE']
Patron_raw['City'] = z_plus4['FNL_CITY']
Patron_raw['FNL_ZIPPLUS4'] = z_plus4['FNL_ZIPPLUS4']

del Patron_raw['city']
del Patron_raw['region']
del Patron_raw['postal_code']
del Patron_raw['record_id']
del Patron_raw['id']
del Patron_raw['id.1']

#PO BOX processing
PO_mask = Patron_raw['addr1'].apply(find_box)>0
Patron_raw.loc[PO_mask,'addr1'] = '5 WASHINGTON STREET'
Patron_raw.loc[PO_mask,'FNL_ZIPPLUS4'] = '07102-3105'
Patron_raw.loc[PO_mask,'City'] = 'NEWORK'
Patron_raw.loc[PO_mask,'State'] = 'NJ'

PO_mask.sum()

#start with non numerical 
AZ_mask = Patron_raw['addr1'].apply(find_start_az)>0
print('Remove:',AZ_mask.sum(),'rows')
Patron_raw = Patron_raw[~AZ_mask]

#combination address processing (1879/1583)
comb_mask = Patron_raw['addr1'].apply(find_combined_add)>0
temp_address = Patron_raw['addr1'].str.split('-',expand=True)
print('combination address:',comb_mask.sum())

Patron_raw['addr1'] = np.where(comb_mask,temp_address[1],Patron_raw['addr1'])

Patron_raw.to_csv('/Users/x208851/Desktop/NPL_Patron_cleaned_v4.csv',index=False)