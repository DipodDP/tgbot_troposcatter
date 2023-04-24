# functions for troposphere trace analysis
import math

from matplotlib.pyplot import subplots
from numpy import correlate, pad, ones, zeros, polyval, fromfile, hstack, column_stack

from tgbot.services import async_path_profiler


def l0_calc(R, lam=0.06):
    return 20 * math.log10(4 * math.pi * R * 1000 / lam)


def lmed_calc(R, lam=0.06):
    l = 0.3
    k = (70 - 85) / (146 - 345)
    b = 70 - k * 146
    return (k * R + b) - 10 * math.log10(lam / l)


def lr_calc(R, delta):
    a = 183.6242531493953
    b = 0.30840274015885827
    k = a / R + b
    c = k * delta + 1
    if c > 0:
        return 20 / 3 * math.log2(c)
    else:
        return -20


def betta_calc(h1, h2, R, ha=2):
    return math.atan2((h2 - (R ** 2 / 12.742) - h1 - ha), (R * 1000)) * 180 / math.pi


def delta_calc(b_sum, ha=2):
    if b_sum < -0.6:
        b_sum = -0.6
    return b_sum + 0.056 * math.sqrt(ha)

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


def filt_elevation_profile(els, aa_level):
    # # filter profile via FFT
    # els_fft = sf.fft(np.pad(els,(10,10),'edge'))
    # z0 = round(els_fft.size/(2*aa_level))
    # z1 = round(els_fft.size - els_fft.size/(2*aa_level))
    # els_fft[z0:z1] = 0
    # ret_els = sf.ifft(els_fft)[10:els_fft.size-10].real
    win = ones(5) / 5
    ret_els = correlate(pad(els, (10, 10), 'edge'), win, 'same')[10:els.size + 10]

    return ret_els


def get_line_pol(p0, p1):
    pol = zeros(2)
    pol[0] = (p1[1] - p0[1]) / (p1[0] - p0[0])
    pol[1] = p0[1] - pol[0] * p0[0]
    return pol


def plot_elevation_profiles(dist, els, hca_dist_ind, pathfilename, ha):
    fig, axes = subplots(2, 1, figsize=[19.20, 5.4])

    # plot plain profile
    zero_line = zeros(dist.size)
    if els.min() < 0:
        zero_line = zero_line + els.min()

    axes[0].plot(dist, els, 'g')
    axes[0].fill_between(dist, els, zero_line, facecolor='g', alpha=0.2)
    axes[0].grid()
    els_range = els.max() - els.min()
    axes[0].axis([dist[0], dist[-1], (els.min() - els_range / 10), (els.max() + els_range / 10)])

    # plot curved profile
    zero_line_curved = zero_line - ((dist - dist[dist.size // 2]) ** 2) / 12.742
    zero_line_curved -= zero_line_curved[0]
    els_curved = els + zero_line_curved
    zero_line_curved += zero_line[0]
    axes[1].plot(dist, els_curved, 'g')
    axes[1].fill_between(dist, els_curved, zero_line_curved, facecolor='g', alpha=0.2)
    axes[1].grid()
    # els_range = els_curved.max() - els_curved.min()
    # axes[1].axis([dist[0], dist[-1], (els_curved.min() - els_range/10), (els_curved.max() + els_range/10)])

    # plot lines of view
    # get lines coeffs
    pol_1 = get_line_pol((dist[0], els_curved[0] + ha),
                         (dist[hca_dist_ind[0]], els_curved[hca_dist_ind[0]]))
    pol_2 = get_line_pol((dist[-1], els_curved[-1] + ha),
                         (dist[hca_dist_ind[1]], els_curved[hca_dist_ind[1]]))

    axes[1].plot(dist, polyval(pol_1, dist), 'k', lw=1)
    axes[1].plot(dist, polyval(pol_2, dist), 'k', lw=1)

    crosspoint = ((pol_2[1] - pol_1[1]) / (pol_1[0] - pol_2[0]),
                  (pol_2[1] - pol_1[1]) / (pol_1[0] - pol_2[0]) * pol_1[0] + pol_1[1])

    els_range = crosspoint[1] - els_curved.min()
    axes[1].axis([dist[0], dist[-1], (els_curved.min() - els_range / 10), (crosspoint[1] + els_range / 10)])

    fig.savefig(pathfilename + '.png', dpi=300, transparent=False, facecolor='mintcream')


def profile_analyzer(prof, pathfilename, bot_mode, ha=2):
    els = prof['elevation']
    dist = prof['distance']
    trace_dist = dist[-1]

    els = filt_elevation_profile(els, 2.5)

    # find left hca (horizon close angle)
    sp = els[0]
    b1_max = -360
    id1 = 0
    for i in range(dist.size):
        b1 = betta_calc(sp, els[i], dist[i], ha)
        if b1 > b1_max:
            b1_max = b1
            id1 = i

    # find right hca
    sp = els[-1]
    b2_max = -360
    id2 = 0
    for i in range(dist.size - 1, -1, -1):
        b2 = betta_calc(sp, els[i], dist[-1] - dist[i], ha)
        if b2 > b2_max:
            b2_max = b2
            id2 = i

    b_sum = b1_max + b2_max

    # calc losses
    # Lr = lr_calc(trace_dist, delta_calc(b_sum, ha))

    # if bot_mode == 1:
    arg = 1 + (b_sum * 60 / (0.4 * trace_dist + b_sum * 60) * (1 + (b_sum * 60 / (0.2 * trace_dist))))
    print(f'Argument {arg}')
    if arg > 0:
        Lr = -40 * math.log10(arg)
    else:
        Lr = 0

    # some output
    plot_elevation_profiles(dist, els, (id1, id2), pathfilename, ha)
    print(f'Trace distance = {trace_dist:.1f} km')
    print(f"Left site HCA = {b1_max:.2f}°")
    print(f"Right site HCA = {b2_max:.2f}°")
    print(f'Sum HCA = {b_sum:.2f}°')
    print(f'Lr = {Lr:.1f} dB')
    # print(f'Extra distance = {extra_dist:.1f} km')
    return trace_dist, b1_max, b2_max, b_sum, Lr


def profile_an_legacy(prof, pathfilename, bot_mode, ha=2):
    els = prof['elevation']
    dist = prof['distance']
    trace_dist = dist[-1]

    els = filt_elevation_profile(els, 2.5)

    # find left hca (horizon close angle)
    sp = els[0]
    b1_max = -360
    id1 = 0
    for i in range(dist.size):
        b1 = betta_calc(sp, els[i], dist[i], ha)
        if b1 > b1_max:
            b1_max = b1
            id1 = i

    # find right hca
    sp = els[-1]
    b2_max = -360
    id2 = 0
    for i in range(dist.size - 1, -1, -1):
        b2 = betta_calc(sp, els[i], dist[-1] - dist[i], ha)
        if b2 > b2_max:
            b2_max = b2
            id2 = i

    b_sum = b1_max + b2_max

    # calc losses
    L0 = l0_calc(trace_dist)
    Lmed = lmed_calc(trace_dist)
    Lr = lr_calc(trace_dist, delta_calc(b_sum, ha))
        
    # some output
    plot_elevation_profiles(dist, els, (id1, id2), pathfilename, ha)
    print(f'Trace distance = {trace_dist:.1f} km')
    print(f"Left site HCA = {b1_max:.2f}°")
    print(f"Right site HCA = {b2_max:.2f}°")
    print(f'Sum HCA = {b_sum:.2f}°')
    print(f'L0 = {L0:.1f} dB, Lmed = {Lmed:.1f} dB, Lr = {Lr:.1f} dB')

    return L0, Lmed, Lr, trace_dist, b1_max, b2_max, b_sum


async def load_path_coords(coord_a, coord_b, pathfilename)-> dict:
    # try to load path_coords from the file
    try:
        tmp = fromfile(pathfilename + '.path').reshape((-1, 4))
        path = {'coordinates': tmp[:, 0:2], 'distance': tmp[:, 2], 'elevation': tmp[:, 3]}
    except Exception:
        # there are problems with read file or path_coords didn't match.
        # get the new one
        path = await async_path_profiler.get_profile(coord_a, coord_b, 0.2)
        tmp = hstack((path['coordinates'],
                      column_stack((path['distance'], path['elevation']))))
        tmp.tofile(pathfilename + '.path')
    return path


async def coords_analyzis_groza(coord_a, coord_b, Lk, pathfilename, bot_mode=0, ha=2):

    print(f"!--- Groza -------- Bot mode is: {bot_mode} -----------!")
    path = load_path_coords(coord_a, coord_b, pathfilename)

    L0, Lmed, Lr, trace_dist, b1_max, b2_max, b_sum = profile_an_legacy(path, pathfilename, bot_mode, ha)
    Ltot, dL, speed = res_calc(L0, Lmed, Lr, Lk, 2)
    print(f'Total losses = {Ltot:.1f} dB')
    print(f'Delta to reference trace = {dL:.1f} dB')
    sp_pref = 'M'
    if speed < 1:
        speed *= 1024
        sp_pref = 'k'
    print(f'Estimated median speed = {speed:.1f} {sp_pref}bits/s')

    return L0, Lmed, Lr, trace_dist, b1_max, b2_max, b_sum, Ltot, dL, speed, sp_pref


async def coords_analyzis_sosnik(coord_a, coord_b, Lk, pathfilename, bot_mode=0, ha=2):

    print(f"!--- Sosnik -------- Bot mode is: {bot_mode} -----------!")
    path = await load_path_coords(coord_a, coord_b, pathfilename)

    trace_dist, b1_max, b2_max, b_sum, Lr = profile_analyzer(path, pathfilename, bot_mode, ha)
    speed, extra_dist = res_calc_sosnik(trace_dist, Lr, b_sum)
    sp_pref = 'k'
    print(f'Extra distance = {extra_dist:.1f} km')
    print(f'Estimated median speed = {speed:.1f} {sp_pref}bits/s')

    return trace_dist, extra_dist, b1_max, b2_max, b_sum, Lr, speed, sp_pref

