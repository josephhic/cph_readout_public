import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

plt.rcParams['axes.facecolor']='white'
plt.rcParams['savefig.facecolor']='white'

def plot_histogram(I_meas, integration_steps, ax=None):
    if ax is None:
        fig,ax = plt.subplots()
    ax.hist(np.average(I_meas[:,:,:integration_steps],axis=2).flatten()*1e3,bins = 100)
    ax.set_xlabel('I_meas [mV]')
    ax.set_ylabel('Counts #')


def monoExp(x, m, tau, b):
    return m * np.exp(-x/tau) + b

def fit_T1(data):
    chunk_size = 76 #ns
    x_data = np.arange(1,len(data)+1)*chunk_size*1e-9
    p0 = (x_data[0]-x_data[-1], 3e-6,x_data[-1]) # start with values near those we expect
    params, cv = curve_fit(monoExp, x_data, data, p0)
    m, tau, b = params
    return m, tau, b, x_data

def fit_and_plot(data, index):
    data_averaged = np.average(np.average(data[:,:,:index],axis=1),axis=0)
    m, tau, b, x_data = fit_T1(data_averaged)

    squaredDiffs = np.square(data_averaged - monoExp(x_data, m, tau, b))
    squaredDiffsFromMean = np.square(data_averaged - np.mean(data_averaged))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    fig, ax = plt.subplots()
    ax.plot(x_data*1e6,data_averaged*1e6, 'k',label = 'data')
    ax.plot(x_data*1e6, monoExp(x_data, m, tau, b)*1e6, 'r--', label=f"fit V$_H$ = ({m*1e6:.1f} exp(-t/{tau*1e6:.2f} $\mu$s) + {b*1e6:.0f}) $\mu$V")


    ax.set_xlabel(f' sampling time ($\mu$s) ', size = 12)
    ax.set_ylabel(f' I_meas ($\mu$V)', size = 12)
    #plt.title( f"T7_3 FF1B run ID#{ds.captured_run_id} - det_value ={exchange_value_mV:.1f} mV ", size = 10)
    # ax.set_title( f"T7_3 FF1B_{label}", size = 10)
    # ax.tick_params(labelsize= 12)
    # ax.tight_layout()
    # plt.locator_params(axis="y", nbins=6)
    # plt.locator_params(axis="x", nbins=6)
    ax.grid()
    fig.legend()


