import random

from jinja2 import Template
from jinja2.utils import Markup
from flask import g
from flask import current_app as app

from boutiquecommons.currency import money_format
from boutiquecommons.unit_system import METRIC, weight_format


_FILTERS = {}

_LINK_CSS = Template('<link href="{{url}}" rel="stylesheet" type="text/css">')
_IMG = Template(
    '<img src="{{ url }}" alt="{{ alt }}"'
    '{% if _class %} class="{{ _class }}"{% endif %}>')
_A = Template(
    '<a href="{{ url }}"{% if _class %} class="{{ _class }}"{% endif %}>'
    '{{ title }}</a>')


def register_sitefilter(func):
  global _FILTERS
  _FILTERS[func.func_name] = func
  return func


def get_filters():
  return _FILTERS


@register_sitefilter
def asset_url(asset):
  return "/assets/{asset}".format(asset=asset)


@register_sitefilter
def product_img_url(filename, width=None, height=None):
  if not hasattr(g, 'site') or not g.site:
    return None
  query = ''
  if width and height:
    query = "?w={}&h={}".format(width, height)

  url = g.site.permanent_url if app.config.get(
      'BOUTIQUE_PRODUCT_IMAGE_URL_ABSOLUTE', True) else ''
  url += "/productimages/{}{}".format(str(filename), query)

  return url


@register_sitefilter
def stylesheet_tag(url):
  return _LINK_CSS.render(url=url)


@register_sitefilter
def img_tag(url, alt="", _class=None):
  return _IMG.render(url=url, alt=alt, _class=_class)


@register_sitefilter
def link_to(title, url, _class=None):
  return _A.render(title=title, url=url, _class=_class)


@register_sitefilter
def limit(l, count):
  return l[:count]


@register_sitefilter
def sample(l, count):
  if len(l) < count:
    count = len(l)
  return random.sample(l, count)


@register_sitefilter
def money(amount, currency=None):
  if amount is None:
    return None
  if not currency:
    if hasattr(g, 'site') and g.site:
      currency = g.site.currency
  if not currency:
    currency = 'USD'
  return Markup(money_format(amount, currency))


@register_sitefilter
def weight(val, unit=None):
  if val is None:
    return None
  if not unit:
    if hasattr(g, 'site') and g.site:
      unit = g.site.unit_system
  if not unit:
    unit = METRIC
  return weight_format(val, unit)
