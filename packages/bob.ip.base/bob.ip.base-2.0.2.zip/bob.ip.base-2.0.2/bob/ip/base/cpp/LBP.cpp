/**
 * @date Wed Apr 20 20:21:19 2011 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Rewritten:
 * @date Wed Apr 10 17:39:21 CEST 2013
 * @author Manuel Guenther <manuel.guenther@idiap.ch>
 *
 * @brief LBP implementation
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.ip.base/LBP.h>

#include <boost/math/constants/constants.hpp>

bob::ip::base::LBP::LBP(
    const int P,
    const double R_y,
    const double R_x,
    const bool circular,
    const bool to_average,
    const bool add_average_bit,
    const bool uniform,
    const bool rotation_invariant,
    const bob::ip::base::ELBPType eLBP_type,
    const bob::ip::base::LBPBorderHandling border_handling
):
  m_P(P),
  m_R_y(R_y),
  m_R_x(R_x),
  m_mb_y(-1),
  m_mb_x(-1),
  m_ov_y(0),
  m_ov_x(0),
  m_circular(circular),
  m_to_average(to_average),
  m_add_average_bit(add_average_bit),
  m_uniform(uniform),
  m_rotation_invariant(rotation_invariant),
  m_eLBP_type(eLBP_type),
  m_border_handling(border_handling),
  m_lut(0),
  m_positions(0,0),
  m_int_positions(0,0)
{
  // sanity check
  if (m_eLBP_type == ELBP_DIRECTION_CODED && m_P%2) {
    throw std::runtime_error("Direction coded LBP types require an even number of neighbors.");
  }
  init();
}

bob::ip::base::LBP::LBP(
    const int P,
    const double R,
    const bool circular,
    const bool to_average,
    const bool add_average_bit,
    const bool uniform,
    const bool rotation_invariant,
    const bob::ip::base::ELBPType eLBP_type,
    const bob::ip::base::LBPBorderHandling border_handling
):
  m_P(P),
  m_R_y(R),
  m_R_x(R),
  m_mb_y(-1),
  m_mb_x(-1),
  m_ov_y(0),
  m_ov_x(0),
  m_circular(circular),
  m_to_average(to_average),
  m_add_average_bit(add_average_bit),
  m_uniform(uniform),
  m_rotation_invariant(rotation_invariant),
  m_eLBP_type(eLBP_type),
  m_border_handling(border_handling),
  m_lut(0),
  m_positions(0,0),
  m_int_positions(0,0)
{
  // sanity check
  if (m_eLBP_type == ELBP_DIRECTION_CODED && m_P%2) {
    throw std::runtime_error("Direction coded LBP types require an even number of neighbors.");
  }
  init();
}

bob::ip::base::LBP::LBP(
    const int P,
    const blitz::TinyVector<int,2> block_size,
    const blitz::TinyVector<int,2> block_overlap,
    const bool to_average,
    const bool add_average_bit,
    const bool uniform,
    const bool rotation_invariant,
    const bob::ip::base::ELBPType eLBP_type,
    const bob::ip::base::LBPBorderHandling border_handling):
  m_P(P),
  m_R_y(-1.),
  m_R_x(-1.),
  m_mb_y(block_size[0]),
  m_mb_x(block_size[1]),
  m_ov_y(block_overlap[0]),
  m_ov_x(block_overlap[1]),
  m_circular(false),
  m_to_average(to_average),
  m_add_average_bit(add_average_bit),
  m_uniform(uniform),
  m_rotation_invariant(rotation_invariant),
  m_eLBP_type(eLBP_type),
  m_border_handling(border_handling),
  m_lut(0),
  m_positions(0,0),
  m_int_positions(0,0)
{
  // sanity check
  if (m_eLBP_type == ELBP_DIRECTION_CODED && m_P%2) {
    throw std::runtime_error("Direction coded LBP types require an even number of neighbors.");
  }
  init();
}

bob::ip::base::LBP::LBP(bob::io::base::HDF5File file):
  m_P(0),
  m_R_y(0),
  m_R_x(0),
  m_mb_y(0),
  m_mb_x(0),
  m_ov_y(0),
  m_ov_x(0),
  m_circular(false),
  m_to_average(false),
  m_add_average_bit(false),
  m_uniform(false),
  m_rotation_invariant(false),
  m_eLBP_type(bob::ip::base::ELBP_REGULAR),
  m_border_handling(bob::ip::base::LBP_BORDER_SHRINK),
  m_lut(0),
  m_positions(0,0),
  m_int_positions(0,0)
{
  // sanity check
  load(file);
}


bob::ip::base::LBP::LBP(const bob::ip::base::LBP& other):
  m_P(other.m_P),
  m_R_y(other.m_R_y),
  m_R_x(other.m_R_x),
  m_mb_y(other.m_mb_y),
  m_mb_x(other.m_mb_x),
  m_ov_y(other.m_ov_y),
  m_ov_x(other.m_ov_x),
  m_circular(other.m_circular),
  m_to_average(other.m_to_average),
  m_add_average_bit(other.m_add_average_bit),
  m_uniform(other.m_uniform),
  m_rotation_invariant(other.m_rotation_invariant),
  m_eLBP_type(other.m_eLBP_type),
  m_border_handling(other.m_border_handling),
  m_lut(0),
  m_positions(0,0),
  m_int_positions(0,0)
{
  // sanity check
  if (m_eLBP_type == ELBP_DIRECTION_CODED && m_P%2) {
    throw std::runtime_error("Direction coded LBP types require an even number of neighbors.");
  }
  init();
}

bob::ip::base::LBP::~LBP() { }

bob::ip::base::LBP& bob::ip::base::LBP::operator=(const bob::ip::base::LBP& other) {
  m_P = other.m_P;
  m_R_y = other.m_R_y;
  m_R_x = other.m_R_x;
  m_mb_y = other.m_mb_y;
  m_mb_x = other.m_mb_x;
  m_ov_y = other.m_ov_y;
  m_ov_x = other.m_ov_x;
  m_circular = other.m_circular;
  m_to_average = other.m_to_average;
  m_add_average_bit = other.m_add_average_bit;
  m_uniform = other.m_uniform;
  m_rotation_invariant = other.m_rotation_invariant;
  m_eLBP_type = other.m_eLBP_type;
  m_border_handling = other.m_border_handling;
  init();
  return *this;
}

bool bob::ip::base::LBP::operator==(const bob::ip::base::LBP& other) const{
  return
    m_P == other.m_P &&
    m_R_y == other.m_R_y &&
    m_R_x == other.m_R_x &&
    m_mb_y == other.m_mb_y &&
    m_mb_x == other.m_mb_x &&
    m_ov_y == other.m_ov_y &&
    m_ov_x == other.m_ov_x &&
    m_circular == other.m_circular &&
    m_to_average == other.m_to_average &&
    m_add_average_bit == other.m_add_average_bit &&
    m_uniform == other.m_uniform &&
    m_rotation_invariant == other.m_rotation_invariant &&
    m_eLBP_type == other.m_eLBP_type &&
    m_border_handling == other.m_border_handling;
}

uint16_t bob::ip::base::LBP::right_shift_circular(uint16_t pattern, int spaces)
{
  return (pattern >> spaces | pattern << (m_P-spaces)) & ((1 << m_P) - 1);
}

void bob::ip::base::LBP::init()
{
  if (m_P < 4)
    throw std::runtime_error("LBP codes with less than 4 bits are not supported.");
  // check that the parameters are something useful, what we can handle
  if (m_P != 4 && m_P != 8 && m_P != 16 &&
      (m_uniform || m_rotation_invariant || (m_add_average_bit && m_to_average)))
    throw std::runtime_error("Special LBP types are only implemented for 4, 8, or 16 neighbors.");
  if (m_P == 16 && m_add_average_bit && m_to_average){
    throw std::runtime_error("LBP codes with average bit require 17 bits, but our representation is UINT16.");
  }
  if (isMultiBlockLBP() && m_P == 16){
    throw std::runtime_error("LBP codes are not supported for multi-block LBP's.");
  }
  if (m_P > 16){
    throw std::runtime_error("LBP codes with more than 16 neighbors are not supported since our representation is UINT16.");
  }
  if ((m_mb_y < 0 || m_mb_x < 0) && (m_R_y < 0 || m_R_x < 0)){
    throw std::runtime_error("LPB codes with negative radius or negative multi-block dimensions are not supported.");
  }

  if (isMultiBlockLBP() && m_border_handling != LBP_BORDER_SHRINK){
    throw std::runtime_error("Multi-block LBP codes cannot handle other border handling than LBP_BORDER_SHRINK");
  }

  if (isMultiBlockLBP() && (m_ov_y < 0 || m_ov_y >= m_mb_y || m_ov_x < 0 || m_ov_x >= m_mb_x)){
    throw std::runtime_error("Overlap of Multi-block LBP's must be positive and smaller than the multi-block size");
  }

  // initialize temporal memory
  _pixels.resize(m_P);

  // initialize the positions
  if (m_mb_y > 0 && m_mb_x > 0){
    // multi-block LBP requested; store the top-left and bottom-right entry for all our positions
    // compute the top-left of the central pixel
    blitz::TinyVector<int, 8> d_y, d_x;
    int top_y = -m_mb_y/2, left_x = -m_mb_x/2;
    switch (m_P){
      case 4:{
        // 4 neighbors: (-y,0), (0,x), (y,0), (0,-x)
        d_y = -m_mb_y + m_ov_y, 0, m_mb_y - m_ov_y, 0;
        d_x = 0, m_mb_x - m_ov_x, 0, -m_mb_x + m_ov_x;
      }break;
      case 8:{
        // 8 neighbors: (-y,-x), (-y,0), (-y,x), (0,x), (y,x), (y,0), (y,-x), (0,-x)
        d_y = -m_mb_y + m_ov_y, -m_mb_y + m_ov_y, -m_mb_y + m_ov_y, 0, m_mb_y - m_ov_y, m_mb_y - m_ov_y, m_mb_y - m_ov_y, 0;
        d_x = -m_mb_x + m_ov_x, 0, m_mb_x - m_ov_x, m_mb_x - m_ov_x, m_mb_x - m_ov_x, 0, -m_mb_x + m_ov_x, -m_mb_x + m_ov_x;
        break;
      }
      default:
        // any other number of neighbors is not supported
        throw std::runtime_error("Multi-block LBP's with other than 4 and 8 neighbors are not supported.");
    }
    // fill the positions
    m_int_positions.resize(m_P+1, 4);
    for (int p = 0; p < m_P; ++p){
      // top of the region
      m_int_positions(p,0) = d_y[p] + top_y;
      // bottom of the region (not included)
      m_int_positions(p,1) = d_y[p] + top_y + m_mb_y;
      // left of the region
      m_int_positions(p,2) = d_x[p] + left_x;
      // right of the region (not included)
      m_int_positions(p,3) = d_x[p] + left_x + m_mb_x;
    }
    // fill the last position, which is the central pixel
    // top of the region
    m_int_positions(m_P,0) = top_y;
    // bottom of the region (not included)
    m_int_positions(m_P,1) = top_y + m_mb_y;
    // left of the region
    m_int_positions(m_P,2) = left_x;
    // right of the region (not included)
    m_int_positions(m_P,3) = left_x + m_mb_x;
  }else{
    if (m_circular){
      m_positions.resize(m_P,2);
      double PI = boost::math::constants::pi<double>();
      // compute angle offset since LBP codes do not start at the x axis
      double angle_offset = m_P == 4 ? - 0.5 * PI : - 0.75 * PI;
      for (int p = 0; p < m_P; ++p){
        double angle = angle_offset + 2. * PI * p / m_P;
        m_positions(p,0) = m_R_y * sin(angle);
        m_positions(p,1) = m_R_x * cos(angle);
      }
    }else{ // circular
      blitz::TinyVector<int, 8> d_y, d_x;
      int r_y = (int)round(m_R_y), r_x = (int)round(m_R_x);
      switch (m_P){
        case 4:{
          // 4 neighbors: (-y,0), (0,x), (y,0), (0,-x)
          d_y = -r_y, 0, r_y, 0;
          d_x = 0, r_x, 0, -r_x;
        }break;
        case 8:{
          // 8 neighbors: (-y,-x), (-y,0), (-y,x), (0,x), (y,x), (y,0), (y,-x), (0,-x)
          d_y = -r_y, -r_y, -r_y, 0, r_y, r_y, r_y, 0;
          d_x = -r_x, 0, r_x, r_x, r_x, 0, -r_x, -r_x;
          break;
        }
        case 16:
          // 16 neighbors: ...
          throw std::runtime_error("Rectangular LBP16 codes are not yet implemented.");
        default:
          // any other number of neighbors is not supported
          throw std::runtime_error("Rectangular LBP's with other than 4 and 8 neighbors are not supported.");
      }
      // fill the positions
      m_int_positions.resize(m_P,2);
      for (int p = 0; p < m_P; ++p){
        m_int_positions(p,0) = d_y[p];
        m_int_positions(p,1) = d_x[p];
      }
    }
  }

  // initialize the look up table for the current setup
  // initialize all values with 0
  m_lut.resize(1 << m_P);
  m_lut = 0;
  uint16_t lbp_code = 0;
  if (m_uniform){
    // pre-compute uniform pattern bases (i.e., which are rotated to build all uniform patterns)
    std::vector<uint16_t> uniform_pattern_bases(m_P+1);
    for (int p = 1; p < m_P+1; ++p){
      // the pattern generation is adapted to be identical to the old LBP8R uniform pattern generator
      uniform_pattern_bases[p] = ((1 << p) -1) << (m_P - p);
    }
    // all non uniform patterns have a label of 0.
    m_lut = lbp_code++;
    // LBP pattern with all zero bits equal to 1
    m_lut(0) = lbp_code++;
    // compute patterns
    // all the other LBP patterns with bases[i] next-to-each-other bits equal to 1
    for (int p = 1; p < m_P; ++p){
      // assign all shifted versions of the base pattern the same lbp code
      for (int shift = 0; shift < m_P; ++shift){
        int shifted_pattern = right_shift_circular(uniform_pattern_bases[p], shift);
        // assign the shifted pattern
        m_lut(shifted_pattern) = lbp_code;
        if (!m_rotation_invariant)
          // change lbp code for each shift of each pattern
          ++lbp_code;
      }
      if (m_rotation_invariant)
        // change lbp code for each pattern
        ++lbp_code;
    }
    //LBP pattern with all unit bits gets the last code
    m_lut(uniform_pattern_bases[m_P]) = lbp_code;
  }else{ // not uniform
    if (m_rotation_invariant){
      // rotation invariant patterns are not that easy...
      // first, collect all possible RI patterns and assign all patterns to them
      std::vector<bool> found_pattern(1 << m_P);
      std::fill(found_pattern.begin(), found_pattern.end(), false);

      for (int c = 0; c < (1 << m_P); ++c){
        uint16_t pattern = static_cast<uint16_t>(c);
        // search for the LBP code with the smallest integral value
        bool this_pattern_is_new = false;
        for (int p = 0; p < m_P; ++p)
        {
          // generate shifted version of the code
          uint16_t shifted_code = right_shift_circular(pattern, p);
          if (!found_pattern[shifted_code]){
            found_pattern[shifted_code] = true;
            this_pattern_is_new = true;
            m_lut(shifted_code) = lbp_code;
          }
        }
        if (this_pattern_is_new){
          ++lbp_code;
        }
      }
    }else{ // not rotation invariant
      // initialize LUT with non-special values
      if(m_add_average_bit && m_to_average)
        m_lut.resize(1 << (m_P+1));
      blitz::firstIndex i;
      m_lut = i;
    }
  }
}

const blitz::TinyVector<int,2> bob::ip::base::LBP::getLBPShape(const blitz::TinyVector<int,2>& resolution, bool is_integral_image) const
{
  int dy, dx;
  if (m_border_handling == LBP_BORDER_WRAP){
    // when wrapping borders, the resolution is not altered
    dy = 0;
    dx = 0;
  } else if (m_mb_y > 0 && m_mb_x > 0){
    dy = 3 * m_mb_y - 2 * m_ov_y - 1;
    dx = 3 * m_mb_x - 2 * m_ov_x - 1;
  } else {
    dy = 2*(int)ceil(m_R_y);
    dx = 2*(int)ceil(m_R_x);
  }

  if (is_integral_image){
    // if the given image is an integral image, we have to subtract one pixel more
    dy += 1;
    dx += 1;
  }
  return blitz::TinyVector<int,2> (std::max(0, resolution[0] - dy), std::max(0, resolution[1] - dx));
}


blitz::TinyVector<int, 2> bob::ip::base::LBP::getOffset() const {
  blitz::TinyVector<int, 2> offset;
  if (m_border_handling == LBP_BORDER_WRAP){
    // for wrapping boarders, all pixels are allowed
    offset[0] = 0;
    offset[1] = 0;
  } else if (m_mb_y > 0 && m_mb_x > 0){
    // for multi-block LBP features, the offset is defined as 1.5 times the block size
    offset[0] = m_mb_y - m_ov_y + m_mb_y/2;
    offset[1] = m_mb_x - m_ov_x + m_mb_x/2;
  } else {
    /// for normal LBP, the offset is equal to the radius
    offset[0] = (int)ceil(m_R_y);
    offset[1] = (int)ceil(m_R_x);
  }
  return offset;
}

int bob::ip::base::LBP::getMaxLabel() const {
  if (m_rotation_invariant){
    if (m_uniform)
      // rotation invariant uniform LBP
      return m_P + 2;
    else
      // rotation invariant non-uniform LBP
      // simply return the highest label plus 1
      return m_lut((1 << m_P) - 1) + 1;
  }else{
    if (m_uniform)
      // uniform LBP
      return m_P * (m_P-1) + 3;
    else{
      // regular LBP
      if (m_to_average && m_add_average_bit)
        return 1 << (m_P+1);
      else
        return 1 << m_P;
    }
  }
}

void bob::ip::base::LBP::save(bob::io::base::HDF5File file) const{
  file.set("Neighbors", m_P);
  if (m_mb_y > 0 && m_mb_y > 0) {
    file.append("BlockSize", m_mb_y);
    file.append("BlockSize", m_mb_x);
    file.append("BlockOverlap", m_ov_y);
    file.append("BlockOverlap", m_ov_x);
  } else {
    file.append("Radius", m_R_y);
    file.append("Radius", m_R_x);
    file.set("Circular", m_circular ? 1 : 0);
    file.set("BorderHandling", m_border_handling);
  }
  file.set("Uniform", m_uniform ? 1 : 0);
  file.set("RotationInvariant", m_rotation_invariant ? 1 : 0);
  file.set("ToAverage", m_to_average ? 1 : 0);
  file.set("AddAverageBit", m_add_average_bit ? 1 : 0);
  file.set("ELBPType", m_eLBP_type);
}

void bob::ip::base::LBP::load(bob::io::base::HDF5File file){
  m_P = file.read<int>("Neighbors");
  m_ov_y = m_ov_x = 0;
  if (file.contains("BlockSize")){
    // multi-block LBP
    m_mb_y = file.read<int>("BlockSize", 0);
    m_mb_x = file.read<int>("BlockSize", 1);
    // block overlap
    if (file.contains("BlockOverlap")){
      m_ov_y = file.read<int>("BlockOverlap", 0);
      m_ov_x = file.read<int>("BlockOverlap", 1);
    }
    m_R_y = m_R_x = -1.;
    m_circular = false;
    m_border_handling = LBP_BORDER_SHRINK;
  } else {
    // regular LBP
    m_R_y = file.read<double>("Radius", 0);
    m_R_x = file.read<double>("Radius", 1);
    m_border_handling = static_cast<bob::ip::base::LBPBorderHandling>(file.read<int>("BorderHandling"));
    m_circular = file.read<int>("Circular") > 0;
    m_mb_y = m_mb_x = -1;
  }

  m_uniform = file.read<int>("Uniform") > 0;
  m_rotation_invariant = file.read<int>("RotationInvariant") > 0;
  m_to_average = file.read<int>("ToAverage") > 0;
  m_add_average_bit = file.read<int>("AddAverageBit") > 0;
  m_eLBP_type = static_cast<bob::ip::base::ELBPType>(file.read<int>("ELBPType"));

  // initialize
  init();
}
