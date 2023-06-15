import numpy as np
from scipy import signal
import xarray as xr
from scipy.fft import fft, fftfreq


def libera_get_ceres_frequency_response(frequencies: list):
    """
    This from Dave Harber creates a theoretical transfer function of the CERES detectors from a list of desired
    input frequencies

    Parameters
    ----------
    frequencies: list
        This is expected similar to a numpy.arange list giving the range of frequencies to be evaluated

    Returns
    -------
    A list of the same shape as the given frequencies of the theoretical output transfer function from the CERES
    instruments
    """
    """ Building a Ceres response function from frequency list """
    s = np.zeros(len(frequencies)) + 1j*2*np.pi*frequencies

    # Scale for 22 Hz filter
    sp = s/65.390841289544042

    # Create bessel filter from Wikipedia https://en.wikipedia.org/wiki/Bessel_filter
    tf_bessel = 105/(sp**4 + 10*sp**3 + 45*sp**2 + 105*sp +105)

    # Ceres time constant
    tau = 0.00824
    tf_bolometer = 1/(1+s*tau)

    return tf_bolometer*tf_bessel


def libera_detector_add_detector_power(libera_detector_data):
    """
    Calculate and add the power in microwatts of the libera detector to an existing xarray Dataset
    Parameters
    ----------
    libera_detector_data: xarray.Dataset
        This is the full detector dataset converted from Dave's IDL code from Labview byte data.

    Returns
    -------
    None: Output is added to the original Dataset

    """
    # Lead resistance is another piece that will be a measured values
    r_heater = 6245  # Temp (of detector) dependent (maybe linear fit)
    r_top = 6807  # Should be constant per detector
    v_ref = 3.599  # constant per detector
    max_pwm = 10000
    max_current = v_ref/(r_top + r_heater)
    max_heater_power_uw = 1e6 * (max_current**2) * r_heater
    uw = max_heater_power_uw * libera_detector_data.PWM.values / max_pwm

    libera_detector_data.POWER_UW.values = uw


def apply_blackman_filter(libera_detector_data, output_points=41):
    """

    Parameters
    ----------
    libera_detector_data: xarray.Dataset
        The full libera detector dataset loaded from netCDF from Dave's
    output_points: int
        The width of the blackman filter to use

    Returns
    -------
    None a column is added to the original dataset

    """
    b_window = signal.windows.blackman(output_points)
    b_window = b_window[b_window > 1e-6]
    b_window_normal = b_window/np.sum(b_window)

    libera_detector_data.POWER_UW_SM.values = np.convolve(libera_detector_data.POWER_UW.values, b_window_normal, mode="same")


def create_detector_dataset_from_file(file_path):
    """
    This is a recreation of Dave's work separating the full signal recorded into specific cycles to make it easier
    to create averages, etc and compare multiple cycles rather across a whole test.

    Parameters
    ----------
    file_path: str
        The path to a netcdf file converted from Dave's IDL code which in turn is Labview output.

    Returns
    -------
    ds: xarray.Dataset
        A newly created dataset with each cycle separated and cycle number as a dimension.

    """
    libera_detector_data = xr.open_dataset(file_path)

    libera_detector_add_detector_power(libera_detector_data)
    apply_blackman_filter(libera_detector_data)

    # Putting in feedforward values to find cycles
    ff_state = libera_detector_data.FF_STATE.values
    index_transition = np.where((np.roll(ff_state, 1) == 0) & (ff_state == 1))

    half_cycle_points = np.median(index_transition - np.roll(index_transition, 1))
    cycle_points = int(2 * half_cycle_points)
    index_start = index_transition[0][1]
    n_cycles = int(np.floor((len(ff_state)-index_start) / cycle_points))

    cycle_steps = libera_detector_data.TIME[index_start:index_start + cycle_points * n_cycles].values.reshape(n_cycles, cycle_points)
    pwm = libera_detector_data.PWM[index_start:index_start + cycle_points * n_cycles].values.reshape(n_cycles, cycle_points)
    power_uw = libera_detector_data.POWER_UW[index_start:index_start + cycle_points * n_cycles].values.reshape(n_cycles,
                                                                                                           cycle_points)
    power_uw_sm = libera_detector_data.POWER_UW_SM[index_start:index_start + cycle_points * n_cycles].values.reshape(
        n_cycles, cycle_points)
    error = libera_detector_data.ERROR[index_start:index_start + cycle_points * n_cycles].values.reshape(n_cycles,
                                                                                                     cycle_points)
    error_cosine = libera_detector_data.ERROR_COSINE[index_start:index_start + cycle_points * n_cycles].values.reshape(
        n_cycles, cycle_points)
    pd_signal = libera_detector_data.PD_SIGNAL[index_start:index_start + cycle_points * n_cycles].values.reshape(n_cycles,
                                                                                                             cycle_points)
    ff_state = libera_detector_data.FF_STATE[index_start:index_start + cycle_points * n_cycles].values.reshape(n_cycles,
                                                                                                           cycle_points)

    ds = xr.Dataset(
        data_vars=dict(
            cycle_steps=(["cycle_number", "time"], cycle_steps),
            pwm=(["cycle_number", "time"], pwm),
            power_uw=(["cycle_number", "time"], power_uw),
            power_uw_sm=(["cycle_number", "time"], power_uw_sm),
            error=(["cycle_number", "time"], error),
            error_cosine=(["cycle_number", "time"], error_cosine),
            pd_signal=(["cycle_number", "time"], pd_signal),
            ff_state=(["cycle_number", "time"], ff_state),
        ),
        coords=dict(
            cycle_number=np.arange(n_cycles) + 1,
            time=np.arange(cycle_points) / 1000
        )
    )
    return ds


def generate_response_function_from_netcdf_file(file_path, interp_freqs: list):
    """
    This creates response functions from real detector data and outputs the response function interpolated along a
    given list of frequencies. This function builds on many others in this file.

    Parameters
    ----------
    file_path: str
        The path to a netcdf file converted from Dave's IDL code.
    interp_freqs: list
        The list of frequencies to interpolate to.

    Returns
    -------
    avg_smooth_tf_interp: list
        This is the smoothed response function at the frequencies given in interp_freqs
    avg_tf_interpolated: list
        This is the raw response function at the frequencies given in interp_freqs.

    """
    libera_step_dataset = create_detector_dataset_from_file(file_path)
    num_cycles = len(libera_step_dataset.power_uw[:, 0])
    cycle_points = len(libera_step_dataset.power_uw[0])

    full_freq = fftfreq(cycle_points, 1 / 1000)
    odd_index = (np.where((np.mod(full_freq, full_freq[2]) != 0) & (full_freq > 0)))[0].astype("int")
    odd_freq = full_freq[odd_index]

    transfer_function = np.zeros([num_cycles, len(odd_freq)], dtype=np.cdouble)
    smooth_transfer_function = np.zeros([num_cycles, len(odd_freq)], dtype=np.cdouble)

    for i in range(num_cycles):
        output_fft = fft(libera_step_dataset.power_uw[i].values)
        input_fft = fft(libera_step_dataset.pd_signal[i].values)
        sm_output_fft = fft(libera_step_dataset.power_uw_sm[i].values)
        transfer_function[i, :] = output_fft[odd_index] / input_fft[odd_index]
        smooth_transfer_function[i, :] = sm_output_fft[odd_index] / input_fft[odd_index]

    avg_transfer_function = np.zeros(len(odd_freq), dtype=np.cdouble)
    avg_smooth_transfer_function = np.zeros(len(odd_freq), dtype=np.cdouble)
    for i in range(len(odd_freq)):
        avg_transfer_function[i] = np.mean(np.real(transfer_function[:, i])) + 1j * np.mean(
            np.imag(transfer_function[:, i]))
        avg_smooth_transfer_function[i] = np.mean(np.real(smooth_transfer_function[:, i])) + 1j * np.mean(
            np.imag(smooth_transfer_function[:, i]))

    avg_transfer_function = avg_transfer_function / np.abs(avg_transfer_function[0])
    avg_tf_interpolated = np.interp(interp_freqs, odd_freq, avg_transfer_function)
    avg_smooth_transfer_function = avg_smooth_transfer_function / np.abs(avg_smooth_transfer_function[0])
    avg_smooth_tf_interp = np.interp(interp_freqs, odd_freq, avg_smooth_transfer_function)

    return avg_smooth_tf_interp, avg_tf_interpolated
