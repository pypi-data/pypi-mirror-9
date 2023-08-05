#!/usr/bin/env python 

import math

def in_radius(lat0, lon0, lat1, lon1, rad):
	d = haversine(lat0, lon0, lat1, lon1)
	if d <= rad:
		return True
	return False

def haversine(lat0,lon0,lat1,lon1, earth_radius = 3961):
	delta_lon = math.radians(lon1) - math.radians(lon0)
	delta_lat = math.radians(lat1) - math.radians(lat0)
	a = math.pow(math.sin(delta_lat/2),2) + math.cos(lat0) * math.cos(lat1) * math.pow(math.sin(delta_lon/2),2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	d = earth_radius * c #  6373km for km result
	return d
