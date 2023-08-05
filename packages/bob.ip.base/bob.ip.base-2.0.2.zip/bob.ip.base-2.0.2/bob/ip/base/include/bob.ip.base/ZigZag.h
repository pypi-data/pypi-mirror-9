/**
 * @date Tue Apr 5 17:28:28 2011 +0200
 * @author Niklas Johansson <niklas.johansson@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief This file defines a function to extract a 1D zigzag pattern from
 * 2D dimensional array as described in:
 *   "Polynomial Features for Robust Face Authentication",
 *   from C. Sanderson and K. Paliwal, in the proceedings of the
 *   IEEE International Conference on Image Processing 2002.
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IP_BASE_ZIGZAG_H
#define BOB_IP_BASE_ZIGZAG_H

#include <stdexcept>
#include <boost/format.hpp>
#include <bob.core/assert.h>

namespace bob { namespace ip { namespace base {

  /**
    * @brief Extract the zigzag pattern from a 2D blitz::array, as
    * described in:
    *   "Polynomial Features for Robust Face Authentication",
    *   from C. Sanderson and K. Paliwal, in the proceedings of the
    *   IEEE International Conference on Image Processing 2002.
    * @param src The input blitz array
    * @param dst The output blitz array
    * @param right_first Set to true to reverse the initial zigzag order.
    *   By default, the direction is left-to-right for the first diagonal.
    */
  template<typename T>
  void zigzagNoCheck(
    const blitz::Array<T,2>& src,
    blitz::Array<T,1>& dst,
    const bool right_first
  ){
    // Number of coefficients to keep
    const int n_coef_kept = dst.extent(0);

    // Define constants
    const int min_dim = std::min(src.extent(0), src.extent(1));
    const int max_dim = std::max(src.extent(0), src.extent(1));
    // Index of the current diagonal
    int current_diagonal = 0;
    // Direction of the current diagonal
    int diagonal_left_to_right_p = !right_first;
    // Offset the point in the current diagonal from its origin
    int diagonal_offset = 0;
    // Length of the current diagonal
    int diagonal_length = 1;

    // Get all required coefficients
    for(int ind=0; ind < n_coef_kept; ++ind ) {
      int x, y;

      // Conditions used to determine the coordinates (x,y) in the 2D
      // array given the 1D index in the zigzag
      if(diagonal_left_to_right_p) {
        if( current_diagonal>src.extent(0)-1 ) {
          x = current_diagonal-(src.extent(0)-1) + diagonal_offset;
          y = (src.extent(0)-1) - diagonal_offset;
        }
        else {
          x = diagonal_offset;
          y = current_diagonal - diagonal_offset;
        }
      } else {
        if( current_diagonal>src.extent(1)-1 ) {
          x = (src.extent(1)-1) - diagonal_offset;
          y = current_diagonal-(src.extent(1)-1) + diagonal_offset;
        }
        else {
          x = current_diagonal - diagonal_offset;
          y = diagonal_offset;
        }
      }

      // save the value in the 1D array
      dst(ind) = src(y, x);

      // Increment the diagonal offset
      ++diagonal_offset;
      // Update information about the current diagonal if required
      if(diagonal_length <= diagonal_offset) {
        // Increment current diagonal
        ++current_diagonal;
        // Reverse the direction in the diagonal
        diagonal_left_to_right_p = !diagonal_left_to_right_p;
        // Reset the offset in the diagonal to 0
        diagonal_offset = 0;
        // Determine the new size of the diagonal
        if( current_diagonal<min_dim )
          ++diagonal_length;
        else if( current_diagonal>=max_dim)
          --diagonal_length;
      }
    }
  }

  /**
    * @brief Extract the zigzag pattern from a 2D blitz::array, as described
    * in:
    *   "Polynomial Features for Robust Face Authentication",
    *   from C. Sanderson and K. Paliwal, in the proceedings of the
    *   IEEE International Conference on Image Processing 2002.
    * @param src The input 2D blitz array
    * @param dst The output 1D blitz array. The number of coefficients kept is
    *            given by the length of this array.
    * @param right_first Set to true to reverse the initial zigzag order.
    *   By default, the direction is left-to-right for the first diagonal.
    */
  template<typename T>
  void zigzag(
    const blitz::Array<T,2>& src,
    blitz::Array<T,1>& dst,
    const bool right_first = false
  ){
    // Checks that the src and dst arrays have zero base indices
    bob::core::array::assertZeroBase( src);
    bob::core::array::assertZeroBase(dst);

    // Define constant
    const int max_n_coef = src.extent(0)*src.extent(1);
    const int n_coef_kept = dst.extent(0);

    // Check that we ask to keep a valid number of coefficients
    if( n_coef_kept < 1 || n_coef_kept > max_n_coef )
      throw std::runtime_error((boost::format("The dst array is larger than the number of pixels in the src array (%d > %d)") % n_coef_kept % max_n_coef).str());

    // Apply the zigzag function
    zigzagNoCheck( src, dst, right_first);
  }

} } } // namespaces

#endif /* BOB_IP_BASE_ZIGZAG_H */

