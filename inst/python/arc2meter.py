"""
Converter arc seconds to meter and vice versa.

Earth circumference around Equator is 40,075,017 meter
1 arc second at equatorial sea level = 1855.325m/60 = 30.922m

Earth circumference around Poles is 40,007,863 meter
1 arc second latitude = 1852.216m/60 = 30.87m

Formula for longitude: meters = arcsec * cos(degree latitude) * 30.922m
(conversion for latitude stays constant: arcsec * 30.87m)
"""

import numpy as np

def calc_arc2meter(arcsec, latitude):
	"""
	Calculate arc seconds to meter

	Input
	-----
	arcsec: float, arcsec
	latitude: float, latitude

	Return
	------
	(meters Long, meters Lat)
	"""
	meter_lng = arcsec * np.cos(latitude * np.pi/180) * 30.922
	meter_lat = arcsec * 30.87
	return (meter_lng, meter_lat)

def calc_meter2arc(meter, latitude):
	"""
	Calculate meter to arc seconds

	Input
	-----
	meter: float, meter
	latitude: float, latitude

	Return
	------
	(arcsec Long, arcsec Lat)
	"""
	arcsec_lng = meter / np.cos(latitude * np.pi/180) / 30.922
	arcsec_lat = meter / 30.87
	return (arcsec_lng, arcsec_lat)