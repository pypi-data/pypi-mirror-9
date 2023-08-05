from functools import wraps
from errors import ParameterError

def check_required(f):
  @wraps(f)
  def wrapper(instance, data):
    required = globals()[f.__name__]()
    for param in required:
      if param not in data:
        raise ParameterError(param)
    return f(instance, data)

  return wrapper

def optimize():
  return ['file_url', 'file_name', 'geocode', 'stop_name', 'date_starting',
    'warehouse', 'num_drivers', 'num_avg_service_time', 'float_fuel_cost',
    'float_driver_wage', 'float_mpg']
