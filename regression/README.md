# Drift and performance dashboards for regression using NannyML, PostgreSQL and Grafana

The following example shows how to run NannyML from the command line to detect drift, estimate performance when targets
are missing and calculate realized performance when targets are available. 

The calculated results are then stored in a PostgreSQL database. Grafana has been configured to use this database as a
data source, allowing us to explore and visualize the results in an interactive and graphical way. We've included two
example dashboards to get started quickly.


## Requirements

All components of the example are running on your local system using containers. We're using `Docker` as a runtime and
`Docker compose` as an orchestrator.

Please ensure you have `Docker` (>= 20.10.17) and `Docker compose` (>= 2.10.2) available on your system.
You can follow the [official installation instructions](https://docs.docker.com/desktop/) for additional support.

## Walkthrough

### Reviewing the NannyML configuration

Let's quickly check out the NannyML configuration. It is located in the 
[`nann.yml` configuration file](nannyml/config/nann.yml).

The *reference*, *analysis* and available *target* datasets are defined first. They are to be read from the container filesystem under the 
`/data` directory. 

```yaml
input:
  reference_data:
    path: /data/regression_synthetic_reference.csv

  analysis_data:
    path: /data/regression_synthetic_analysis.csv

  target_data:
    path: /data/regression_synthetic_analysis_targets.csv
```

Check the [`docker-compose` file](docker-compose.yml) to see how the local data files
are mounted into the container.

We then define where to write our results to using the `output` section.
We are writing to a database here and provide a *connection string* to configure where and how to connect.
Remark that we also provide an optional `model_name`, to facilitate querying in the database
and ensure we can reuse the database to store other model results as well.

```yaml
output:
  database:
    connection_string: postgresql://nannyml:we<3nannyml@metrics-store:5432/nannyml
    model_name: car_price_regression
```

We can instruct NannyML it is working on a regression model by providing the `problem_type` parameter. 
The optional `chunker` section allows us to configure chunking. Here we chunk by day, ensuring we have a single value
per day for each metric. That should yield some nice graphs!

```yaml
problem_type: regression

chunker:
  chunk_period: D
```

And finally we tell NannyML how to interpret your data, i.e. what columns represent features, predictions, targets etc.
We do this using the `column_mapping` section: 

```yaml
column_mapping:
  features:
    - car_age
    - km_driven
    - price_new
    - accident_count
    - door_count
    - transmission
    - fuel
  timestamp: timestamp
  y_pred: y_pred
  y_true: y_true
```

### Starting the containers

We'll now spin up the three containers described in the [docker compose](docker-compose.yml) configuration:
1. `nannyml`: the NannyML container crunching the numbers
2. `metric-store`: a PostgresQL container providing the database where the results will be written into
3. `grafana`: a Grafana container preconfigured to connect to the `metric store` and visualize that data 
   in two included dashboards.

First ensure you're in the `regression` directory, then use the following command to start them:

```shell
docker compose up
```

You'll see a lot of outputs flying by in the terminal, these are both PostgreSQL and Grafana booting.
After some time you'll start seeing the NannyML CLI output show up. You can see all of the calculators and estimators 
being run, before this container exits.

```
regression-nannyml-1        | ──────────────────── Confidence Base Performance Estimator ─────────────────────
regression-nannyml-1        |            CBPE does not support 'REGRESSION' problems. Skipping   runner.py:456
regression-nannyml-1        |            CBPE estimation.
regression-nannyml-1        | ──────────────────────────── Direct Loss Estimator ─────────────────────────────
regression-nannyml-1        |            fitting on reference data                               runner.py:530
regression-nannyml-1        | [11:26:33] estimating on analysis data                             runner.py:540
regression-nannyml-1        | [11:26:34] writing results                                         runner.py:564
regression-nannyml-1        |
regression-nannyml-1        |
regression-nannyml-1        | Run complete ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
regression-nannyml-1 exited with code 0
```

At this point all data should be available in the database.

### Inspecting the database

We can use connect directly to the database container to get a look at the data inside.
Open up a new terminal and use the following command to spawn an interactive shell in the container:

```shell
docker compose exec -ti metrics-store /bin/bash
```

Now we can connect to the database. Note that we've seeded our database to create a custom database and a new user.
Feel free to check out the used [*DDL* script](db/ddl.sql) and the [docker compose](docker-compose.yml) file to see how. 

In the shell we've just opened, type the following to connect to the `nannyml` database as user `nannyml`:

```shell
psql nannyml nannyml
```

Inside the database console we can now check what tables are available using the `\dt+` command:

```
nannyml=> \dt+
 public | cbpe_performance_metrics                  | table | nannyml | permanent   | heap          | 8192 bytes |
 public | data_reconstruction_feature_drift_metrics | table | nannyml | permanent   | heap          | 16 kB      |
 public | dle_performance_metrics                   | table | nannyml | permanent   | heap          | 48 kB      |
 public | model                                     | table | nannyml | permanent   | heap          | 16 kB      |
 public | realized_performance_metrics              | table | nannyml | permanent   | heap          | 48 kB      |
 public | run                                       | table | nannyml | permanent   | heap          | 8192 bytes |
 public | statistical_feature_drift_metrics         | table | nannyml | permanent   | heap          | 56 kB      |
 public | statistical_output_drift_metrics          | table | nannyml | permanent   | heap          | 16 kB      |
 public | target_drift_metrics                      | table | nannyml | permanent   | heap          | 16 kB      |
```

We can perform simple queries to inspect some of the data, such as the DLE performance metrics:

```
nannyml=> select * from dle_performance_metrics limit 10;
  1 |        1 |      1 | 2017-02-16 00:00:00 | 2017-02-17 00:00:00 | 2017-02-16 12:00:00 | MAE         | 869.0190751005765 | f     | 885.101337637579 | 808.5402395237686
  2 |        1 |      1 | 2017-02-17 00:00:00 | 2017-02-18 00:00:00 | 2017-02-17 12:00:00 | MAE         | 850.8380044377367 | f     | 885.101337637579 | 808.5402395237686
  3 |        1 |      1 | 2017-02-18 00:00:00 | 2017-02-19 00:00:00 | 2017-02-18 12:00:00 | MAE         | 841.7973301178172 | f     | 885.101337637579 | 808.5402395237686
  4 |        1 |      1 | 2017-02-19 00:00:00 | 2017-02-20 00:00:00 | 2017-02-19 12:00:00 | MAE         | 847.3458004361022 | f     | 885.101337637579 | 808.5402395237686
  5 |        1 |      1 | 2017-02-20 00:00:00 | 2017-02-21 00:00:00 | 2017-02-20 12:00:00 | MAE         | 851.2066515236666 | f     | 885.101337637579 | 808.5402395237686
  6 |        1 |      1 | 2017-02-21 00:00:00 | 2017-02-22 00:00:00 | 2017-02-21 12:00:00 | MAE         | 846.9276956905213 | f     | 885.101337637579 | 808.5402395237686
  7 |        1 |      1 | 2017-02-22 00:00:00 | 2017-02-23 00:00:00 | 2017-02-22 12:00:00 | MAE         | 833.5151359638033 | f     | 885.101337637579 | 808.5402395237686
  8 |        1 |      1 | 2017-02-23 00:00:00 | 2017-02-24 00:00:00 | 2017-02-23 12:00:00 | MAE         | 851.3197582768654 | f     | 885.101337637579 | 808.5402395237686
  9 |        1 |      1 | 2017-02-24 00:00:00 | 2017-02-25 00:00:00 | 2017-02-24 12:00:00 | MAE         | 850.8792012081623 | f     | 885.101337637579 | 808.5402395237686
 10 |        1 |      1 | 2017-02-25 00:00:00 | 2017-02-26 00:00:00 | 2017-02-25 12:00:00 | MAE         | 846.4863687654673 | f     | 885.101337637579 | 808.5402395237686```
```

Or we can count the number of alerts per day for each metric:

```
nannyml=> select count(*), metric_name from dle_performance_metrics where alert group by metric_name;
    12 | MSE
    12 | RMSE
    12 | MSLE
    12 | MAE
    12 | MAPE
    12 | RMSLE
```

You can now exit the database console by typeing `\q` followed by `exit` to exit the database container shell.


### Viewing the dashboards

Now that we know what we can play with we can connect to our local Grafana instance. 

Open up a web browser and visit [http://localhost:3000](http://localhost:3000) to open up Grafana. You can log in with 
username `nannyml` and password `nannyml`.

<p><img src="_assets/grafana_login.png"  alt="Logging in to Grafana"/></p>

In the menu on the left hand side, hover over the `dashboards` menu, then click `browse` to get an overview of 
the available dashboards. The example dashboards are located in the `NannyML` directory.

<p><img src="_assets/grafana_dashboards_list.png" alt="Browsing dashboards"></p>

You can now view both the *Drift* and *Performance* example dashboards. 

<p><img src="_assets/grafana_dashboard_drift.png" alt="Drift dashboard" /></p>

<p><img src="_assets/grafana_dashboard_performance.png" alt="Performance dashboard" /></p>

Be sure to review the configuration behind the dashboard panels and variables to see how they are populated. 

### Stopping the demo

You can stop the spun up containers by forming `CTRL+C`. To fully remove the containers you can follow up with the 
`docker compose down` command.

## Final remarks

- Grafana also allows you to configure alert rules and notifications, check out the 
[official documentation](https://grafana.com/docs/grafana/latest/alerting/alerting-rules/) on how to set that up.
