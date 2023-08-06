from __future__ import division, print_function, absolute_import, unicode_literals

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def double_array(r):
    return np.concatenate((r, r))


def narrow_periodgram(time, amplitude, center_frequency, frequency_width,
                      num=1000):
    f_min = center_frequency - frequency_width / 2
    f_max = center_frequency + frequency_width / 2
    frequencies = np.linspace(f_min, f_max, num=num)
    pgram = signal.lombscargle(time, amplitude, 2 * np.pi * frequencies)
    return (frequencies, pgram)


def mark_at(freqs, labels, ax=None, voffset=0):
    if ax is None:
        ax = plt.axes()

    for freq, label in zip(freqs, labels):
        line, = ax.plot([freq, freq], ax.get_ylim(), ':')
        ax.text(1.0 * freq, (0.9 + voffset) * ax.get_ylim()[1], label,
                color=line.get_color(), horizontalalignment='center',
                backgroundcolor='w', size='large')


def plot_near_harmonics(time, amplitude, fundamental_freq,
                        max_harmonic=20, nplots_per_row=5, freq_width=0.1,
                        mark_harmonics=None):
    for harm in range(max_harmonic):
        if (harm % nplots_per_row) == 0:
            fig, axs = plt.subplots(ncols=nplots_per_row, sharey=True)

        fm = mark_harmonics or False

        axis_index = harm % nplots_per_row
        ax = axs[axis_index]
        if axis_index == int(nplots_per_row / 2):
            ax.set_title('Normalized peridograms near harmonics')
        cen_freq = (harm + 1) * fundamental_freq
        f, p = narrow_periodgram(time, amplitude, cen_freq, freq_width)
        cen_freq_label = '{}$f_0$'.format(harm + 1)
        ax.plot(f - cen_freq, p / p.max(),
                label=cen_freq_label + ' max is {:5f}'.format(p.max()))
        if fm:
            mark_freq = []
            mark_label = []
            for i in [-3, -2, -1, 1, 2, 3]:
                mark_freq.append(i * fm)
                mark_label.append('{}$f_m$'.format(i))
            mark_at(mark_freq, mark_label, ax=ax)
        mark_at([0], [cen_freq_label], ax=ax)
        ax.set_xlabel('$f-$' + cen_freq_label)
        ax.legend(loc='lower center')
        plt.subplots_adjust(wspace=0)


def plot_data_and_model(phase, data, model=None):
    double_phase = np.concatenate((phase, phase + 1))
    plt.plot(double_phase, -double_array(data), '.', color='b', label='data')
    if model is None:
        return

    ordered_phase = double_phase.argsort()
    sorted_model = (double_array(model))[ordered_phase]
    plt.plot(double_phase[ordered_phase], -sorted_model,
             color='g', label='model', linewidth=3)
    plt.xlabel('phase')
    plt.ylabel(u'-$\Delta R$')
    plt.legend()


def plot_data_model_with_fanciness(nights, phase, target_mag, dates,
                                   model=None,
                                   highlight_nights=None,
                                   nights_to_include=None,
                                   highlight_model=False):
    unique_nights = np.unique(nights)

    line_format = 'None'
    colors = ['b', 'r', 'c', 'm', 'y']
    markers = ['v', '^', 'd', 's']

    nights_to_include = nights_to_include or unique_nights

    #nights_to_include =[1, 4]
    highlight_nights = highlight_nights or unique_nights
    linew = 3
    for idx, night in enumerate(unique_nights):
        this_night = (nights == night)

        marker_format = markers[idx % len(markers)]

        if night in highlight_nights:
            alpha = 1.0
        else:
            alpha = 0.1

        legend_label = 'night ' + str(night)
        this_color = colors[idx % (len(colors))]

        if night in nights_to_include:
            plt.plot(np.concatenate((phase[this_night], phase[this_night] + 1)),
                     - double_array(target_mag[this_night]),
                     marker=marker_format, linestyle=line_format,
                     markersize=6.0,
                     color=this_color,
                     alpha=alpha,
                     label=legend_label)

            if model is None:
                continue

            p = phase[this_night].argsort()

            gap_at = (phase[this_night][p] - np.roll(phase[this_night][p], 1))
            gap_at = (gap_at > 0.1)

            masked_model = np.ma.masked_where(gap_at, model(dates[this_night][p]),
                                              copy=True)
            if highlight_model:
                model_alpha = 1.0
            else:
                model_alpha = alpha
            plt.plot(phase[this_night][p],
                     - masked_model,
                     color=this_color,
                     linewidth=linew, alpha=model_alpha)
            plt.plot(phase[this_night][p] + 1,
                     - masked_model,
                     color=this_color,
                     linewidth=linew, alpha=model_alpha)

    sze = 22

    #plt.legend(bbox_to_anchor=(0, 1), loc=2, ncol=3, borderaxespad=0.)
    #plt.title('Period = ' + str(p0) + ' days', size = sze)
    plt.xlabel('Phase', size=sze)
    plt.ylabel(r'$-dm$', size=sze)


def plot_model_over_time(model, primary_period, secondary_period,
                         points_primary=100,
                         points_secondary=5,
                         primary_epoch=0.):
    """
    Plot a light curve with changes over two different time scales
    """
    one_period = np.linspace(primary_epoch,
                             primary_epoch + primary_period,
                             num=points_primary)
    secondary_start_times = np.linspace(0, secondary_period,
                                        num=points_secondary)
    all_times = [t + one_period for t in secondary_start_times]
    for i, time in enumerate(all_times):
        phase = (time - primary_epoch) / primary_period
        phase -= np.int64((time - primary_epoch) / primary_period)
        sort_index = np.argsort(phase)
        this_label = '{:5.4f} secondary periods'.format(i / points_secondary)
        plt.plot(phase[sort_index], -model(time[sort_index]),
                 label=this_label)
        plt.xlabel('Phase')
        plt.ylabel('- Magnitude')
