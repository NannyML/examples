# Drift and performance dashboards for regression using NannyML, PostgreSQL and Grafana

The following example shows how to run NannyML from the command line to detect drift, estimate performance when targets
are missing and calculate realized performance when targets are available. 

The calculated results are then stored in a PostgreSQL database. Grafana has been configured to use this database as a
data source, allowing us to explore and visualize the results in an interactive and graphical way. We've included two
example dashboards to get started quickly.

This example simulates running NannyML once a day through scheduling. A day's worth of data is processed every minute
and you can see your model metrics appear automatically in your dashboards.


## Requirements

All components of the example are running on your local system using containers. We're using `Docker` as a runtime and
`Docker compose` as an orchestrator.

Please ensure you have `Docker` (>= 20.10.17) and `Docker compose` (>= 2.10.2) available on your system.
You can follow the [official installation instructions](https://docs.docker.com/desktop/) for additional support.

## Walkthrough

### Reviewing the NannyML configuration

Let's quickly check out the NannyML configuration. It is located in the 
[`nann.yml` configuration file](nannyml/config/nann.yml).

The *reference*, *analysis* are defined first. They are to be read from the container filesystem under the 
`/data` directory. 

Take note that the analysis data path has been templated and is now dependent on the time of execution. Both the input
and output configuration sections support [templating](https://nannyml.readthedocs.io/en/stable/cli/configuration_file.html?highlight=templating#templating-paths).

Because of the special preprocessing that is required for the simulation of time passing we've already joined a part
of the target data with the analysis data. This reflects an environment where model target values are only
available after a delay.

```yaml
input:
  reference_data:
    path: /data/regression_synthetic_reference.csv

  analysis_data:
    path: /data/incremental/{{year}}/{{month}}/{{day}}/{{hour}}/{{minute}}/regression_synthetic_analysis_with_partial_targets.csv

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

An additional section is configuring the schedule for NannyML to run by. In this case we tell NannyML to run every
minute, for demo purposes. In a proper production environment this period will more likely be hours or days.

```yaml
scheduling:
  interval:
    minutes: 1
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

We'll now spin up the four containers described in the [docker compose](docker-compose.yml) configuration:
1. `nannyml`: the NannyML container crunching the numbers
2. `metric-store`: a PostgresQL container providing the database where the results will be written into
3. `grafana`: a Grafana container preconfigured to connect to the `metric store` and visualize that data 
   in two included dashboards.
4. `incrementor`: a custom built container running a Python script that will take the analysis data, group it per day
   and write each group in a directory following the template used above. This will ensure that for each minute passing
   there is a directory containing a day's worth of data.

First ensure you're in the `regression` directory, then use the following command to start them:

```shell
docker compose up
```

You'll see a lot of outputs flying by in the terminal, these are both PostgreSQL and Grafana booting.
After some time you'll start seeing the NannyML CLI output show up. After the calculators and estimators have
finished running NannyML will sleep for a minute, indicating the time of its next run.

```
regression_incremental-nannyml-1        | ──────────────────── Confidence Base Performance Estimator ─────────────────────
regression_incremental-nannyml-1        |            CBPE does not support 'REGRESSION' problems. Skipping   runner.py:456
regression_incremental-nannyml-1        |            CBPE estimation.
regression_incremental-nannyml-1        | ──────────────────────────── Direct Loss Estimator ─────────────────────────────
regression_incremental-nannyml-1        |            fitting on reference data                               runner.py:530
regression_incremental-nannyml-1        | [22:05:25] estimating on analysis data                             runner.py:540
regression_incremental-nannyml-1        |            writing results                                         runner.py:564
regression_incremental-nannyml-1        |
regression_incremental-nannyml-1        |
regression_incremental-nannyml-1        | Run complete ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
regression_incremental-nannyml-1        | [22:05:25] run successfully completed, sleeping until next run at     run.py:116
regression_incremental-nannyml-1        |            2022-10-14 22:06:14.634903+02:00
```

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
                                                       List of relations
 Schema |                   Name                    | Type  |  Owner  | Persistence | Access method |    Size    | Description
--------+-------------------------------------------+-------+---------+-------------+---------------+------------+-------------
 public | cbpe_performance_metrics                  | table | nannyml | permanent   | heap          | 8192 bytes |
 public | data_reconstruction_feature_drift_metrics | table | nannyml | permanent   | heap          | 16 kB      |
 public | dle_performance_metrics                   | table | nannyml | permanent   | heap          | 16 kB      |
 public | model                                     | table | nannyml | permanent   | heap          | 16 kB      |
 public | realized_performance_metrics              | table | nannyml | permanent   | heap          | 16 kB      |
 public | run                                       | table | nannyml | permanent   | heap          | 8192 bytes |
 public | statistical_feature_drift_metrics         | table | nannyml | permanent   | heap          | 16 kB      |
 public | statistical_output_drift_metrics          | table | nannyml | permanent   | heap          | 16 kB      |
 public | target_drift_metrics                      | table | nannyml | permanent   | heap          | 16 kB      |
(9 rows)
```

We can perform simple queries to inspect some of the data, such as the DLE performance metrics. Note that there is only
data for a limited number of days.

```
nannyml=> select * from dle_performance_metrics limit 10;
 id | model_id | run_id |   start_timestamp   |    end_timestamp    |      timestamp      | metric_name |        value        | alert |   upper_threshold   |   lower_threshold
----+----------+--------+---------------------+---------------------+---------------------+-------------+---------------------+-------+---------------------+---------------------
  1 |        1 |      1 | 2017-02-16 00:00:00 | 2017-02-17 00:00:00 | 2017-02-16 12:00:00 | MAE         |   869.0190751005765 | f     |    885.101337637579 |   808.5402395237686
  2 |        1 |      1 | 2017-02-16 00:00:00 | 2017-02-17 00:00:00 | 2017-02-16 12:00:00 | MAPE        | 0.23002480905604067 | f     | 0.24270914439802063 |  0.2236432902002524
  3 |        1 |      1 | 2017-02-16 00:00:00 | 2017-02-17 00:00:00 | 2017-02-16 12:00:00 | MSE         |  1162248.8802275867 | f     |  1237538.2586267272 |  1007214.3054955051
  4 |        1 |      1 | 2017-02-16 00:00:00 | 2017-02-17 00:00:00 | 2017-02-16 12:00:00 | RMSE        |   1078.076472346738 | f     |  1113.7445456138323 |  1004.7894058546048
  5 |        1 |      1 | 2017-02-16 00:00:00 | 2017-02-17 00:00:00 | 2017-02-16 12:00:00 | MSLE        | 0.06955579311271981 | f     | 0.07600802148411293 | 0.06734137419436653
  6 |        1 |      1 | 2017-02-16 00:00:00 | 2017-02-17 00:00:00 | 2017-02-16 12:00:00 | RMSLE       |  0.2637343229705224 | f     | 0.27582231209779323 |  0.2595929712423682
  7 |        1 |      2 | 2017-02-17 00:00:00 | 2017-02-18 00:00:00 | 2017-02-17 12:00:00 | MAE         |   850.8380044377367 | f     |    885.101337637579 |   808.5402395237686
  8 |        1 |      2 | 2017-02-17 00:00:00 | 2017-02-18 00:00:00 | 2017-02-17 12:00:00 | MAPE        |   0.230285578450427 | f     | 0.24270914439802063 |  0.2236432902002524
  9 |        1 |      2 | 2017-02-17 00:00:00 | 2017-02-18 00:00:00 | 2017-02-17 12:00:00 | MSE         |  1152875.1096635645 | f     |  1237538.2586267272 |  1007214.3054955051
 10 |        1 |      2 | 2017-02-17 00:00:00 | 2017-02-18 00:00:00 | 2017-02-17 12:00:00 | RMSE        |  1073.7202194536362 | f     |  1113.7445456138323 |  1004.7894058546048
(10 rows)
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

You can now view both the *Drift* and *Performance* example dashboards. Be sure to enable the automatic refresh in the 
upper right corner, setting it to 10 seconds. Only a couple of data points will be visible at first.

<p><img src="_assets/grafana_dashboard_drift_1.png" alt="Drift dashboard" /></p>

You can see new datapoints appear every minute, simulating a daily processing of inputs and 
outputs for a model in production.

<p><img src="_assets/grafana_dashboard_drift_2.png" alt="Drift dashboard after several minutes" /></p>

<p><img src="_assets/grafana_dashboard_performance_1.png" alt="Performance dashboard" /></p>

After a couple of minutes you'll notice the realized performance graph not continuing. The estimated performance however
does. This is due to having only partial target values available.

<p><img src="_assets/grafana_dashboard_performance_2.png" alt="Performance dashboard" /></p>

Be sure to review the configuration behind the dashboard panels and variables to see how they are populated. 

### Stopping the demo

You can stop the spun up containers by forming `CTRL+C`. To fully remove the containers you can follow up with the 
`docker compose down` command.

## Final remarks

- Grafana also allows you to configure alert rules and notifications, check out the 
[official documentation](https://grafana.com/docs/grafana/latest/alerting/alerting-rules/) on how to set that up.
