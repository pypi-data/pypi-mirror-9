# Foxtrot Python Client Library

This is the Python client library for interacting with the Foxtrot API. The only endpoint currently exposed is the route optimization endpoint (`Foxtrot.optimize`).

In order to make requests, you need a valid API key. Your API key can be found at the bottom of any page in the [Foxtrot web app](http://app.foxtrot.io/).

## Installation

`pip install foxtrot-client`

## Usage

```python
data = {
  "file_url": "https://www.domain.io/your_file.xlsx",
  "file_name": "your_file.xlsx",
  "geocode": "false",
  "stop_name": "Customer",
  "lat": "Lat",
  "lng": "Long",
  "load": "Load",
  "service_time": "Service Time",
  "time_window": "Time Window",
  "extra_info": "Contact Info",
  "date_starting": "1407712069593",
  "warehouse": "77 Massachusetts Ave, Cambridge MA",
  "num_drivers": 1,
  "num_avg_service_time": 10,
  "float_fuel_cost": 3.56,
  "float_driver_wage": 6.01,
  "float_mpg": 8.32
}

api_key = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

from foxtrot import Foxtrot
fox = Foxtrot(api_key)

resp = fox.optimize(data).poll_and_block()
result = resp.get_result()
```
