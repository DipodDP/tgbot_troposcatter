# functions for troposphere trace analysis
import asyncio

from numpy import fromfile, hstack, column_stack

from trace_calc.profile_analysis import profile_an_legacy, profile_analyzer, get_profile


def res_calc(l0, lmed, lp, lk, ld):
    """ Input: L0, Lmed, Lp, Lk, Ld
    Return L, Delta_L, and speed in tuple """
    l = l0 + lmed + lp + lk + ld
    # dl = l - 229.6
    # sp = 4 * 10 ** (-dl / 10)
    dl = l - 233.8
    if dl > -1.66:
        sp = 15.2 * 10 ** (-dl / 10)
    elif dl < -1.66 - 5:
        sp = 44.6
    else:
        sp = 22.3

    return l, dl, sp


def res_calc_sosnik(trace_dist, Lr, b_sum):
    """ Input: trace distance, Lr
    Return speed, extra distance in tuple """

    # extra_dist = -Lr * 3

    if b_sum > 0:
        extra_dist = 148 * b_sum
    else:
        extra_dist = 0

    equal_dist = trace_dist + extra_dist

    if trace_dist < 40 and equal_dist < 90 and Lr >= -35:
        speed = 2048
        # extra_dist = 0
    elif Lr < -45:
        speed = 0
    elif equal_dist < 120:
        speed = 512
    elif equal_dist < 140:
        speed = 256
    elif equal_dist < 210:
        speed = 64
    else:
        speed = 0

    return speed, extra_dist


async def load_path_coords(coord_a, coord_b, pathfilename) -> dict:
    # try to load path_coords from the file
    try:
        tmp = fromfile(pathfilename + '.path').reshape((-1, 4))
        path = {'coordinates': tmp[:, 0:2],
                'distance': tmp[:, 2], 'elevation': tmp[:, 3]}
    except Exception:
        # there are problems with read file or path_coords didn't match.
        # get the new one
        path = await get_profile(coord_a, coord_b, 0.2)
        tmp = hstack((path['coordinates'],
                      column_stack((path['distance'], path['elevation']))))
        tmp.tofile(pathfilename + '.path')
    return path


async def coords_analyzis_groza(coord_a, coord_b, Lk, pathfilename,
                                bot_mode=0, ha1=2, ha2=2):

    print(f"!--- Groza -------- Bot mode is: {bot_mode} -----------!")
    path = await load_path_coords(coord_a, coord_b, pathfilename)

    L0, Lmed, Lr, trace_dist, b1_max, b2_max, b_sum = profile_an_legacy(
        path, pathfilename, ha1=ha1, ha2=ha2)
    Ltot, dL, speed = res_calc(L0, Lmed, Lr, Lk, 2)
    print(f'Total losses = {Ltot:.1f} dB')
    print(f'Delta to reference trace = {dL:.1f} dB')
    sp_pref = 'M'
    if speed < 1:
        speed *= 1024
        sp_pref = 'k'
    print(f'Estimated median speed = {speed:.1f} {sp_pref}bits/s')

    return L0, Lmed, Lr, trace_dist, b1_max, b2_max, b_sum,\
        Ltot, dL, speed, sp_pref


async def coords_analyzis_sosnik(coord_a, coord_b, Lk,
                                 pathfilename, bot_mode=0, ha1=2, ha2=2):
    print(f"!--- Sosnik -------- Bot mode is: {bot_mode} -----------!")
    path = await load_path_coords(coord_a, coord_b, pathfilename)

    trace_dist, b1_max, b2_max, b_sum, Lr = profile_analyzer(
        path, pathfilename, ha1=ha1, ha2=ha2)
    speed, extra_dist = res_calc_sosnik(trace_dist, Lr, b_sum)
    sp_pref = 'k'
    print(f'Extra distance = {extra_dist:.1f} km')
    print(f'Estimated median speed = {speed:.1f} {sp_pref}bits/s')

    return trace_dist, extra_dist, b1_max, b2_max, b_sum, Lr, speed, sp_pref


async def main():
    stored_filename = input('Enter stored file name: ')
    try:
        with open(f'sites coords/{stored_filename}.path', 'r') as f:
            f.close()
        coord_a, coord_b = ([0.0, 0.0], [0.0, 0.0])

    except FileNotFoundError:
        coord_a1, coord_a2 = input(
            'Input site "A" coorinates (format: -123.456 12,345): '
        ).split()
        coord_b1, coord_b2 = input(
            'Input site "B" coorinates (format: -123.456 12,345): '
        ).split()

        coord_a, coord_b = ([int(coord_a1), int(coord_a2)],
                            [int(coord_b1), int(coord_b2)])

    ha1 = int(input('Enter antenna 1 height: '))
    ha2 = int(input('Enter antenna 2 height: '))
    await coords_analyzis_sosnik(coord_a, coord_b, 0,
                                 f'./sites coords/{stored_filename}',
                                 ha1=ha1, ha2=ha2)

if __name__ == "__main__":

    asyncio.run(main())
