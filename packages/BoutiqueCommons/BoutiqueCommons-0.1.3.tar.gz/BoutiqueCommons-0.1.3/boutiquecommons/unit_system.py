METRIC = 'metric'
IMPERIAL = 'imperial'


UNIT_SYSTEM_CHOICES = [
  (METRIC, 'Metric (kg)'),
  (IMPERIAL, 'Imperial (lb)'),
]

_WEIGHT_SYMBOL = {
  METRIC: 'kg',
  IMPERIAL: 'lb',
}


_WEIGHT_FORMAT = {
  METRIC: '{val} kg',
  IMPERIAL: '{val} lb',
}


def weight_symbol(unit=METRIC):
  return _WEIGHT_SYMBOL.get(unit)


def weight_format(val, unit=METRIC):
  fmt = _WEIGHT_FORMAT.get(unit)
  val_str = '{:,.2f}'.format(val)

  return fmt.format(val=val_str)
