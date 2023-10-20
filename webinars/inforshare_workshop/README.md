# Infoshare Workshop Dataset Description

The dataset comes from the [folktables](https://github.com/socialfoundations/folktables/tree/main) library
using US Census data.

It was created using data from IL regarding the ACSPublicCoverage prediction task.
Data from 2015 were used to train a RandomForest model. Data from 2016 are used as
a reference dataset to establish a baseline for performane. Data from 2017 and 2018 are
used as an analysis data to monitor the trained model's performance.

## Notes

[Data Dictionary Link for 2015 data](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict15.pdf)

```
# list of categorical variables in dataset
cat_vars = [
    "SCHL"
    "MAR"
    "DIS"
    "ESP"
    "CIT"
    "MIG"
    "MIL"
    "ANC"
    "NATIVITY"
    "DEAR"
    "DEYE"
    "DREM"
    "SEX"
    "RAC1P"
    "ESR"
    "FER"
]
```