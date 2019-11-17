# CEAP Reimbursement Analysis

|                |                                                            |
| -------------- | ----------------------------------------------------------:|
| Language       | [Python 3.7](https://www.python.org/ "Python's Homepage")  |

Checking on the hypothesis that Brazilian politicians are spending public money 
destinated to parliamentarian activity in establishments owned by people related 
to their political parties.

This project is inspired by this [Serenata de Amor](https://github.com/okfn-brasil/serenata-de-amor)'s 
issue: ["Hypothesis: there are politicians spending mostly with people from the same political party"](https://github.com/okfn-brasil/serenata-de-amor/issues/121)

---

## ABOUT
In this project, we are going to link political parties' affiliates with owners of
establishments where federal deputies have asked for reimbursement by the CEAP 
(Quota for the exercise of the Brazilian parliamentary activity).

Since we don't have the CPF of affiliates and owners of establishments, the match 
between them is made using their names.

> Important to say that this *is not an accurate way to do this match* because homonyms exist.
But it is still a way to help finding suspicious cases automatically with the same 
allowances a human would have access to if wanted to perform the same search manually.

In order to do it, we need data of:
* The reimbursements made using the CEAP
* The political parties affiliates list


I got this datasets and both are in .csv files in the `datasets` folder.

You can learn more about how I got this data and how it was handled, enriched and analysed in the scripts:
* [[Script] Political Parties Scrapping](https://github.com/dehatanes/CEAP-reimbursement-analysis#script-political-parties-scrapping)
* [[Script] Reimbursements Enrichment](https://github.com/dehatanes/CEAP-reimbursement-analysis#script-reimbursements-enrichment)
* [[Notebook] Reimbursements Establishment Owners Analysis](https://github.com/dehatanes/CEAP-reimbursement-analysis#notebook-reimbursements-establishment-owners-analysis)


## SETUP

### Requirements
With the project cloned in your computer, go to it's folder and install the project's dependencies using:
```
pip3 install -r requirements.txt
``` 

### Setup Mongo DB
**This is only necessary if you are going to use the [Reimbursements Enrichment script](https://github.com/dehatanes/CEAP-reimbursement-analysis#script-reimbursements-enrichment).**

Create a MongoDB server (you can create one for free [here](https://www.mongodb.com/)) and export your
connection url, DB/Cluster name and collection name to your environment variables:

```bash
export MONGO_DB__CONNECTION_URL=<YOUR_MONGO_DB_CONNECTION_URL>
export MONGO_DB__CLUSTER_NAME=<YOUR_MONGO_DB_CLUSTER_NAME>
export MONGO_DB__COLLECTION_NAME=<YOUR_MONGO_DB_MONGO_DB__COLLECTION_NAME>
```

## Setup Receita WS
**This is only necessary if you are going to use the [Reimbursements Enrichment script](https://github.com/dehatanes/CEAP-reimbursement-analysis#script-reimbursements-enrichment).**

Create an account at [ReceitaWS](https://www.receitaws.com.br/), get your Authentication Token and then
add it to your environment variables:

```bash
export RECEITA_WS_API__AUTH_TOKEN=<YOUR_RECEITA_WS_API_AUTH_TOKEN>
```

## RUNNING THE PROJECT SCRIPTS AND ANALYSIS

### [Script] Political Parties Scrapping
This script is used to generate the dataset with all the affiliates of all the political parties
from all the Brazilian districts.

This information is scrapped from the ['dados.gov' website](http://dados.gov.br/dataset/filiados-partidos-politicos).

The resulting dataset will be stored in a `/datasets` folder with the name `political_parties_data_<DATE>.csv`,
In this folder you can also find a file called `fetching_errors_<DATE>.csv`
with the resources from 'dados.gov' that could not be fetched. 

You can generate an updated dataset running:
```
python3 political_parties_scraping.py
```
> But be careful, it may take a long time to finish and the resulting dataset is huge!
 

### [Script] Reimbursements Enrichment

This script is used to get all the reimbursements data from [Serenata de Amor Toolbox](https://github.com/okfn-brasil/serenata-toolbox#serenata-de-amor-toolbox)
(more precisely, the dataset with the reimbursements of 2018) and then enrich this data with
more information about the supplier for that reimbursement in order to know the owners of 
the establishment.

We will use an API called [Receita WS](https://www.receitaws.com.br/), where we can use the
CNPJ of the establishment to get this extra information that we need.

The resulting dataset will be stored in a `/datasets` folder with the name `reimbursements_2018_complete_df.csv`,

You can generate an updated dataset running:
```
python3 reimbursements_enrichment.py
```
> But be careful, it may take a long time to finish and the resulting dataset is huge!

> Also, make sure you follow the Setup to correctly set the necessary environment variables. 


### [Notebook] Reimbursements Establishment Owners Analysis

The join of the previously cited data frames and the analysis of the owners of the suppliers
of the reimbursements are in the [`reimbursements_establishment_owners_analysis.ipynb`](https://github.com/dehatanes/CEAP-reimbursement-analysis/blob/master/reimbursements_establishment_owners_analysis.ipynb).

You can open it as a [Jupyter Notebook file](https://jupyter.org/).

---
Made with :heart: by @dehatanes
