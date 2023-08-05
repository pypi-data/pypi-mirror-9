_CURRENCY_FORMAT = {
  'html': {
    'USD': '${amount}',
    'EUR': '&euro;{amount}',
    'GBP': '&pound;{amount}',
    'CHF': '{amount} CHF',
    'RON': '{amount} lei RON',
  }
}


_CURRENCY_FORMAT_DEFAULT = {
  'html': '{amount} {currency}'
}

def money_format(amount, currency='USD', format='html'):
  try:
    float(amount)
  except ValueError:
    return "N/A"

  fmt = _CURRENCY_FORMAT.get(format, {}).get(currency, None)
  if fmt is None:
    fmt = _CURRENCY_FORMAT_DEFAULT.get(format, None)
  assert fmt

  amount_str = '{:,.2f}'.format(amount)
  return fmt.format(amount=amount_str, currency=currency)
  