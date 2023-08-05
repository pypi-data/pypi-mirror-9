/**
 * @date Mon Aug 27 20:29:15 2012 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.ip.base/GaussianScaleSpace.h>

bob::ip::base::GaussianScaleSpace::GaussianScaleSpace(
  const size_t height,
  const size_t width,
  const size_t n_intervals,
  const size_t n_octaves,
  const int octave_min,
  const double sigma_n,
  const double sigma0,
  const double kernel_radius_factor,
  const bob::sp::Extrapolation::BorderType border_type
):
  m_height(height),
  m_width(width),
  m_n_octaves(n_octaves),
  m_n_intervals(n_intervals),
  m_octave_min(octave_min),
  m_sigma_n(sigma_n),
  m_sigma0(sigma0),
  m_kernel_radius_factor(kernel_radius_factor),
  m_conv_border(border_type)
{
  checkOctaveMin();
  resetCache();
  resetGaussians();
}

bob::ip::base::GaussianScaleSpace::GaussianScaleSpace(const GaussianScaleSpace& other):
  m_height(other.m_height), m_width(other.m_width),
  m_n_octaves(other.m_n_octaves), m_n_intervals(other.m_n_intervals),
  m_octave_min(other.m_octave_min), m_sigma_n(other.m_sigma_n),
  m_sigma0(other.m_sigma0),
  m_kernel_radius_factor(other.m_kernel_radius_factor),
  m_conv_border(other.m_conv_border)
{
  resetCache();
  resetGaussians();
}

bob::ip::base::GaussianScaleSpace::~GaussianScaleSpace()
{
}

bob::ip::base::GaussianScaleSpace& bob::ip::base::GaussianScaleSpace::operator=(const bob::ip::base::GaussianScaleSpace& other)
{
  if (this != &other)
  {
    m_height = other.m_height;
    m_width = other.m_width;
    m_n_octaves = other.m_n_octaves;
    m_n_intervals = other.m_n_intervals;
    m_octave_min = other.m_octave_min;
    m_sigma_n = other.m_sigma_n;
    m_sigma0 = other.m_sigma0;
    m_kernel_radius_factor = other.m_kernel_radius_factor;
    m_conv_border = other.m_conv_border;
    resetCache();
    resetGaussians();
  }
  return *this;
}

void bob::ip::base::GaussianScaleSpace::resetCache() const
{
  const blitz::TinyVector<int,3> shape = getOutputShape(m_octave_min);
  m_cache_array0.resize(shape(1), shape(2));
}

bool bob::ip::base::GaussianScaleSpace::operator==(const bob::ip::base::GaussianScaleSpace& b) const
{
  return (this->m_height == b.m_height && this->m_width == b.m_width &&
          this->m_n_octaves == b.m_n_octaves && this->m_n_intervals == b.m_n_intervals &&
          this->m_octave_min == b.m_octave_min && this->m_sigma_n == b.m_sigma_n &&
          this->m_sigma0 == b.m_sigma0 &&
          this->m_kernel_radius_factor == b.m_kernel_radius_factor &&
          this->m_conv_border == b.m_conv_border);
}

bool bob::ip::base::GaussianScaleSpace::operator!=(const bob::ip::base::GaussianScaleSpace& b) const
{
  return !(this->operator==(b));
}

void bob::ip::base::GaussianScaleSpace::checkOctaveMin() const
{
  if (m_octave_min < -1) {
    boost::format m("parameter `octave_min' should be greater or equal to -1 (it was set to %d)");
    m % m_octave_min;
    throw std::runtime_error(m.str());
  }
}

void bob::ip::base::GaussianScaleSpace::setSigma0NoInitSmoothing()
{
  m_sigma0 = m_sigma_n * pow(2., -(double)m_octave_min);
  resetGaussians();
  m_smooth_at_init = false;
}

void bob::ip::base::GaussianScaleSpace::resetGaussians()
{
  m_gaussians.clear();

  // First Gaussian
  double sa = m_sigma0;
  double sb = m_sigma_n * pow(2., -(double)m_octave_min);
  // sigma = sqrt( (sigma0*2^(-1/N_scales))**2 - (sigman*2^(-octave_min))**2
  double sigma;
  // Checks that the square root computation is possible
//std::cout << "sa=" << sa << " -- sb=" << sb << std::endl;
  if (sa <= sb)
  {
    // TODO: throw an exception?
    m_smooth_at_init = false;
    sigma = 1.;
  }
  else
  {
    m_smooth_at_init = true;
    sigma = sqrt(sa * sa - sb * sb);
  }
  size_t radius = static_cast<size_t>(ceil(m_kernel_radius_factor*sigma));
  boost::shared_ptr<bob::ip::base::Gaussian> g0(new
      bob::ip::base::Gaussian(radius, radius, sigma, sigma, m_conv_border));
  m_gaussians.push_back(g0);

  // The effective sigma for the next scale is computed as the square root of
  // the difference between the sigma^2 associated to this scale and the
  // sigma^2 of the previous scale. More precisely,
  //   sigEff_{o,s} = sqrt(sig_{o,s}^2 - sig_{o,s-1}^2) = dsigma0 * 2^{s/Ns}
  // where dsigma0 = sigma0 * sqrt(1 - 2^{-2/Ns}
  const double dsigma0 = m_sigma0 * sqrt(1. - pow(2,-2./(double)m_n_intervals));
  for (size_t s=0; s<m_n_intervals+2; ++s)
  {
    double sigma = dsigma0 * pow(2,(double)s / (double)m_n_intervals);
    size_t radius = static_cast<size_t>(ceil(m_kernel_radius_factor*sigma));
    boost::shared_ptr<bob::ip::base::Gaussian> g(new
        bob::ip::base::Gaussian(radius, radius, sigma, sigma, m_conv_border));
    m_gaussians.push_back(g);
  }
}

void bob::ip::base::GaussianScaleSpace::allocateOutputPyramid(
  std::vector<blitz::Array<double,3> >& dst) const
{
  dst.clear();
  for (size_t i=0; i<m_n_octaves; ++i)
  {
    blitz::Array<double,3> dst_o(getOutputShape(m_octave_min+(int)i));
    dst.push_back(dst_o);
  }
}

const blitz::TinyVector<int,3> bob::ip::base::GaussianScaleSpace::getOutputShape(const int octave) const
{
  // Is the octave index valid?n
  if (octave < m_octave_min || octave > getOctaveMax()) {
    boost::format m("parameter `octave' (%d) is outside the expected bounds [%d, %d]");
    m % octave % m_octave_min % getOctaveMax();
    throw std::runtime_error(m.str());
  }

  blitz::TinyVector<int,3> res;
  res(0) = m_n_intervals+3;
  if (octave < 0)
  {
    res(1) = m_height * (1 << -octave);
    res(2) = m_width * (1 << -octave);
  }
  else if (octave == 0)
  {
    res(1) = m_height;
    res(2) = m_width;
  }
  else
  {
    res(1) = m_height / (1 << octave);
    res(2) = m_width / (1 << octave);
  }
  return res;
}


