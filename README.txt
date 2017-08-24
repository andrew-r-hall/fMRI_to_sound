24 Aug 2017 : fmri-to-sound

This project aims to provide a function to map fMRI timeseries to human-audible sounds, with
possible applications as a form of neurofeedback, as some subtle differences may be audible, 
though not visible in more traditional methods of fMRI viewing. A description of the process
is below.

-- A GM-masked resting state fmri image is averaged across all spatial and temporal dimensions, to yield a 1D timeseries.

-- A 100 TR sliding window is applied, advanced by 1 TR in each iteration

-- Each windowed timeseries is converted to a power spectrum, and the average PS of the whole timeseries is subtracted from it.
	(in the baseline_not_removed data, this subtraction is skipped)

-- The power spectra are scaled into a frequency domain audible to humans

-- The spectra are transformed back to timeseries, and are written to .wav format