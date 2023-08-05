/**
 * @date Tue Apr 26 19:20:57 2011 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 * @author Tiago Freitas Pereira <Tiago.Pereira@idiap.ch>
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * This class can be used to calculate the LBP-Top  of a set of image frames
 * representing a video sequence (c.f. Dynamic Texture Recognition Using Local
 * Binary Patterns with an Application to Facial Expression from Zhao &
 * Pietikäinen, IEEE Trans. on PAMI, 2007)
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IP_BASE_LBPTOP_H
#define BOB_IP_BASE_LBPTOP_H

#include <boost/shared_ptr.hpp>
#include <blitz/array.h>
#include <algorithm>
#include <limits>

#include <bob.ip.base/LBP.h>

namespace bob { namespace ip { namespace base {

  /**
   * The LBPTop class is designed to calculate the LBP-Top
   * coefficients given a set of images.
   *
   * The workflow is as follows:
   * TODO: UPDATE as this is not true
   * 1. You initialize the class, defining the radius and number of points
   * in each of the three directions: XY, XT, YT for the LBP calculations
   * 2. For each image you have in the frame sequence, you push into the
   * class
   * 3. An internal FIFO queue (length = radius in T direction) keeps track
   * of the current image and their order. As a new image is pushed in, the
   * oldest on the queue is pushed out.
   * 4. After pushing an image, you read the current LBP-Top coefficients
   * and may save it somewhere.
   */
  class LBPTop {

    public:

      /**
       * Constructs a new LBPTop object starting from the algorithm
       * configuration
       *
       * @param lbp_xy The 2D LBP-XY plane configuration
       * @param lbp_xt The 2D LBP-XT plane configuration
       * @param lbp_yt The 2D LBP-YT plane configuration
       */
      LBPTop(boost::shared_ptr<LBP> lbp_xy,
             boost::shared_ptr<LBP> lbp_xt,
             boost::shared_ptr<LBP> lbp_yt);

      /**
       * Copy constructor
       */
      LBPTop(const LBPTop& other);

      /**
       * Destructor
       */
      virtual ~LBPTop();

      /**
       * Assignment
       */
      LBPTop& operator= (const LBPTop& other);

      /**
       * Processes a 3D array representing a set of <b>grayscale</b> images and
       * returns (by argument) the three LBP planes calculated. The 3D array
       * has to be arranged in this way:
       *
       * 1st dimension => time
       * 2nd dimension => frame height
       * 3rd dimension => frame width
       *
       * @param src The input 3D array as described in the documentation of
       * this method.
       * @param xy The result of the LBP operator in the XY plane (frame), for
       * the central frame of the input array. This is an image.
       * @param xt The result of the LBP operator in the XT plane for the whole
       * image, taking into consideration the size of the width of the input
       * array along the time direction.
       * @param yt The result of the LBP operator in the YT plane for the whole
       * image, taking into consideration the size of the width of the input
       * array along the time direction.
       */
      template <typename T>
        void process(const blitz::Array<T,3>& src,
            blitz::Array<uint16_t,3>& xy,
            blitz::Array<uint16_t,3>& xt,
            blitz::Array<uint16_t,3>& yt) const;

      /**
       * Accessors
       */

      /**
       * Returns the XY plane LBP operator
       */
      const boost::shared_ptr<LBP> getXY() const {
        return m_lbp_xy;
      }

      /**
       * Returns the XT plane LBP operator
       */
      const boost::shared_ptr<LBP> getXT() const {
        return m_lbp_xt;
      }

      /**
       * Returns the YT plane LBP operator
       */
      const boost::shared_ptr<LBP> getYT() const {
        return m_lbp_yt;
      }

    private: //representation and methods

      boost::shared_ptr<LBP> m_lbp_xy; ///< LBP for the XY calculation
      boost::shared_ptr<LBP> m_lbp_xt; ///< LBP for the XT calculation
      boost::shared_ptr<LBP> m_lbp_yt; ///< LBP for the YT calculation
  };

  /**
   * Implementation of certain template methods.
   */

  template <typename T>
    void LBPTop::process(
        const blitz::Array<T,3>& src,
        blitz::Array<uint16_t,3>& xy,
        blitz::Array<uint16_t,3>& xt,
        blitz::Array<uint16_t,3>& yt
    ) const
    {
      int radius_x = m_lbp_xy->getRadii()[0];  ///< The LBPu2,i radius in X direction
      int radius_y = m_lbp_xy->getRadii()[1];  ///< The LBPu2,i radius in Y direction
      int radius_t = m_lbp_yt->getRadii()[1];  ///< The LBPu2,i radius in T direction

      int Tlength = src.extent(0);
      int height = src.extent(1);
      int width = src.extent(2);

      /***** Checking the inputs *****/
      /**** Get XY plane (the first is enough) ****/

      const blitz::Array<T,2> checkXY = src( 0, blitz::Range::all(), blitz::Range::all());
      m_lbp_xy->extract(checkXY, radius_x, radius_y);

      /**** Get XT plane (Intersect in one point is enough) ****/
      int limitT = ceil(2*radius_t + 1);
      if( Tlength < limitT ) {
        boost::format m("t_radius (%d) cannot be smaller than %d");
        m % Tlength % limitT;
        throw std::runtime_error(m.str());
      }

      /***** Checking the outputs *****/
      int max_radius = radius_x > radius_y ? radius_x : radius_y;
      max_radius = max_radius > radius_t ? max_radius : radius_t;
      int limitWidth  = width-2*max_radius;
      int limitHeight = height-2*max_radius;
      int limitTime   = Tlength-2*max_radius;

      /*Checking XY*/
      if( xy.extent(0) != limitTime) {
        boost::format m("time parameter in direction XY (%d) has to be %d");
        m % xy.extent(0) % limitTime;
        throw std::runtime_error(m.str());
      }
      if( xy.extent(1) != limitHeight) {
        boost::format m("height parameter in direction XY = %d has to be %d");
        m % xy.extent(1) % limitHeight;
        throw std::runtime_error(m.str());
      }
      if( xy.extent(2) != limitWidth) {
        boost::format m("width parameter in direction XY = %d has to be %d");
        m % xy.extent(2) % limitWidth;
        throw std::runtime_error(m.str());
      }

      /*Checking XT*/
      if( xt.extent(0) != limitTime) {
        boost::format m("time parameter in direction XT = %d has to be %d");
        m % xt.extent(0) % limitTime;
        throw std::runtime_error(m.str());
      }
      if( xt.extent(1) != limitHeight) {
        boost::format m("height parameter in direction XT = %d has to be %d");
        m % xt.extent(1) % limitHeight;
        throw std::runtime_error(m.str());
      }
      if( xt.extent(2) != limitWidth) {
        boost::format m("width parameter in direction XT = %d has to be %d");
        m % xt.extent(2) % limitWidth;
        throw std::runtime_error(m.str());
      }

      /*Checking YT*/
      if( yt.extent(0) != limitTime) {
        boost::format m("time parameter in direction YT = %d has to be %d");
        m % yt.extent(0) % limitTime;
        throw std::runtime_error(m.str());
      }
      if( yt.extent(1) != limitHeight) {
        boost::format m("height parameter in direction YT = %d has to be %d");
        m % yt.extent(1) % limitHeight;
        throw std::runtime_error(m.str());
      }
      if( yt.extent(2) != limitWidth) {
        boost::format m("width parameter in direction YT = %d has to be %d");
        m % yt.extent(2) % limitWidth;
        throw std::runtime_error(m.str());
      }

      //for each element in time domain (the simplest way to see what is happening)
      for(int i=max_radius;i<(Tlength-max_radius);i++){
        for (int j=max_radius; j < (height-max_radius); j++) {
          for (int k=max_radius; k < (width-max_radius); k++) {
            /*Getting the "micro-plane" for XY calculus*/
            const blitz::Array<T,2> kxy =
               src( i, blitz::Range(j-max_radius,j+max_radius), blitz::Range(k-max_radius,k+max_radius));
            xy(i-max_radius,j-max_radius,k-max_radius) = m_lbp_xy->extract(kxy, max_radius, max_radius);

            /*Getting the "micro-plane" for XT calculus*/
            const blitz::Array<T,2> kxt =
               src(blitz::Range(i-max_radius,i+max_radius),j,blitz::Range(k-max_radius,k+max_radius));
            xt(i-max_radius,j-max_radius,k-max_radius) = m_lbp_xt->extract(kxt, max_radius, max_radius);

            /*Getting the "micro-plane" for YT calculus*/
            const blitz::Array<T,2> kyt =
               src(blitz::Range(i-max_radius,i+max_radius),blitz::Range(j-max_radius,j+max_radius),k);
            yt(i-max_radius,j-max_radius,k-max_radius) = m_lbp_yt->extract(kyt, max_radius, max_radius);
          }
        }
      }
    }
} } } // namespaces

#endif /* BOB_IP_BASE_LBPTOP_H */
