# functions for troposphere trace profile analysis and Lr calculation
import math

from matplotlib.pyplot import subplots
from numpy import correlate, pad, ones, zeros, polyval


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


def get_line_pol(p0, p1):
    pol = zeros(2)
    pol[0] = (p1[1] - p0[1]) / (p1[0] - p0[0])
    pol[1] = p0[1] - pol[0] * p0[0]
    return pol


def plot_elevation_profiles(dist, els, hca_dist_ind, pathfilename, ha1=2, ha2=2):
    fig, axes = subplots(2, 1, figsize=[19.20, 5.4])

    # plot plain profile
    zero_line = zeros(dist.size)
    if els.min() < 0:
        zero_line = zero_line + els.min()

    axes[0].plot(dist, els, 'g')
    axes[0].fill_between(dist, els, zero_line, facecolor='g', alpha=0.2)
    axes[0].grid()
    els_range = els.max() - els.min()
    axes[0].axis([dist[0], dist[-1], (els.min() - els_range / 10),
                 (els.max() + els_range / 10)])

    # plot curved profile
    zero_line_curved = zero_line - \
        ((dist - dist[dist.size // 2]) ** 2) / 12.742
    zero_line_curved -= zero_line_curved[0]
    els_curved = els + zero_line_curved
    zero_line_curved += zero_line[0]
    axes[1].plot(dist, els_curved, 'g')
    axes[1].fill_between(dist, els_curved, zero_line_curved,
                         facecolor='g', alpha=0.2)
    axes[1].grid()
    # els_range = els_curved.max() - els_curved.min()
    # axes[1].axis([dist[0], dist[-1], (els_curved.min() - els_range/10),
    # (els_curved.max() + els_range/10)])

    # plot lines of view
    # get lines coeffs
    pol_1 = get_line_pol((dist[0], els_curved[0] + ha1),
                         (dist[hca_dist_ind[0]], els_curved[hca_dist_ind[0]]))
    pol_2 = get_line_pol((dist[-1], els_curved[-1] + ha2),
                         (dist[hca_dist_ind[1]], els_curved[hca_dist_ind[1]]))

    axes[1].plot(dist, polyval(pol_1, dist), 'k', lw=1)
    axes[1].plot(dist, polyval(pol_2, dist), 'k', lw=1)
    crosspoint = ((pol_2[1] - pol_1[1]) / (pol_1[0] - pol_2[0]),
                  (pol_2[1] - pol_1[1]) / (pol_1[0] - pol_2[0])
                  * pol_1[0] + pol_1[1])

    els_range = crosspoint[1] - els_curved.min()
    axes[1].axis([dist[0], dist[-1], (els_curved.min() -
                 els_range / 10), (crosspoint[1] + els_range / 10)])

    fig.savefig(pathfilename + '.png', dpi=300,
                transparent=False, facecolor='mintcream')


def betta_calc(h1, h2, R, ha=2):
    return math.atan2((h2 - (R ** 2 / 12.742) - h1 - ha),
                      (R * 1000)) * 180 / math.pi


def delta_calc(b_sum, ha1=2, ha2=2):
    if b_sum < -0.6:
        b_sum = -0.6
    return b_sum + 0.056 * math.sqrt((ha1 + ha2)/2)


def filt_elevation_profile(els, aa_level):
    # # filter profile via FFT
    # els_fft = sf.fft(np.pad(els,(10,10),'edge'))
    # z0 = round(els_fft.size/(2*aa_level))
    # z1 = round(els_fft.size - els_fft.size/(2*aa_level))
    # els_fft[z0:z1] = 0
    # ret_els = sf.ifft(els_fft)[10:els_fft.size-10].real
    win = ones(5) / 5
    ret_els = correlate(pad(els, (10, 10), 'edge'),
                        win, 'same')[10:els.size + 10]

    return ret_els


def hca_calc(prof, pathfilename, ha1=2, ha2=2):

    print(f'Antenas heigths {ha1}, {ha2}')

    els = prof['elevation']
    dist = prof['distance']
    trace_dist = dist[-1]

    els = filt_elevation_profile(els, 2.5)

    # find left hca (horizon close angle)
    sp = els[0]
    b1_max = -360
    id1 = 0
    for i in range(dist.size):
        b1 = betta_calc(sp, els[i], dist[i], ha1)
        if b1 > b1_max:
            b1_max = b1
            id1 = i

    # find right hca
    sp = els[-1]
    b2_max = -360
    id2 = 0
    for i in range(dist.size - 1, -1, -1):
        b2 = betta_calc(sp, els[i], dist[-1] - dist[i], ha2)
        if b2 > b2_max:
            b2_max = b2
            id2 = i

    b_sum = b1_max + b2_max

    plot_elevation_profiles(dist, els, (id1, id2), pathfilename, ha1=ha1, ha2=ha2)

    return trace_dist, b1_max, b2_max, b_sum


def profile_analyzer(prof, pathfilename, ha1=2, ha2=2):
    trace_dist, b1_max, b2_max, b_sum = hca_calc(prof, pathfilename, ha1=ha1, ha2=ha2)

    # calc losses
    # Lr = lr_calc(trace_dist, delta_calc(b_sum, ha))

    arg = 1 + (b_sum * 60 / (0.4 * trace_dist + b_sum * 60) *
               (1 + (b_sum * 60 / (0.2 * trace_dist))))
    print(f'Argument {arg}')
    if arg > 0:
        Lr = -40 * math.log10(arg)
    else:
        Lr = 0

    # some output
    print(f'Trace distance = {trace_dist:.1f} km')
    print(f"Left site HCA = {b1_max:.2f}°")
    print(f"Right site HCA = {b2_max:.2f}°")
    print(f'Sum HCA = {b_sum:.2f}°')
    print(f'Lr = {Lr:.1f} dB')
    # print(f'Extra distance = {extra_dist:.1f} km')
    return trace_dist, b1_max, b2_max, b_sum, Lr


def profile_an_legacy(prof, pathfilename, ha1=2, ha2=2):
    print(prof)
    trace_dist, b1_max, b2_max, b_sum = hca_calc(prof, pathfilename, ha1=ha1, ha2=ha2)

    # calc losses
    L0 = l0_calc(trace_dist)
    Lmed = lmed_calc(trace_dist)
    Lr = lr_calc(trace_dist, delta_calc(b_sum, ha1=ha1, ha2=ha2))

    # some output
    print(f'Trace distance = {trace_dist:.1f} km')
    print(f"Left site HCA = {b1_max:.2f}°")
    print(f"Right site HCA = {b2_max:.2f}°")
    print(f'Sum HCA = {b_sum:.2f}°')
    print(f'L0 = {L0:.1f} dB, Lmed = {Lmed:.1f} dB, Lr = {Lr:.1f} dB')

    return L0, Lmed, Lr, trace_dist, b1_max, b2_max, b_sum
