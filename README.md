# CEAP Reimbursement Analysis

|                |                                                            |
| -------------- | ----------------------------------------------------------:|
| Language       | [Python 3.7](https://www.python.org/ "Python's Homepage")  |

Checking on the hypothesis that Brazilian politicians are spending public money in establishments owned by people related with political parties.

This project is inspired by this [Serenata de Amor](https://github.com/okfn-brasil/serenata-de-amor)'s issue: ["Hypothesis: there are politicians spending mostly with people from the same political party"](https://github.com/okfn-brasil/serenata-de-amor/issues/121)

---

## ABOUT
In this project we are going to link political parties affiliates with owners of 
establishments where federal deputies have asked for reimbursement by the CEAP 
(Quota for the exercise of the Brazilian parliamentary activity).

Since we don't have CPF data of affiliates and owners of establishments, the match 
between them is made using their names.

> Important to say that this *is not an accurate way to this match* because homonyms exist.
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

## BUILD WITH
Special thanks for:
* The Serenata de Amor folks
* The xpto API
* The xpto website with he

## SETUP

### Requirements
With the project cloned in your computer, go to it's folder and install the project's dependencies using:
```
pip3 install -r requirements.txt
``` 

## RUNNING THE PROJECT SCRIPTS

### [Script] Political Parties Scrapping

```
# TODO
```

### [Script] Reimbursements Enrichment

```
# TODO
```

### [Notebook] Reimbursements Establishment Owners Analysis

```
# TODO
```

---
Made by @dehatanes with :heart:
