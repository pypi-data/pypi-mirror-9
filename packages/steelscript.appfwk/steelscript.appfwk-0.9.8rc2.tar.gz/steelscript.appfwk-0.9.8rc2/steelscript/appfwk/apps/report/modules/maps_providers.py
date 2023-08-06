# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


def google_postprocess(data):
    """Translate data for use in google_maps API."""
    circles = []
    for c in data['circles']:
        circle = {
            'strokeColor': '#FF0000',
            'strokeOpacity': 0.8,
            'strokeWeight': 2,
            'fillColor': '#FF0000',
            'fillOpacity': 0.35,
            'center': [c.lat, c.long],
            'size': c.size,
            'title': c.title,
            'value': c.value,
            'units': c.units,
            'formatter': c.formatter
        }
        circles.append(circle)
    data['circles'] = circles

    return data


def openstreetmaps_postprocess(data):
    """Translate data for use in Open Street Maps API."""
    circles = []
    for c in data['circles']:
        circle = {
            'center': [c.lat, c.long],
            'stroke': True,
            'color': '#FF0000',
            'weight': 2,
            'opacity': 0.8,
            'fillColor': '#FF0000',
            'fillOpacity': 0.35,
            'clickable': False,

            'radius': c.size,
            'title': c.title,

            'value': c.value,
            'units': c.units,
            'formatter': c.formatter
        }
        circles.append(circle)
    data['circles'] = circles

    return data
