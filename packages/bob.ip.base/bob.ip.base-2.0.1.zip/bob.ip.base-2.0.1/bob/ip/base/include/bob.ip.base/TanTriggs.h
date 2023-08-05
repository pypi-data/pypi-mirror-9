/**
 * @date Fri Mar 18 18:09:25 2011 +0100
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief This file provides a class to perform Tan and Triggs preprocessing.
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IP_BASE_TAN_TRIGGS_H
#define BOB_IP_BASE_TAN_TRIGGS_H

#include <bob.core/assert.h>
#include <bob.sp/conv.h>
#include <bob.sp/extrapolate.h>

namespace bob { namespace ip { namespace base {

  /**
    * @brief Function which performs a gamma correction on a 2D
    *   blitz::array/image of a given type.
    *   The first dimension is the height (y-axis), whereas the second
    *   one is the width (x-axis).
    * @param src The input blitz array
    * @param dst The output blitz array (always double)
    * @param gamma The gamma value for power-law gamma correction
    */
  template<typename T>
  void gammaCorrection(
    const blitz::Array<T,2>& src,
    blitz::Array<double,2>& dst,
    const double gamma
  ){
    // Check input/output
    bob::core::array::assertZeroBase(src);
    bob::core::array::assertZeroBase(dst);
    bob::core::array::assertSameShape(dst, src);

    // Check parameters and throw exception if required
    if( gamma < 0.)  throw std::runtime_error((boost::format("parameter `gamma' was set to %f, but should be greater or equal zero") % gamma).str());

    // Perform gamma correction for the 2D array
    dst = blitz::pow(src, gamma);
  }


  /**
   * @brief This class can be used to perform Tan and Triggs preprocessing.
   *   This algorithm is described in the following articles:
   *    1) "Enhanced Local Texture Feature Sets for Face Recognition Under
   *         Difficult Lighting Conditions", from Xiaoyang Tan and Bill Triggs,
   *       in the proceedings of IEEE International Workshop on Analysis and
   *       Modelling of Faces and Gestures (AMFG), 2007, p. 162-182.
   *    2) "Enhanced Local Texture Feature Sets for Face Recognition Under
   *         Difficult Lighting Conditions", from Xiaoyang Tan and Bill Triggs,
   *       in IEEE Transactions on Image Processing, June 2010, Issue 6,
   *       Volume 19, p. 1635-1650.
   *       (http://ieeexplore.ieee.org/xpl/freeabs_all.jsp?arnumber=5411802)
  */
  class TanTriggs
  {
    public:

      /**
       * @brief Creates an object to preprocess images using the algorithm of
       *  Tan and Triggs.
       * @param gamma The gamma value for the Gamma correction
       * @param sigma0 The standard deviation of the inner Gaussian of the
       *  DOG filter
       * @param sigma1 The standard deviation of the outer Gaussian of the
       *  DOG filter
       * @param radius The radius (kernel_size=2*radius+1) of the kernel along
       *  both axes
       * @param threshold threshold value used for the contrast equalization
       * @param alpha alpha value used for the contrast equalization
       * @param border_type The interpolation type for the convolution
       */
      TanTriggs(
        const double gamma=0.2,
        const double sigma0=1.,
        const double sigma1=2.,
        const size_t radius=2,
        const double threshold=10.,
        const double alpha=0.1,
        const bob::sp::Extrapolation::BorderType border_type=bob::sp::Extrapolation::Mirror
      );

      /**
       * @brief Copy constructor
       */
      TanTriggs(const TanTriggs& other);

      /**
        * @brief Destructor
        */
      virtual ~TanTriggs() { }

      /**
       * @brief Assignment operator
       */
      TanTriggs& operator=(const TanTriggs& other);

      /**
       * @brief Equal to
       */
      bool operator==(const TanTriggs& b) const;
      /**
       * @brief Not equal to
       */
      bool operator!=(const TanTriggs& b) const;

      /**
       * @brief Resets the parameters of the filter
       * @param gamma The gamma value for the Gamma correction
       * @param sigma0 The standard deviation of the inner Gaussian of the
       *  DOG filter
       * @param sigma1 The standard deviation of the outer Gaussian of the
       *  DOG filter
       * @param radius The radius (kernel_size=2*radius+1) of the kernel along
       *  both axes
       * @param threshold threshold value used for the contrast equalization
       * @param alpha alpha value used for the contrast equalization
       * @param border_type The interpolation type for the convolution
       */
      void reset(
        const double gamma=0.2,
        const double sigma0=1.,
        const double sigma1=2.,
        const size_t radius=2,
        const double threshold=10.,
        const double alpha=0.1,
        const bob::sp::Extrapolation::BorderType
        border_type=bob::sp::Extrapolation::Mirror
      );

      /**
       * @brief Getters
       */
      double getGamma() const { return m_gamma; }
      double getSigma0() const { return m_sigma0; }
      double getSigma1() const { return m_sigma1; }
      size_t getRadius() const { return m_radius; }
      double getThreshold() const { return m_threshold; }
      double getAlpha() const { return m_alpha; }
      bob::sp::Extrapolation::BorderType getConvBorder() const { return m_border_type; }
      const blitz::Array<double,2>& getKernel() const { return m_kernel; }

      /**
       * @brief Setters
       */
      void setGamma(const double gamma) { m_gamma = gamma; }
      void setSigma0(const double sigma0) { m_sigma0 = sigma0; computeDoG(m_sigma0, m_sigma1, 2*m_radius+1); }
      void setSigma1(const double sigma1) { m_sigma1 = sigma1; computeDoG(m_sigma0, m_sigma1, 2*m_radius+1); }
      void setRadius(const size_t radius) { m_radius = radius; computeDoG(m_sigma0, m_sigma1, 2*m_radius+1); }
      void setThreshold(const double threshold) { m_threshold = threshold; }
      void setAlpha(const double alpha) { m_alpha = alpha; }
      void setConvBorder(const bob::sp::Extrapolation::BorderType border_type) { m_border_type = border_type; }

      /**
        * @brief Process a 2D blitz Array/Image by applying the preprocessing
        * algorihtm
        */
      template <typename T> void process(const blitz::Array<T,2>& src, blitz::Array<double,2>& dst)
      {
        // Check input and output arrays
        bob::core::array::assertZeroBase(src);
        bob::core::array::assertZeroBase(dst);
        bob::core::array::assertSameShape(src, dst);

        // Check and resize intermediate array if required
        if (m_img_tmp.extent(0) != src.extent(0) || m_img_tmp.extent(1) != src.extent(1))
          m_img_tmp.resize( src.extent(0), src.extent(1) );

        // 1/ Perform gamma correction
        if( m_gamma > 0.)
          bob::ip::base::gammaCorrection( src, m_img_tmp, m_gamma);
        else
          m_img_tmp = blitz::log( 1. + src );

        // 2/ Convolution with the DoG Filter
        if (m_border_type == bob::sp::Extrapolation::Zero)
          sp::conv( m_img_tmp, m_kernel, dst, bob::sp::Conv::Same);
        else {
          m_img_tmp2.resize(bob::sp::getConvOutputSize(m_img_tmp, m_kernel, bob::sp::Conv::Full));
          if (m_border_type == bob::sp::Extrapolation::NearestNeighbour)
            bob::sp::extrapolateNearest(m_img_tmp, m_img_tmp2);
          else if (m_border_type == bob::sp::Extrapolation::Circular)
            bob::sp::extrapolateCircular(m_img_tmp, m_img_tmp2);
          else
            bob::sp::extrapolateMirror(m_img_tmp, m_img_tmp2);
          bob::sp::conv( m_img_tmp2, m_kernel, dst, bob::sp::Conv::Valid);
        }

        // 3/ Perform contrast equalization
        performContrastEqualization(dst);
      }


    private:
      /**
        * @brief Perform the contrast equalization step on a 2D blitz
        * Array/Image.
        */
      void performContrastEqualization( blitz::Array<double,2>& img);

      /**
        * @brief Generate the difference of Gaussian filter
        */
      void computeDoG(double sigma0, double sigma1, size_t size);

      // Attributes
      blitz::Array<double, 2> m_kernel;
      blitz::Array<double, 2> m_img_tmp;
      blitz::Array<double, 2> m_img_tmp2;
      double m_gamma;
      double m_sigma0;
      double m_sigma1;
      size_t m_radius;
      double m_threshold;
      double m_alpha;
      bob::sp::Extrapolation::BorderType m_border_type;
  };

} } } // namespaces

#endif /* BOB_IP_BASE_TAN_TRIGGS_H */

