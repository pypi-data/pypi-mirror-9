/**
 * @date Sat Apr 30 17:52:15 2011 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief This file provides a class to process images with a Gaussian kernel
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */


#include <bob.ip.base/Gaussian.h>

bob::ip::base::Gaussian::Gaussian(
  const size_t radius_y, const size_t radius_x,
  const double sigma_y, const double sigma_x,
  const bob::sp::Extrapolation::BorderType border_type
):
  m_radius_y(radius_y), m_radius_x(radius_x),
  m_sigma_y(sigma_y), m_sigma_x(sigma_x),
  m_conv_border(border_type)
{
  computeKernel();
}


bob::ip::base::Gaussian::Gaussian(const Gaussian& other)
:
  m_radius_y(other.m_radius_y), m_radius_x(other.m_radius_x),
  m_sigma_y(other.m_sigma_y), m_sigma_x(other.m_sigma_x),
  m_conv_border(other.m_conv_border)
{
  computeKernel();
}


void bob::ip::base::Gaussian::computeKernel()
{
  m_kernel_y.resize(2 * m_radius_y + 1);
  // Computes the kernel
  const double half_inv_sigma2_y = 0.5 / (m_sigma_y * m_sigma_y);
  for (int j = -(int)m_radius_y; j <= (int)m_radius_y; j ++)
      m_kernel_y(j + m_radius_y) = exp(- half_inv_sigma2_y * (j * j));
  // Normalizes the kernel
  m_kernel_y /= blitz::sum(m_kernel_y);

  m_kernel_x.resize(2 * m_radius_x + 1);
  // Computes the kernel
  const double half_inv_sigma2_x = 0.5 / (m_sigma_x * m_sigma_x);
  for (int i = -(int)m_radius_x; i <= (int)m_radius_x; i++) {
    m_kernel_x(i + m_radius_x) = exp(- half_inv_sigma2_x * (i * i));
  }
  // Normalizes the kernel
  m_kernel_x /= blitz::sum(m_kernel_x);
}

void bob::ip::base::Gaussian::reset(
  const size_t radius_y, const size_t radius_x,
  const double sigma_y, const double sigma_x,
  const bob::sp::Extrapolation::BorderType border_type
){
  m_radius_y = radius_y;
  m_radius_x = radius_x;
  m_sigma_y = sigma_y;
  m_sigma_x = sigma_x;
  m_conv_border = border_type;
  computeKernel();
}

bob::ip::base::Gaussian& bob::ip::base::Gaussian::operator=(const bob::ip::base::Gaussian& other)
{
  if (this != &other)
  {
    m_radius_y = other.m_radius_y;
    m_radius_x = other.m_radius_x;
    m_sigma_y = other.m_sigma_y;
    m_sigma_x = other.m_sigma_x;
    m_conv_border = other.m_conv_border;
    computeKernel();
  }
  return *this;
}

bool bob::ip::base::Gaussian::operator==(const bob::ip::base::Gaussian& b) const
{
  return (this->m_radius_y == b.m_radius_y && this->m_radius_x == b.m_radius_x &&
          this->m_sigma_y == b.m_sigma_y && this->m_sigma_x == b.m_sigma_x &&
          this->m_conv_border == b.m_conv_border);
}

bool bob::ip::base::Gaussian::operator!=(const bob::ip::base::Gaussian& b) const
{
  return !(this->operator==(b));
}

void bob::ip::base::Gaussian::filter_(const blitz::Array<double,2>& src, blitz::Array<double,2>& dst)
{
  // Checks are postponed to the convolution function.
  if(m_conv_border == bob::sp::Extrapolation::Zero)
  {
    m_tmp_int.resize(bob::sp::getConvSepOutputSize(src, m_kernel_y, 0, bob::sp::Conv::Same));
    bob::sp::convSep(src, m_kernel_y, m_tmp_int, 0, bob::sp::Conv::Same);
    bob::sp::convSep(m_tmp_int, m_kernel_x, dst, 1, bob::sp::Conv::Same);
  }
  else
  {
    m_tmp_int1.resize(bob::sp::getConvSepOutputSize(src, m_kernel_y, 0, bob::sp::Conv::Full));
    if(m_conv_border == bob::sp::Extrapolation::NearestNeighbour)
      bob::sp::extrapolateNearest(src, m_tmp_int1);
    else if(m_conv_border == bob::sp::Extrapolation::Circular)
      bob::sp::extrapolateCircular(src, m_tmp_int1);
    else
      bob::sp::extrapolateMirror(src, m_tmp_int1);
    m_tmp_int.resize(bob::sp::getConvSepOutputSize(m_tmp_int1, m_kernel_y, 0, bob::sp::Conv::Valid));
    bob::sp::convSep(m_tmp_int1, m_kernel_y, m_tmp_int, 0, bob::sp::Conv::Valid);

    m_tmp_int2.resize(bob::sp::getConvSepOutputSize(m_tmp_int, m_kernel_x, 1, bob::sp::Conv::Full));
    if(m_conv_border == bob::sp::Extrapolation::NearestNeighbour)
      bob::sp::extrapolateNearest(m_tmp_int, m_tmp_int2);
    else if(m_conv_border == bob::sp::Extrapolation::Circular)
      bob::sp::extrapolateCircular(m_tmp_int, m_tmp_int2);
    else
      bob::sp::extrapolateMirror(m_tmp_int, m_tmp_int2);
    bob::sp::convSep(m_tmp_int2, m_kernel_x, dst, 1, bob::sp::Conv::Valid);
  }
}

