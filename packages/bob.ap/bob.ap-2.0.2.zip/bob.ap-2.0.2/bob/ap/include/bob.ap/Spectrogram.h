/**
 * @date Wed Jan 11:10:20 2013 +0200
 * @author Elie Khoury <Elie.Khoury@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief Implement spectrogram
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */


#ifndef BOB_AP_SPECTROGRAM_H
#define BOB_AP_SPECTROGRAM_H

#include <vector>
#include <stdexcept>
#include <blitz/array.h>
#include <boost/format.hpp>

#include <bob.sp/FFT1D.h>

#include "Energy.h"

namespace bob {
/**
 * \ingroup libap_api
 * @{
 *
 */
namespace ap {

/**
 * @brief This class implements an audio spectrogram extractor
 */
class Spectrogram: public Energy
{
  public:
    /**
     * @brief Constructor. Initializes working arrays
     */
    Spectrogram(const double sampling_frequency,
      const double win_length_ms=20., const double win_shift_ms=10.,
      const size_t n_filters=24, const double f_min=0.,
      const double f_max=4000., const double pre_emphasis_coeff=0.95,
      bool mel_scale=true);

    /**
     * @brief Copy Constructor
     */
    Spectrogram(const Spectrogram& other);

    /**
     * @brief Assignment operator
     */
    Spectrogram& operator=(const Spectrogram& other);

    /**
     * @brief Equal to
     */
    bool operator==(const Spectrogram& other) const;

    /**
     * @brief Not equal to
     */
    bool operator!=(const Spectrogram& other) const;

    /**
     * @brief Destructor
     */
    virtual ~Spectrogram();

    /**
     * @brief Gets the output shape for a given input/input length
     */
    virtual blitz::TinyVector<int,2> getShape(const size_t input_length) const;
    virtual blitz::TinyVector<int,2> getShape(const blitz::Array<double,1>& input) const;

    /**
     * @brief Computes the spectrogram
     */
    void operator()(const blitz::Array<double,1>& input, blitz::Array<double,2>& output);

    /**
     * @brief Returns the number of filters used in the filter bank.
     */
    size_t getNFilters() const
    { return m_n_filters; }
    /**
     * @brief Returns the frequency of the lowest triangular filter in the
     * filter bank
     */
    double getFMin() const
    { return m_f_min; }
    /**
     * @brief Returns the frequency of the highest triangular filter in the
     * filter bank
     */
    double getFMax() const
    { return m_f_max; }
    /**
     * @brief Tells whether the frequencies of the filters in the filter bank
     * are taken from the linear or the Mel scale
     */
    bool getMelScale() const
    { return m_mel_scale; }
    /**
     * @brief Returns the pre-emphasis coefficient.
     */
    double getPreEmphasisCoeff() const
    { return m_pre_emphasis_coeff; }
    /**
     * @brief Tells whether we used the energy or the square root of the energy
     */
    bool getEnergyFilter() const
    { return m_energy_filter; }
    /**
     * @brief Tells whether we used the log triangular filter or the triangular
     * filter
     */
    bool getLogFilter() const
    { return m_log_filter; }
    /**
     * @brief Tells whether we compute a spectrogram or energy bands
     */
    bool getEnergyBands() const
    { return m_energy_bands; }

    /**
     * @brief Sets the sampling frequency/frequency rate
     */
    virtual void setSamplingFrequency(const double sampling_frequency);
    /**
     * @brief Sets the window length in miliseconds
     */
    virtual void setWinLengthMs(const double win_length_ms);
    /**
     * @brief Sets the window shift in miliseconds
     */
    virtual void setWinShiftMs(const double win_shift_ms);

    /**
     * @brief Sets the number of filters used in the filter bank.
     */
    virtual void setNFilters(size_t n_filters);
    /**
     * @brief Sets the pre-emphasis coefficient. It should be a value in the
     * range [0,1].
     */
    virtual void setPreEmphasisCoeff(double pre_emphasis_coeff)
    {
      if (pre_emphasis_coeff < 0. || pre_emphasis_coeff > 1.) {
        boost::format m("the argument for `pre_emphasis_coeff' cannot take the value %f - the value must be in the interval [0.,1.]");
        m % pre_emphasis_coeff;
        throw std::runtime_error(m.str());
      }
      m_pre_emphasis_coeff = pre_emphasis_coeff;
    }
    /**
     * @brief Returns the frequency of the lowest triangular filter in the
     * filter bank
     */
    virtual void setFMin(double f_min);
    /**
     * @brief Returns the frequency of the highest triangular filter in the
     * filter bank
     */
    virtual void setFMax(double f_max);
    /**
     * @brief Sets whether the frequencies of the filters in the filter bank
     * are taken from the linear or the Mel scale
     */
    virtual void setMelScale(bool mel_scale);
    /**
     * @brief Sets whether we used the energy or the square root of the energy
     */
    virtual void setEnergyFilter(bool energy_filter)
    { m_energy_filter = energy_filter; }
    /**
     * @brief Sets whether we used the log triangular filter or the triangular
     * filter
     */
    virtual void setLogFilter(bool log_filter)
    { m_log_filter = log_filter; }
    /**
     * @brief Sets whether we compute a spectrogram or energy bands
     */
    virtual void setEnergyBands(bool energy_bands)
    { m_energy_bands = energy_bands; }


  protected:
    /**
     * @brief Converts a frequency in Herz to the corresponding one in Mel
     */
    static double herzToMel(double f);
    /**
     * @brief Converts a frequency in Mel to the corresponding one in Herz
     */
    static double melToHerz(double f);
    /**
     * @brief Pre-emphasises the signal by applying the first order equation
     * \f$data_{n} := data_{n} − a*data_{n−1}\f$
     */
    void pre_emphasis(blitz::Array<double,1> &data) const;
    /**
     * @brief Applies the Hamming window to the signal
     */
    void hammingWindow(blitz::Array<double,1> &data) const;

    /**
     * @brief Computes the power-spectrum of the FFT of the input frame
     */
    void powerSpectrumFFT(blitz::Array<double,1>& x);
    /**
     * @brief Applies the triangular filter bank
     */
    void filterBank(blitz::Array<double,1>& x);
    /**
     * @brief Applies the triangular filter bank to the input array and
     * returns the logarithm of the magnitude in each band.
     */
    void logTriangularFilterBank(blitz::Array<double,1>& data) const;
    /**
     * @brief Applies the triangular filter bank to the input array and
     * returns the magnitude in each band.
     */
    void triangularFilterBank(blitz::Array<double,1>& data) const;


    virtual void initWinLength();
    virtual void initWinSize();

    void initCacheHammingKernel();
    void initCacheFilterBank();

    /**
     * @brief Initialize the table m_p_index, which contains the indices of
     * the cut-off frequencies of the triangular filters.. It looks like:
     *
     *                      filter 2
     *                   <------------->
     *                filter 1           filter 4
     *             <----------->       <------------->
     *        | | | | | | | | | | | | | | | | | | | | | ..........
     *         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9  ..........
     *             ^     ^     ^       ^             ^
     *             |     |     |       |             |
     *            t[0]   |    t[2]     |           t[4]
     *                  t[1]          t[3]
     *
     */
    void initCachePIndex();
    void initCacheFilters();

    size_t m_n_filters;
    double m_f_min;
    double m_f_max;
    double m_pre_emphasis_coeff;
    bool m_mel_scale;
    double m_fb_out_floor;
    bool m_energy_filter;
    bool m_log_filter;
    bool m_energy_bands;
    double m_log_fb_out_floor;

    blitz::Array<double,1> m_hamming_kernel;
    blitz::Array<int,1> m_p_index;
    std::vector<blitz::Array<double,1> > m_filter_bank;
    bob::sp::FFT1D m_fft;

    mutable blitz::Array<std::complex<double>,1> m_cache_frame_c1;
    mutable blitz::Array<std::complex<double>,1> m_cache_frame_c2;
    mutable blitz::Array<double,1> m_cache_filters;
};

}
}

#endif /* BOB_AP_SPECTROGRAM_H */
