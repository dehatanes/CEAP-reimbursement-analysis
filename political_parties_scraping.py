# -------------------------------------------------------------------------------------------------
# Web scraping to get the data of affiliate people related to political parties from all districts
# -------------------------------------------------------------------------------------------------

import io
import zipfile
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

POLITICAL_PARTIES_SOURCE_URL = 'http://dados.gov.br/dataset/filiados-partidos-politicos'

# Find the available resources in the "dados.gov" page
# Each resource represents a file with the list of affiliates of a political party in a specific Brazilian district
print('Finding resources...')
response = requests.get(POLITICAL_PARTIES_SOURCE_URL)
soup = BeautifulSoup(response.content, 'html.parser')
political_parties_resources = [a['href'] for a in soup.find_all('a', {'class': 'resource-url-analytics'}, href=True)]

# Web scraping to get the .csv resources and join them in one
final_df = pd.DataFrame()
resources_with_error = []

processed_resources = 0
total_resources = len(political_parties_resources)
print(f'-> {total_resources} resources found.')
print()
print('STARTING TO FETCH')
print('--------------------')
start_time = datetime.now()
for resource_link in political_parties_resources:
    try:
        processed_resources += 1
        response = requests.get(resource_link)
        # The downloaded resource is zipped, so we need to extract it's content
        z_file = zipfile.ZipFile(io.BytesIO(response.content))
        # Then we need to select the .csv file we are searching for...
        csv_path = [file.filename for file in z_file.filelist if 'filiados_' in file.filename][0]
        # And then we load this .csv file into a pandas data frame to join all resources in the final data frame
        current_resource_df = pd.read_csv(
            z_file.open(csv_path),
            sep=';',
            encoding='ISO-8859-1',
            parse_dates=['DATA DA REGULARIZACAO'],
        )
        final_df = final_df.append(current_resource_df, ignore_index=True)
        # Display the processing status to show this program is still alive
        qtd_lines = current_resource_df.shape[0]
        file_name = csv_path.split('/')[-1]
        print(f'[{processed_resources} / {total_resources}] '
              f'New data with {qtd_lines} lines from "{file_name}"')
    except:
        print(f'ERROR: {resource_link}')
        resources_with_error.append(resource_link)

# -------------
# FINALLY DONE
# -------------
# Report
time_spent_to_fetch = datetime.now() - start_time
print()
print('-' * 30)
print('FINISHED DATA FETCHING')
print(f'-> Time spent to fetch.............: {time_spent_to_fetch}')
print(f'-> Final dataset shape.............: {final_df.shape[0]} lines and {final_df.shape[1]} columns')
print(f'-> Amount of resources found.......: {total_resources}')
print(f'-> Amount of resources with errors.: {len(resources_with_error)}')
print()
print('Saving the data...')

current_date = datetime.now().strftime('%Y_%b_%d')
datasets_folder = 'datasets/'
final_data_file_name = f'political_parties_data_{current_date}.csv'
errors_file_name = f'fetching_errors_{current_date}.csv'

# Save full dataset
final_df.to_csv(datasets_folder + final_data_file_name)
print(f'[1/2] Full dataset saved in "{final_data_file_name}"')

# Save errors
errors_dataset = pd.DataFrame(
    {'resource_link': resources_with_error},
    columns=['resource_link'],
)
errors_dataset.to_csv(datasets_folder + errors_file_name)
print(f'[2/2] Errors dataset saved in {errors_file_name}')

print('\nDONE')
