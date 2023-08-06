/**
 * @date Thu Mar 3 20:17:53 2011 +0100
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief This file defines functions which allows to convert/rescale a
 * blitz array of a given type into a blitz array of an other type. Typically,
 * this can be used to rescale a 16 bit precision grayscale image (2d array)
 * into an 8 bit precision grayscale image.
 * @see bob::core::scalar_cast
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_CORE_ARRAY_CONVERT_H
#define BOB_CORE_ARRAY_CONVERT_H

#include <limits>
#include <stdexcept>
#include <boost/format.hpp>
#include <blitz/array.h>
#include "assert.h"

namespace bob { namespace core { namespace array {
/**
 * @ingroup CORE_ARRAY
 * @{
 */

/**
 * @brief Function which converts a 1D blitz::array of a given type into
 * a 1D blitz::array of an other type, using the given ranges.
 */
template<typename T, typename U>
blitz::Array<T,1> convert(const blitz::Array<U,1>& src,
  T dst_min, T dst_max, U src_min, U src_max)
{
  bob::core::array::assertZeroBase(src);
  blitz::Array<T,1> dst( src.extent(0) );
  if (src_min == src_max)
    throw std::runtime_error("cannot convert an array with a zero width input range.");
  double src_ratio = 1. / ( src_max - src_min);
  T dst_diff = dst_max - dst_min;
  for (int i=0; i<src.extent(0); ++i) {
    if (src(i) < src_min) {
      boost::format m("src[%d] = %f is below the minimum %f of input range");
      m % i % src(i) % src_min;
      throw std::runtime_error(m.str());
    }
    if (src(i) > src_max) {
      boost::format m("src[%d] = %f is above the maximum %f of input range");
      m % i % src(i) % src_max;
      throw std::runtime_error(m.str());
    }
    // If the destination is an integer-like type, we need to add 0.5 s.t.
    // the round done by the implicit conversion is correct
    dst(i) = dst_min + (((src(i)-src_min)*src_ratio) *
      dst_diff + (std::numeric_limits<T>::is_integer?0.5:0));
  }
  return dst;
}

/**
 * @brief Function which converts a 2D blitz::array of a given type into
 * a 2D blitz::array of an other type, using the given ranges.
 */
template<typename T, typename U>
blitz::Array<T,2> convert(const blitz::Array<U,2>& src,
  T dst_min, T dst_max, U src_min, U src_max)
{
  bob::core::array::assertZeroBase(src);
  blitz::Array<T,2> dst( src.extent(0), src.extent(1) );
  if (src_min == src_max)
    throw std::runtime_error("cannot convert an array with a zero width input range.");
  double src_ratio = 1. / ( src_max - src_min);
  T dst_diff = dst_max - dst_min;
  for (int i=0; i<src.extent(0); ++i)
    for (int j=0; j<src.extent(1); ++j) {
      if (src(i,j) < src_min) {
        boost::format m("src[%d,%d] = %f is below the minimum %f of input range");
        m % i % j % src(i,j) % src_min;
        throw std::runtime_error(m.str());
      }
      if (src(i,j) > src_max ) {
        boost::format m("src[%d,%d] = %f is above the maximum %f of input range");
        m % i % j % src(i,j) % src_max;
        throw std::runtime_error(m.str());
      }
      // If the destination is an integer-like type, we need to add 0.5
      // s.t. the round done by the implicit conversion is correct
      dst(i,j) = dst_min + (((src(i,j)-src_min)*src_ratio) *
        dst_diff + (std::numeric_limits<T>::is_integer?0.5:0));
    }
  return dst;
}

/**
 * @brief Function which converts a 3D blitz::array of a given type into
 * a 3D blitz::array of an other type, using the given ranges.
 */
template<typename T, typename U>
blitz::Array<T,3> convert(const blitz::Array<U,3>& src,
  T dst_min, T dst_max, U src_min, U src_max)
{
  bob::core::array::assertZeroBase(src);
  blitz::Array<T,3> dst( src.extent(0), src.extent(1), src.extent(2) );
  if (src_min == src_max)
    throw std::runtime_error("cannot convert an array with a zero width input range.");
  double src_ratio = 1. / ( src_max - src_min);
  T dst_diff = dst_max - dst_min;
  for (int i=0; i<src.extent(0); ++i)
    for (int j=0; j<src.extent(1); ++j)
      for (int k=0; k<src.extent(2); ++k) {
        if (src(i,j,k) < src_min) {
          boost::format m("src[%d,%d,%d] = %f is below the minimum %f of input range");
          m % i % j % k % src(i,j,k) % src_min;
          throw std::runtime_error(m.str());
        }
        if (src(i,j,k) > src_max ) {
          boost::format m("src[%d,%d,%d] = %f is above the maximum %f of input range");
          m % i % j % k % src(i,j,k) % src_max;
          throw std::runtime_error(m.str());
        }
        // If the destination is an integer-like type, we need to add 0.5
        // s.t. the round done by the implicit conversion is correct
        dst(i,j,k) = dst_min + (((src(i,j,k)-src_min)*src_ratio) *
          dst_diff + (std::numeric_limits<T>::is_integer?0.5:0));
      }
  return dst;
}

/**
 * @brief Function which converts a 4D blitz::array of a given type into
 * a 4D blitz::array of an other type, using the given ranges.
 */
template<typename T, typename U>
blitz::Array<T,4> convert(const blitz::Array<U,4>& src,
  T dst_min, T dst_max, U src_min, U src_max)
{
  bob::core::array::assertZeroBase(src);
  blitz::Array<T,4> dst( src.extent(0), src.extent(1), src.extent(2),
    src.extent(3) );
  if (src_min == src_max)
    throw std::runtime_error("cannot convert an array with a zero width input range.");
  double src_ratio = 1. / ( src_max - src_min);
  T dst_diff = dst_max - dst_min;
  for (int i=0; i<src.extent(0); ++i)
    for (int j=0; j<src.extent(1); ++j)
      for (int k=0; k<src.extent(2); ++k)
        for (int l=0; l<src.extent(3); ++l) {
          if (src(i,j,k,l) < src_min) {
            boost::format m("src[%d,%d,%d,%d] = %f is below the minimum %f of input range");
            m % i % j % k % l % src(i,j,k,l) % src_min;
            throw std::runtime_error(m.str());
          }
          if (src(i,j,k,l) > src_max ) {
            boost::format m("src[%d,%d,%d,%d] = %f is above the maximum %f of input range");
            m % i % j % k % l % src(i,j,k,l) % src_max;
            throw std::runtime_error(m.str());
          }
          // If the destination is an integer-like type, we need to add 0.5
          // s.t. the round done by the implicit conversion is correct
          dst(i,j,k,l) = dst_min + (((src(i,j,k,l)-src_min)*src_ratio) *
            dst_diff + (std::numeric_limits<T>::is_integer?0.5:0));
        }
  return dst;
}


/**
 * @brief Function which converts a blitz::array of a given type into
 * a blitz::array of an other type, using the full type range.
 */
template<typename T, typename U, int d>
blitz::Array<T,d> convert(const blitz::Array<U,d>& src)
{
  T tmin = (std::numeric_limits<T>::is_iec559 ?
    -std::numeric_limits<T>::max() : std::numeric_limits<T>::min());
  U umin = (std::numeric_limits<U>::is_iec559 ?
    -std::numeric_limits<U>::max() : std::numeric_limits<U>::min());
  return convert<T,U>( src, tmin, std::numeric_limits<T>::max(), umin,
    std::numeric_limits<U>::max() );
}

/**
 * @brief Function which converts a blitz::array of a given type into
 * a blitz::array of an other type, using the given range for the
 * destination.
 */
template<typename T, typename U, int d>
blitz::Array<T,d> convertToRange(const blitz::Array<U,d>& src,
  T dst_min, T dst_max)
{
  U umin = (std::numeric_limits<U>::is_iec559 ?
    -std::numeric_limits<U>::max() : std::numeric_limits<U>::min());
  return convert<T,U>( src, dst_min, dst_max,
    umin, std::numeric_limits<U>::max() );
}

/**
 * @brief Function which converts a blitz::array of a given type into
 * a blitz::array of an other type, using the given range for the
 * source.
 */
template<typename T, typename U, int d>
blitz::Array<T,d> convertFromRange(const blitz::Array<U,d>& src,
  U src_min, U src_max)
{
  T tmin = (std::numeric_limits<T>::is_iec559 ?
    -std::numeric_limits<T>::max() : std::numeric_limits<T>::min());
  return convert<T,U>( src, tmin,
    std::numeric_limits<T>::max(), src_min, src_max );
}

/**
 * @}
 */
}}}

#endif /* BOB_CORE_ARRAY_CONVERT_H */

