async def get_dist_azim(coord_a, coord_b):
    # -*- coding: utf-8 -*-
    # !/usr/bin/env python

    # ---------------------------------------------------------------------------
    # async_great_circles.py
    # Расчет длины большого круга и начального азимута используя полное уравнение.
    # More info: http://gis-lab.info/qa/great-circles.html
    # Date created: 04.07.2010
    # Last updated: 11.08.2010
    # ---------------------------------------------------------------------------

    import math

    # pi - число pi, rad - радиус сферы (Земли)
    rad = 6372795

    # координаты двух точек
    # в радианах
    lat1 = coord_a[0] * math.pi / 180.
    lat2 = coord_b[0] * math.pi / 180.
    long1 = coord_a[1] * math.pi / 180.
    long2 = coord_b[1] * math.pi / 180.

    # косинусы и синусы широт и разницы долгот
    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    # вычисления длины большого круга
    y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = math.atan2(y, x)
    dist = ad * rad

    # вычисление начального азимута
    x = (cl1 * sl2) - (sl1 * cl2 * cdelta)
    y = sdelta * cl2
    z = math.degrees(math.atan(-y / x))

    if (x < 0):
        z = z + 180.

    z2 = (z + 180.) % 360. - 180.
    z2 = - math.radians(z2)
    anglerad2 = z2 - ((2 * math.pi) * math.floor((z2 / (2 * math.pi))))
    angledeg = (anglerad2 * 180.) / math.pi
    dist_azim = (dist, angledeg)

    return dist_azim


async def get_magdec(coord):
    import datetime
    import re
    import urllib.request
    import urllib.parse
    import xml.dom.minidom

    now = datetime.datetime.now()
    month = now.month
    latitude = coord[0]
    longitude = coord[1]

    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    params = urllib.parse.urlencode({'lat1': latitude, 'lon1': longitude, 'resultFormat': 'xml', 'startMonth': month})
    # Load XML file
    f = urllib.request.urlopen("http://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?%s" % params)
    # Process XML file into object tree and get only declination info
    dom = xml.dom.minidom.parseString(f.read())
    my_string = getText(dom.getElementsByTagName("declination")[0].childNodes)
    # At this point the string still contains some formatting, this removes it
    declination = float(re.findall(r"[-+]?\d*\.\d+|\d+", my_string)[0])
    # Output formatting and append line to declination file
    f.close()
    return declination
