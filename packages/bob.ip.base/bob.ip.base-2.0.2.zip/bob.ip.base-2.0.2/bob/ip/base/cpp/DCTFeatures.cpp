/**
 * @date Mon Aug 27 20:29:15 2012 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief This file provides a class to DCT by blocks features
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.ip.base/DCTFeatures.h>
#include <bob.ip.base/ZigZag.h>

#include <stdexcept>

bob::ip::base::DCTFeatures::DCTFeatures(
  const size_t n_dct_coefs,
  const size_t block_h, const size_t block_w,
  const size_t overlap_h, const size_t overlap_w,
  const bool norm_block,
  const bool norm_dct,
  const bool square_pattern
):
  m_dct2d(block_h, block_w),
  m_block_h(block_h), m_block_w(block_w), m_overlap_h(overlap_h),
  m_overlap_w(overlap_w), m_n_dct_coefs(n_dct_coefs),
  m_norm_block(norm_block), m_norm_dct(norm_dct),
  m_square_pattern(square_pattern),
  m_norm_epsilon(10*std::numeric_limits<double>::epsilon())
{
  setCheckSqrtNDctCoefs();
  resetCache();
}


bob::ip::base::DCTFeatures::DCTFeatures(const bob::ip::base::DCTFeatures& other)
:
  m_dct2d(other.m_dct2d),
  m_block_h(other.m_block_h), m_block_w(other.m_block_w),
  m_overlap_h(other.m_overlap_h), m_overlap_w(other.m_overlap_w),
  m_n_dct_coefs(other.m_n_dct_coefs),
  m_norm_block(other.m_norm_block), m_norm_dct(other.m_norm_dct),
  m_square_pattern(other.m_square_pattern),
  m_norm_epsilon(other.m_norm_epsilon)
{
  setCheckSqrtNDctCoefs();
  resetCache();
}


bob::ip::base::DCTFeatures& bob::ip::base::DCTFeatures::operator=(const bob::ip::base::DCTFeatures& other)
{
  if (this != &other)
  {
    m_block_h = other.m_block_h;
    m_block_w = other.m_block_w;
    m_overlap_h = other.m_overlap_h;
    m_overlap_w = other.m_overlap_w;
    m_n_dct_coefs = other.m_n_dct_coefs;
    m_norm_block = other.m_norm_block;
    m_norm_dct = other.m_norm_dct;
    m_dct2d.setShape(m_block_h, m_block_w);
    m_square_pattern = other.m_square_pattern;
    m_norm_epsilon = other.m_norm_epsilon;
    setCheckSqrtNDctCoefs();
    resetCache();
  }
  return *this;
}

void bob::ip::base::DCTFeatures::setCheckSqrtNDctCoefs()
{
  m_sqrt_n_dct_coefs = (size_t)sqrt(m_n_dct_coefs);
  if (m_square_pattern)
  {
    // Check that m_n_dct_coefs is a square integer
    int root = 0;
    while (root * root < (int)m_n_dct_coefs) ++root;
    // m_n_dct_coefs is a square integer
    if (root * root != (int)m_n_dct_coefs)
      throw std::runtime_error("bob::ip::DCTFeatures: Cannot use a square pattern when the number of DCT coefficients is not a square integer");
  }
}

void bob::ip::base::DCTFeatures::resetCache() const
{
  resetCacheBlock();
  resetCacheDct();
}

void bob::ip::base::DCTFeatures::resetCacheBlock() const
{
  m_cache_block1.resize(m_block_h, m_block_w);
  m_cache_block2.resize(m_block_h, m_block_w);
}

void bob::ip::base::DCTFeatures::resetCacheDct() const
{
  m_cache_dct_full.resize(m_n_dct_coefs);
  const size_t m_n_dct_coefs_norm = m_n_dct_coefs - (m_norm_block?1:0);
  m_cache_dct1.resize(m_n_dct_coefs_norm);
  m_cache_dct2.resize(m_n_dct_coefs_norm);
}

bool bob::ip::base::DCTFeatures::operator==(const bob::ip::base::DCTFeatures& b) const
{
  return (this->m_block_h == b.m_block_h && this->m_block_w == b.m_block_w &&
          this->m_overlap_h == b.m_overlap_h &&
          this->m_overlap_w == b.m_overlap_w &&
          this->m_norm_block == b.m_norm_block &&
          this->m_norm_dct == b.m_norm_dct &&
          this->m_n_dct_coefs == b.m_n_dct_coefs &&
          this->m_square_pattern == b.m_square_pattern &&
          this->m_norm_epsilon == b.m_norm_epsilon);
}

bool bob::ip::base::DCTFeatures::operator!=(const bob::ip::base::DCTFeatures& b) const
{
  return !(this->operator==(b));
}

void bob::ip::base::DCTFeatures::normalizeBlock(const blitz::Array<double,2>& b) const
{
  // Normalize block if required and extract DCT for the current block
  if(m_norm_block)
  {
    double mean = blitz::mean(b);
    double var = blitz::sum(blitz::pow2(b - mean)) / (double)(m_block_h * m_block_w);
    double std = 1.;
    if(var >= m_norm_epsilon) std = sqrt(var);
    m_cache_block1 = (b - mean) / std;
    m_dct2d(m_cache_block1, m_cache_block2);
  }
  else
    m_dct2d(bob::core::array::ccopy(b), m_cache_block2);
}

void bob::ip::base::DCTFeatures::extractRowDCTCoefs(blitz::Array<double,1>& dst_row) const
{
  if (!m_square_pattern)
  {
    if (m_norm_block)
    {
      zigzag(m_cache_block2, m_cache_dct_full);
      dst_row = m_cache_dct_full(blitz::Range(1,m_n_dct_coefs-1));
    }
    else
      zigzag(m_cache_block2, dst_row);
  }
  else
  {
    int r=0;
    int beg=0;
    if (m_norm_block)
    {
      dst_row(blitz::Range(0,m_sqrt_n_dct_coefs-2)) = m_cache_block2(r,blitz::Range(1,m_sqrt_n_dct_coefs-1));
      r += 1;
      beg = m_sqrt_n_dct_coefs-1;
    }
    blitz::Range ra(0,m_sqrt_n_dct_coefs-1);
    for(; r<(int)m_sqrt_n_dct_coefs; ++r, beg+=m_sqrt_n_dct_coefs)
      dst_row(blitz::Range(beg,beg+m_sqrt_n_dct_coefs-1)) = m_cache_block2(r,ra);
  }
}

void bob::ip::base::DCTFeatures::extract_(const blitz::Array<double,2>& src, blitz::Array<double,2>& dst) const
{
  // Checks input/output
  bob::core::array::assertZeroBase(src);
  bob::core::array::assertZeroBase(dst);
  blitz::TinyVector<int,2> shape = get2DOutputShape(src.shape());
  bob::core::array::assertSameShape(dst, shape);

  // get all the blocks
  const auto blocks = blockReference(src, m_block_h, m_block_w, m_overlap_h, m_overlap_w);

  /// dct extract each block
  int i=0;
  for(auto it = blocks.begin(); it != blocks.end(); ++it, ++i)
  {
    // Normalize input block (if required)
    normalizeBlock(*it);

    // Extract the required number of coefficients using the zigzag pattern
    // and push it in the right dst row
    blitz::Array<double,1> dst_row = dst(i, blitz::Range::all());
    extractRowDCTCoefs(dst_row);
  }

  // Normalize dct if required
  if(m_norm_dct)
  {
    blitz::firstIndex ii;
    blitz::secondIndex jj;
    m_cache_dct1 = blitz::mean(dst(jj,ii), jj); // mean
    m_cache_dct2 = blitz::sum(blitz::pow2(dst(jj,ii) - m_cache_dct1(ii)),jj) / (double)(dst.extent(0));
    m_cache_dct2 = blitz::where(m_cache_dct2 <= m_norm_epsilon, 1., blitz::sqrt(m_cache_dct2));
    dst = (dst(ii,jj) - m_cache_dct1(jj)) / m_cache_dct2(jj);
  }
}


void bob::ip::base::DCTFeatures::extract_(const blitz::Array<double,2>& src, blitz::Array<double,3>& dst) const
{
  // Checks input/output
  bob::core::array::assertZeroBase(src);
  bob::core::array::assertZeroBase(dst);
  blitz::TinyVector<int,3> shape = get3DOutputShape(src.shape());
  bob::core::array::assertSameShape(dst, shape);

  // get all the blocks
  const auto blocks = blockReference(src, m_block_h, m_block_w, m_overlap_h, m_overlap_w);
  const blitz::TinyVector<int,4> block_shape = getBlock4DOutputShape(src.extent(0), src.extent(1), m_block_h, m_block_w, m_overlap_h, m_overlap_w);

  /// dct extract each block
  int i=0;
  int j=0;
  for(auto  it = blocks.begin(); it != blocks.end(); ++it)
  {
    // Normalize block if required and extract DCT for the current block
    normalizeBlock(*it);

    // Extract the required number of coefficients using the zigzag pattern
    // and push it in the right dst row
    blitz::Array<double,1> dst_row = dst(i, j, blitz::Range::all());
    extractRowDCTCoefs(dst_row);
    // Increment block indices
    if (j>=shape(1)-1)
    {
      j=0;
      ++i;
    }
    else
      ++j;
  }

  // Normalize dct if required
  if(m_norm_dct)
  {
    blitz::firstIndex ii;
    blitz::secondIndex jj;
    blitz::thirdIndex kk;
    m_cache_dct1 = blitz::mean(dst(kk,ii,jj), kk); // mean
    m_cache_dct2 = blitz::sum(blitz::pow2(dst(kk,ii,jj) - m_cache_dct1(ii,jj)),kk) / (double)(dst.extent(0));
    m_cache_dct2 = blitz::where(m_cache_dct2 <= m_norm_epsilon, 1., blitz::sqrt(m_cache_dct2));
    dst = (dst(ii,jj,kk) - m_cache_dct1(kk)) / m_cache_dct2(kk);
  }
}


