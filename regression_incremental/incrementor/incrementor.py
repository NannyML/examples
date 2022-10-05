import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

import pandas as pd


def run():
    # retrieve and set variables
    data_dir = Path(os.environ.get('NML_DATA_DIR', default='/data'))
    out_dir = Path(os.environ.get('NML_OUT_DIR', default=data_dir / 'incremental'))
    timestamp_column_name = os.environ.get('NML_TIMESTAMP_COLUMN_NAME', default='timestamp')
    glob_pattern = os.environ.get('NML_GLOB_PATTERN', default='*analysis*.csv')
    start_datetime = (
        datetime.now() if os.environ.get('NML_START_DATETIME', default=None) is None
        else datetime.strptime(os.environ.get('NML_START_DATETIME'), '%Y-%m-%d %H-%M-%S')
    )
    date_offset = os.environ.get('NML_OFFSET', default='D')
    delta = timedelta(minutes=int(os.environ.get('NML_DELTA_MINUTES', default=1)))

    # check if input data dir exists, else exit.
    if not data_dir.exists():
        print(f"data directory '{str(data_dir)} does not exist'")
        sys.exit(1)

    # ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)

    for data_file in list_input_data(data_dir, glob_pattern=glob_pattern):
        transform(data_file, out_dir, timestamp_column_name, start_datetime, date_offset, delta)

    print('done')


def list_input_data(data_dir: Path, glob_pattern: str) -> List[Path]:
    return list(data_dir.glob(glob_pattern))


def transform(data_file: Path, out_dir: Path, timestamp_column_name: str, start_datetime: datetime,
              date_offset: str, delta: timedelta):
    data = pd.DataFrame()
    if data_file.suffix == '.csv':
        data = pd.read_csv(data_file)
    elif data_file.suffix == '.pq':
        data = pd.read_parquet(data_file)
    grouped_data = data.groupby(pd.to_datetime(data[timestamp_column_name]).dt.to_period(date_offset))
    for index, period in enumerate(grouped_data.groups.keys()):

        incremental_datetime = start_datetime + (index + 0) * delta

        incremental_out_dir = out_dir / datetime.strftime(incremental_datetime, '%Y/%m/%d/%H/%M')
        incremental_out_dir.mkdir(parents=True, exist_ok=True)

        if data_file.suffix == '.csv':
            grouped_data.get_group(period).to_csv(incremental_out_dir / data_file.name)
        elif data_file.suffix == '.pq':
            grouped_data.get_group(period).to_parquet(incremental_out_dir / data_file.name)


if __name__ == "__main__":
    run()
