Unofficial parser for FMI weather information
=============================================

This is unofficial parser - screen scraper - implementation for FMI website. Please check possible conditions and terms before using. This will probably break on every website update.

Installation
------------

::

  pip install fmiweather

Usage
-----

::

  from fmiweather import FmiWeather
  weather = FmiWeather()
  weather.download_content("http://ilmatieteenlaitos.fi/saa/helsinki/s%C3%B6rn%C3%A4inen")

  print weather.parse_next_days() # Parses daily forecasts
  print weather.parse_next_hours() # Parses hourly forecast
  print weather.parse_observations() # Parses observations
