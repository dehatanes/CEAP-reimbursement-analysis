# -----------------------------------------------------------------------------------------------------------------------
# - In this script we will get all the reimbursements data and then we will enrich
#   them with more information about the supplier for that reimbursement in order to
#   know the owners of the establishment.
# - We will use an API called "Receita WS", where we can use the of the establishment
#   to get this extra information that we need.
# -----------------------------------------------------------------------------------------------------------------------
import os
import json
import time
import requests
import numpy as np
import pandas as pd
from pymongo import MongoClient
from serenata_toolbox.chamber_of_deputies.reimbursements import Reimbursements

# ---------------------------------------------------------
# Configure a database to store the receita_ws responses
"""
As there are a lot of different CNPJs to be checked and the 
Receita WS API has a limit of requests per month, we are 
going to store the response for every CNPJ we check in a 
MongoDB database so we can freely review that data later.
"""
# ---------------------------------------------------------

MONGO_CONNECTION_URL = os.environ['MONGO_DB__CONNECTION_URL']
MONGO_CLUSTER_NAME = os.environ['MONGO_DB__CLUSTER_NAME']
MONGO_COLLECTION = os.environ['MONGO_DB__COLLECTION_NAME']

client = MongoClient(MONGO_CONNECTION_URL)
db = client[MONGO_CLUSTER_NAME]
receita_colection = db[MONGO_COLLECTION]

print(f'-> MongoDB connected to cluster "{MONGO_CLUSTER_NAME}" - collection "{MONGO_COLLECTION}"')

# --------------------------------------------------------------------
# Get the reimbursements from 2018 from Serenata de Amor Operation
# --------------------------------------------------------------------
fetch_chamber_reimbursements = Reimbursements('2018', 'data/')
fetch_chamber_reimbursements()
reimbursements_raw_df = pd.read_csv(
    'data/reimbursements-2018.csv',
    dtype={
        'applicant_id': np.str,
        'cnpj_cpf': np.str,
        'congressperson_id': np.str,
        'leg_of_the_trip': np.str,
        'subquota_group_description': np.str,
        'subquota_number': np.str,
    }
)
print('-> Reimbursements dataframe imported from Serenata Toolbox: Shape {}'.format(reimbursements_raw_df.shape))

# --------------------------------------------------
# Get a list with the CNPJs that we need to process
# --------------------------------------------------

# First let's get all the different CNPJs in the dataset
cnpjs_list = reimbursements_raw_df.cnpj_cpf.unique()


def remove_already_processed_cnpjs(cnpjs_series):
    # for all the cnpj's already processed
    for doc in receita_colection.find():
        # if there was no problem with the cnpj
        if not doc.get("retry"):
            # remove that cnpj from the list of those that we will process
            cnpjs_series = cnpjs_series[cnpjs_series != doc.get("raw_cnpj")]
    return cnpjs_series


# And them let's keep only the ones that we still have no information stored in the database
cnpjs_list = remove_already_processed_cnpjs(cnpjs_list)

print()
print("- Amount of different CNPJs in the reimbursements data frame: {}".format(len(cnpjs_list)))
print("- Amount of different CNPJs that still need to be processed: {}".format(len(cnpjs_list)))
print()

# --------------------------------------------------
# Using the Receita WS API
# --------------------------------------------------

RECEITA_API_AUTH_TOKEN = f'Bearer {os.environ["RECEITA_WS_API__AUTH_TOKEN"]}'

processed_cnpjs = 0
total_cnpjs = len(cnpjs_list)

print('STARTING TO FETCH')
print('--------------------')
for cnpj in cnpjs_list:
    processed_cnpjs += 1
    print(f'[{processed_cnpjs}/{total_cnpjs}] CNPJ: {cnpj}')

    time.sleep(30)  # Delay 30 seconds so the API don't block our request
    try:
        # perform API request
        response = requests.get(
            f'https://www.receitaws.com.br/v1/cnpj/{cnpj}',
            headers={'Authorization': RECEITA_API_AUTH_TOKEN}
        )
        # insert data into database
        if response.status_code == 200:
            response_as_json = json.loads(response.text)
            response_as_json["raw_cnpj"] = cnpj
            receita_colection.insert_one(response_as_json)

            # Report status
            if len(response_as_json.get('qsa', [])) != 0:
                print(f'\t- [SUCCESS] CNPJ: {cnpj}')
            elif response_as_json.get('message'):
                print(f'\t- [INVALID] CNPJ: {cnpj} | Message: {response_as_json.get("message")}')
            else:
                print(f'\t- [MISSING OWNERS] CNPJ: {cnpj} | Company name: "{response_as_json.get("nome")}"')
        else:
            response_as_json = {
                'retry': response.status_code,
                'raw_cnpj': cnpj
            }
            print(f'\t- [REQUEST ERROR] CNPJ: {cnpj} | Status code: {response.status_code}')
            receita_colection.insert_one(response_as_json)
            time.sleep(10)  # Delays for 10 additional seconds.
    except Exception as e:
        print("\t- [EXCEPTION] {}".format(e))
        time.sleep(5)  # Delays for 5 additional seconds.

# Report
print()
print('-' * 30)
print('FINISHED DATA FETCHING')
print()
print("- TOTAL DOCS IN DATABASE: {}\n".format(receita_colection.count_documents({})))
print("-> Amount of success........................: {}".format(receita_colection.count_documents({"$and": [{"qsa": {"$exists": True}}, {"qsa": {"$not": {"$size": 0}}}]})))
print("-> Amount of invalid cnpj's.................: {}".format(receita_colection.count_documents({"message": {"$exists": True}})))
print("-> Amount of cnpj's missing owners info.....: {}".format(receita_colection.count_documents({"qsa": {"$size": 0}})))
print("-> Amount of errors with the cnpj request...: {}".format(receita_colection.count_documents({"retry": {"$exists": True}})))

# ----------------------------------------------------------------------
# Finally enrich the reimbursements data using the data in the database
# ----------------------------------------------------------------------

print()
print('REIMBURSEMENTS DATA ENRICHMENT...')

# let's create 5 more columns in the Serenata's reimbursements dataframe to store
# the metadata we found about the supplier company
reimbursements_raw_df['company_owners_list'] = ''         # list with the company owners info
reimbursements_raw_df['company_qtd_owners'] = None        # amount of owners that the company have
reimbursements_raw_df['receita_api_company_name'] = ''    # company name registered in the receitaWS API
reimbursements_raw_df['company_metadata'] = None          # json with all the info we got about the company
reimbursements_raw_df['receita_api_erro'] = None          # flag indicating if we got an error trying to get the company in the API or no

# correct cnpjs
print(f'[1/2] Adding info of the companies that we properly got information about...')
for document in receita_colection.find({"qsa": {"$exists": True}}, no_cursor_timeout=True):
    df_filter = reimbursements_raw_df.cnpj_cpf == document.get('raw_cnpj')

    reimbursements_raw_df.loc[df_filter, ['company_owners_list']] = str(document.get('qsa'))
    reimbursements_raw_df.loc[df_filter, ['company_qtd_owners']] = len(document.get('qsa'))
    reimbursements_raw_df.loc[df_filter, ['receita_api_company_name']] = document.get('nome')
    reimbursements_raw_df.loc[df_filter, ['company_metadata']] = str(document)
    reimbursements_raw_df.loc[df_filter, ['receita_api_erro']] = False
    break
print("\t- Done")

# cnpjs and cpfs with error
print(f'[2/2] Adding info of the companies that did not got information about...')
for document in receita_colection.find({"$or": [{"retry": {"$exists": True}}, {"message": {"$exists": True}}]},
                                       no_cursor_timeout=True):
    df_filter = reimbursements_raw_df.cnpj_cpf == document.get('raw_cnpj')

    reimbursements_raw_df.loc[df_filter, ['receita_api_company_name']] = document.get('name')
    reimbursements_raw_df.loc[df_filter, ['company_metadata']] = str(document)
    reimbursements_raw_df.loc[df_filter, ['receita_api_erro']] = True
    break
print("\t- Done")

# ----------------------------
# SAVE DATASET FOR BACKUP
# ----------------------------
file_name = 'reimbursements_2018_complete_df.csv'
reimbursements_raw_df.to_csv(f"datasets/{file_name}")
print()
print(f'-> Reimbursement dataset saved in "{file_name}"')
print('DONE')
