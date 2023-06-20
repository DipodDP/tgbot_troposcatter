import requests
import json
import time

import numpy as np
from environs import Env
from progress.bar import Bar


class APIException(Exception):
    """Can't get API data"""


BLOCK_SIZE = 256


async def elevations_api_request(coord_vect_block: list):
    url = "https://maptoolkit.p.rapidapi.com/elevation"

    env = Env()
    env.read_env(".env")
    headers = {
        "X-RapidAPI-Host": "maptoolkit.p.rapidapi.com",
        "X-RapidAPI-Key": env.str('ELEVATION_API_KEY')
    }
    querystring = {"points": '['}

    for coord in coord_vect_block:
        # getting back W and S coords from coord vector
        if coord[0] > 180:
            coord[0] = coord[0] - 360
        if coord[1] > 180:
            coord[1] = coord[1] - 360

        querystring["points"] += f'[{coord[0]:.6f},{coord[1]:.6f}],'

    querystring["points"] = querystring["points"][:-1] + ']'
    response = requests.request("GET", url, headers=headers, params=querystring)
    resp = json.loads(response.text)

    if response.status_code in [200, 301, 302]:
        resp_data = resp
        return resp_data

    else:
        raise APIException(f'{response.status_code} - {": ".join(list(resp.values()))}')


async def get_elevations(coord_vect):

    assert coord_vect.shape[0] % BLOCK_SIZE == 0, f'support only {BLOCK_SIZE} wide requests'

    blocks_num = coord_vect.shape[0] // BLOCK_SIZE
    bar = Bar('Retrieving data', max=blocks_num)
    els = []

    for n in range(blocks_num):
        coord_vect_block = coord_vect[n * BLOCK_SIZE:(n + 1) * BLOCK_SIZE]
        els_block = await elevations_api_request(coord_vect_block)
        els = np.append(els, els_block)

        bar.goto(n + 1)
        time.sleep(1)

    bar.finish()

    return els


async def get_angle(coord_a, coord_b):

    a = (coord_a[0] * np.pi / 180.0, coord_a[1] * np.pi / 180.0)
    b = (coord_b[0] * np.pi / 180.0, coord_b[1] * np.pi / 180.0)
    return np.arccos(np.sin(a[0]) * np.sin(b[0]) +
                     np.cos(a[0]) * np.cos(b[0]) * np.cos(b[1] - a[1]))


async def get_distance(coord_a, coord_b):
    return 6371.21 * await get_angle(coord_a, coord_b)


async def linspace_coord(coord_a, coord_b, resolution=0.5):
    # Handling S and W coords for coord vector
    for i in range(2):
        if coord_a[i] < 0 and abs(coord_a[i] + 360 - coord_b[i]) < 180:
            coord_a[i] = coord_a[i] + 360
    for i in range(2):
        if coord_b[i] < 0 and abs(coord_a[i] + 360 - coord_b[i]) < 180:
            coord_b[i] = coord_b[i] + 360
    dist = await get_distance(coord_a, coord_b)

    points_num = (np.ceil(dist / (BLOCK_SIZE * resolution)) * BLOCK_SIZE).astype(int)
    lat_vect = np.linspace(coord_a[0], coord_b[0], points_num)
    lon_vect = np.linspace(coord_a[1], coord_b[1], points_num)
    return np.column_stack((lat_vect, lon_vect))


async def get_profile(coord_a, coord_b, resolution=0.5):
    coord_v = await linspace_coord(coord_a, coord_b, resolution)
    points_num = coord_v.shape[0]

    profile = {'distance': np.zeros(points_num), 'elevation': np.zeros(points_num),
               'coordinates': coord_v}

    # calc distance vector
    for i in range(points_num):
        profile['distance'][i] = await get_distance(coord_v[0], coord_v[i])
    profile['distance'][0] = 0.0
    profile['elevation'] = await get_elevations(coord_v)

    return profile


def coord_min2dec(degree, minutes, seconds=0):
    return degree + minutes / 60 + seconds / 3600
