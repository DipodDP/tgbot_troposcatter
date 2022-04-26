import http.client
import json
import time

from numpy import zeros
from progress.bar import Bar

BLOCK_SIZE = 256


async def get_elevations(coord_vect):
    assert coord_vect.shape[0] % BLOCK_SIZE == 0, f'support only {BLOCK_SIZE} wide requests'

    conn = http.client.HTTPSConnection("geo-services-by-mvpc-com.p.rapidapi.com")
    headers = {
        'x-rapidapi-host': "geo-services-by-mvpc-com.p.rapidapi.com",
        'x-rapidapi-key': "16e3b027e2mshb4312fe84fe66e2p1f76b7jsn7d81aa678c1b"
    }

    blocks_num = coord_vect.shape[0] // BLOCK_SIZE;
    els = zeros(BLOCK_SIZE * blocks_num)
    bar = Bar('Retreiving data', max=blocks_num)

    for n in range(blocks_num):
        req_str = "/elevation?locations="
        for c in coord_vect[n * BLOCK_SIZE: (n + 1) * BLOCK_SIZE]:
            req_str += f'{c[0]:.6f},{c[1]:.6f}|'
        req_str = req_str[:-1];

        conn.request("GET", req_str, headers=headers)
        res = conn.getresponse()
        resp = res.read()
        resp_data = json.loads(resp);

        for i in range(BLOCK_SIZE):
            els[n * BLOCK_SIZE + i] = resp_data['data'][i]['elevation']

        bar.goto(n + 1)
        time.sleep(1)

    bar.finish()

    return els


async def get_angle(coord_a, coord_b):
    a = (coord_a[0] * np.pi / 180.0, coord_a[1] * np.pi / 180.0);
    b = (coord_b[0] * np.pi / 180.0, coord_b[1] * np.pi / 180.0);
    return np.arccos(np.sin(a[0]) * np.sin(b[0]) +
                     np.cos(a[0]) * np.cos(b[0]) * np.cos(b[1] - a[1]))


async def get_distance(coord_a, coord_b):
    return 6371.21 * await get_angle(coord_a, coord_b)


async def linspace_coord(coord_a, coord_b, resolution=0.5):
    dist = await get_distance(coord_a, coord_b);
    points_num = (np.ceil(dist / (BLOCK_SIZE * resolution)) * BLOCK_SIZE).astype(np.int)
    lat_vect = np.linspace(coord_a[0], coord_b[0], points_num)
    lon_vect = np.linspace(coord_a[1], coord_b[1], points_num)
    return np.column_stack((lat_vect, lon_vect))


async def get_profile(coord_a, coord_b, resolution=0.5):
    coord_v = await linspace_coord(coord_a, coord_b, resolution)
    points_num = coord_v.shape[0];

    profile = {'distance': np.zeros(points_num), 'elevation': np.zeros(points_num),
               'coordinates': coord_v}

    # calc distance vector
    for i in range(points_num):
        profile['distance'][i] = await get_distance(coord_v[0], coord_v[i])

    profile['elevation'] = await get_elevations(coord_v)

    return profile


def coord_min2dec(degree, minutes, seconds):
    return degree + minutes / 60 + seconds / 3600
