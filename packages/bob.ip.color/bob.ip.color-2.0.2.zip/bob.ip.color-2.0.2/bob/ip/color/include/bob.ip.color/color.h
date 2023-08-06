/**
 * @date Fri Mar 25 10:02:16 2011 +0100
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Methods to convert between color spaces
 *
*/

#ifndef BOB_IP_COLOR_COLOR_H
#define BOB_IP_COLOR_COLOR_H

#include <stdexcept>
#include <stdint.h>
#include <boost/tuple/tuple.hpp>
#include <boost/format.hpp>

#include <bob.io.base/array_type.h>
#include <bob.core/assert.h>

#include <blitz/array.h>

namespace bob { namespace ip { namespace color {

  /** ------------------- **/
  /** HSV TO RGB AND BACK **/
  /** ------------------- **/

  /**
   * Converts a RGB color-pixel to HSV as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   *
   * \warning This method is just an API definition. Look for the type-specific
   * implementations in this file to understand supported types.
   */
  template <typename T> void rgb_to_hsv_one (T r, T g, T b, T& h, T& s, T& v) {
    boost::format m("rgb_to_hsv_one(): color conversion for type `%s' is not supported");
    m % bob::io::base::array::stringize<T>();
    throw std::runtime_error(m.str());
  }

  /**
   * Converts a RGB color-pixel (each band with 256 gray levels) to HSV as
   * defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void rgb_to_hsv_one (uint8_t r, uint8_t g, uint8_t b,
      uint8_t& h, uint8_t& s, uint8_t& v);

  /**
   * Converts a RGB color-pixel (each band with 65535 gray levels) to HSV as
   * defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void rgb_to_hsv_one (uint16_t r, uint16_t g, uint16_t b,
      uint16_t& h, uint16_t& s, uint16_t& v);

  /**
   * Converts a RGB color-pixel (each band as a double between 0 and 1) to HSV
   * as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void rgb_to_hsv_one (double r, double g, double b,
      double& h, double& s, double& v);

  /**
   * Converts a HSV color-coded pixel to RGB as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   *
   * \warning This method is just an API definition. Look for the type-specific
   * implementations in this file to understand supported types.
   */
  template <typename T> void hsv_to_rgb_one (T h, T s, T v, T& r, T& g, T& b) {
    boost::format m("hsv_to_rgb_one(): color conversion for type `%s' is not supported");
    m % bob::io::base::array::stringize<T>();
    throw std::runtime_error(m.str());
  }

  /**
   * Converts a HSV color-pixel (each band with 256 gray levels) to RGB as
   * defined in: http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void hsv_to_rgb_one (uint8_t h, uint8_t s, uint8_t v,
      uint8_t& r, uint8_t& g, uint8_t& b);

  /**
   * Converts a HSV color-pixel (each band with 65535 gray levels) to RGB as
   * defined in: http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void hsv_to_rgb_one (uint16_t h, uint16_t s, uint16_t v,
      uint16_t& r, uint16_t& g, uint16_t& b);

  /**
   * Converts a HSV color-pixel (each band as a double between 0 and 1) to RGB
   * as defined in: http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void hsv_to_rgb_one (double h, double s, double v,
      double& r, double& g, double& b);

  /** ------------------- **/
  /** HSL TO RGB AND BACK **/
  /** ------------------- **/

  /**
   * Converts a RGB color-pixel to HSL as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   *
   * \warning This method is just an API definition. Look for the type-specific
   * implementations in this file to understand supported types.
   */
  template <typename T> void rgb_to_hsl_one (T r, T g, T b, T& h, T& s, T& l) {
    boost::format m("rgb_to_hsl_one(): color conversion for type `%s' is not supported");
    m % bob::io::base::array::stringize<T>();
    throw std::runtime_error(m.str());
  }

  /**
   * Converts a RGB color-pixel (each band with 256 gray levels) to HSL as
   * defined in: http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void rgb_to_hsl_one (uint8_t r, uint8_t g, uint8_t b,
      uint8_t& h, uint8_t& s, uint8_t& l);

  /**
   * Converts a RGB color-pixel (each band with 65535 gray levels) to HSL as
   * defined in: http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void rgb_to_hsl_one (uint16_t r, uint16_t g, uint16_t b,
      uint16_t& h, uint16_t& s, uint16_t& l);

  /**
   * Converts a RGB color-pixel (each band as a double between 0 and 1) to HSL
   * as defined in: http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void rgb_to_hsl_one (double r, double g, double b,
      double& h, double& s, double& l);

  /**
   * Converts a HSL color-coded pixel to RGB as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   *
   * \warning This method is just an API definition. Look for the type-specific
   * implementations in this file to understand supported types.
   */
  template <typename T> void hsl_to_rgb_one (T h, T s, T l, T& r, T& g, T& b) {
    boost::format m("hsl_to_rgb_one(): color conversion for type `%s' is not supported");
    m % bob::io::base::array::stringize<T>();
    throw std::runtime_error(m.str());
  }

  /**
   * Converts a HSL color-pixel (256 gray levels) to RGB as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void hsl_to_rgb_one (uint8_t h, uint8_t s, uint8_t l,
      uint8_t& r, uint8_t& g, uint8_t& b);

  /**
   * Converts a HSL color-pixel (65535 gray levels) to RGB as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void hsl_to_rgb_one (uint16_t h, uint16_t s, uint16_t l,
      uint16_t& r, uint16_t& g, uint16_t& b);

  /**
   * Converts a HSL color-pixel (doubles between 0 and 1) to RGB as defined in:
   * http://en.wikipedia.org/wiki/HSL_and_HSV
   */
  template <> void hsl_to_rgb_one (double h, double s, double l,
      double& r, double& g, double& b);

  /** ------------------- **/
  /** YUV TO RGB AND BACK **/
  /** ------------------- **/

  /**
   * Converts a RGB color-coded pixel to YUV (Y'CbCr) using the CCIR 601 (Kb =
   * 0.114, Kr = 0.299) as discussed here: http://en.wikipedia.org/wiki/YCbCr
   * and here: http://www.fourcc.org/fccyvrgb.php
   *
   * \warning This method is just an API definition. Look for the type-specific
   * implementations in this file to understand supported types.
   */
  template <typename T> void rgb_to_yuv_one (T r, T g, T b, T& y, T& u, T& v) {
    boost::format m("rgb_to_yuv_one(): color conversion for type `%s' is not supported");
    m % bob::io::base::array::stringize<T>();
    throw std::runtime_error(m.str());
  }

  /**
   * Converts a RGB color-coded pixel (3-bands each with 256 levels of gray) to
   * YUV (Y'CbCr) using the CCIR 601 (Kb = 0.114, Kr = 0.299) norm as discussed
   * here: http://en.wikipedia.org/wiki/YCbCr and here:
   * http://www.fourcc.org/fccyvrgb.php
   *
   * \warning This implementation returns U and V values varying from 0 to the
   * maximum range for mapping norm ranges [-0.5, 0.5] into unsigned integer
   * values.
   */
  template <> void rgb_to_yuv_one (uint8_t r, uint8_t g, uint8_t b,
      uint8_t& y, uint8_t& u, uint8_t& v);

  /**
   * Converts a RGB color-coded pixel (3-bands each with 65535 levels of gray)
   * to YUV (Y'CbCr) using the CCIR 601 (Kb = 0.114, Kr = 0.299) norm as
   * discussed here: http://en.wikipedia.org/wiki/YCbCr and here:
   * http://www.fourcc.org/fccyvrgb.php
   *
   * \warning This implementation returns U and V values varying from 0 to the
   * maximum range for mapping norm ranges [-0.5, 0.5] into unsigned integer
   * values.
   */
  template <> void rgb_to_yuv_one (uint16_t r, uint16_t g, uint16_t b,
      uint16_t& y, uint16_t& u, uint16_t& v);

  /**
   * Converts a RGB color-coded pixel (3-bands of doubles between 0 and 1) to
   * YUV (Y'CbCr) using the CCIR 601 (Kb = 0.114, Kr = 0.299) norm as discussed
   * here: http://en.wikipedia.org/wiki/YCbCr and here:
   * http://www.fourcc.org/fccyvrgb.php
   *
   * \warning This implementation returns U and V values varying from 0 to 1
   * for mapping norm ranges [-0.5, 0.5] into a more standard setting.
   */
  template <> void rgb_to_yuv_one (double r, double g, double b,
      double& y, double& u, double& v);

  /**
   * Converts a YUV (Y'CbCr) color-coded pixel using the CCIR 601 (Kb = 0.114,
   * Kr = 0.299) to RGB as discussed here: http://en.wikipedia.org/wiki/YCbCr
   * and here: http://www.fourcc.org/fccyvrgb.php
   *
   * \warning This method is just an API definition. Look for the type-specific
   * implementations in this file to understand supported types.
   */
  template <typename T> void yuv_to_rgb_one (T y, T u, T v, T& r, T& g, T& b) {
    boost::format m("yuv_to_rgb_one(): color conversion for type `%s' is not supported");
    m % bob::io::base::array::stringize<T>();
    throw std::runtime_error(m.str());
  }

  /**
   * Converts a YUV (Y'CbCr) color-coded pixel (3-bands each with 256 levels of
   * gray) using the CCIR 601 (Kb = 0.114, Kr = 0.299) to RGB as discussed
   * here: http://en.wikipedia.org/wiki/YCbCr and here:
   * http://www.fourcc.org/fccyvrgb.php
   */
  template <> void yuv_to_rgb_one (uint8_t y, uint8_t u, uint8_t v,
      uint8_t& r, uint8_t& g, uint8_t& b);

  /**
   * Converts a YUV (Y'CbCr) color-coded pixel (3-bands each with 65535 levels
   * of gray) using the CCIR 601 (Kb = 0.114, Kr = 0.299) to RGB as discussed
   * here: http://en.wikipedia.org/wiki/YCbCr and here:
   * http://www.fourcc.org/fccyvrgb.php
   */
  template <> void yuv_to_rgb_one (uint16_t y, uint16_t u, uint16_t v,
      uint16_t& r, uint16_t& g, uint16_t& b);

  /**
   * Converts a YUV (Y'CbCr) color-coded pixel (3-bands of doubles between 0 and
   * 1) using the CCIR 601 (Kb = 0.114, Kr = 0.299) to RGB as discussed here:
   * http://en.wikipedia.org/wiki/YCbCr and here:
   * http://www.fourcc.org/fccyvrgb.php
   */
  template <> void yuv_to_rgb_one (double y, double u, double v,
      double& r, double& g, double& b);

  /** ------------------------- **/
  /** Grayscale TO RGB AND BACK **/
  /** ------------------------- **/

  /**
   * Converts a RGB color-coded pixel to grayscale using the CCIR 601 (Kb =
   * 0.114, Kr = 0.299) "Y'" (luma) component conversion.
   *
   * \warning This method is just an API definition. Look for the type-specific
   * implementations in this file to understand supported types.
   */
  template <typename T> void rgb_to_gray_one (T r, T g, T b, T& gray) {
    boost::format m("rgb_to_gray_one(): color conversion for type `%s' is not supported");
    m % bob::io::base::array::stringize<T>();
    throw std::runtime_error(m.str());
  }

  /**
   * Converts a RGB color-coded pixel (256 levels of gray) to grayscale using
   * the CCIR 601 (Kb = 0.114, Kr = 0.299) "Y'" (luma) component conversion as
   * discussed here: http://www.fourcc.org/fccyvrgb.php
   */
  template <> void rgb_to_gray_one (uint8_t r, uint8_t g, uint8_t b, uint8_t& gray);

  /**
   * Converts a RGB color-coded pixel (65535 levels of gray) to grayscale using
   * the CCIR 601 (Kb = 0.114, Kr = 0.299) "Y'" (luma) component conversion as
   * discussed here: http://www.fourcc.org/fccyvrgb.php
   */
  template <> void rgb_to_gray_one (uint16_t r, uint16_t g, uint16_t b, uint16_t& gray);

  /**
   * Converts a RGB color-coded pixel (each band as a double between 0 and 1) to
   * grayscale using the CCIR 601 (Kb = 0.114, Kr = 0.299) "Y'" (luma)
   * component conversion as discussed here: http://www.fourcc.org/fccyvrgb.php
   */
  template <> void rgb_to_gray_one (double r, double g, double b, double& gray);

  /**
   * Converts a grayscale pixel to RGB by copying all components:
   * R = G = B = Grayscale Value
   */
  template <typename T> void gray_to_rgb_one (T gray, T& r, T& g, T& b) {
    //special case where it is an obvious conversion, we let the template do it
    r = g = b = gray;
  }

  /** --------------------- **/
  /** Blitz array converter **/
  /** --------------------- **/

  /**
   * Takes a 3-dimensional array encoded as RGB and sets the second array with
   * HSV equivalents as determined by rgb_to_hsv_one(). The array must be
   * organized in such a way that the color bands are represented by the first
   * dimension.  Its shape should be something like (3, width, height) or (3,
   * height, width). The output array will be checked for shape conformity.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void rgb_to_hsv (const blitz::Array<T,3>& from,
      blitz::Array<T,3>& to) {
    if (from.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % from.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameShape(from, to);
    for (int j=0; j<from.extent(1); ++j)
      for (int k=0; k<from.extent(2); ++k)
        rgb_to_hsv_one(from(0,j,k), from(1,j,k), from(2,j,k),
                       to(0,j,k), to(1,j,k), to(2,j,k));
  }

  /**
   * Takes a 3-dimensional array encoded as HSV and sets the second array with
   * RGB equivalents as determined by hsv_to_rgb_one(). The array must be
   * organized in such a way that the color bands are represented by the first
   * dimension.  Its shape should be something like (3, width, height) or (3,
   * height, width). The output array will be checked for shape conformity.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void hsv_to_rgb (const blitz::Array<T,3>& from,
      blitz::Array<T,3>& to) {
    if (from.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % from.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameShape(from, to);
    for (int j=0; j<from.extent(1); ++j)
      for (int k=0; k<from.extent(2); ++k)
        hsv_to_rgb_one(from(0,j,k), from(1,j,k), from(2,j,k),
                       to(0,j,k), to(1,j,k), to(2,j,k));
  }

  /**
   * Takes a 3-dimensional array encoded as RGB and sets the second array with
   * HSL equivalents as determined by rgb_to_hsl_one(). The array must be
   * organized in such a way that the color bands are represented by the first
   * dimension.  Its shape should be something like (3, width, height) or (3,
   * height, width). The output array will be checked for shape conformity.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void rgb_to_hsl (const blitz::Array<T,3>& from,
      blitz::Array<T,3>& to) {
    if (from.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % from.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameShape(from, to);
    for (int j=0; j<from.extent(1); ++j)
      for (int k=0; k<from.extent(2); ++k)
        rgb_to_hsl_one(from(0,j,k), from(1,j,k), from(2,j,k),
                       to(0,j,k), to(1,j,k), to(2,j,k));
  }

  /**
   * Takes a 3-dimensional array encoded as HSV and sets the second array with
   * RGB equivalents as determined by hsl_to_rgb_one(). The array must be
   * organized in such a way that the color bands are represented by the first
   * dimension.  Its shape should be something like (3, width, height) or (3,
   * height, width). The output array will be checked for shape conformity.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void hsl_to_rgb (const blitz::Array<T,3>& from,
      blitz::Array<T,3>& to) {
    if (from.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % from.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameShape(from, to);
    for (int j=0; j<from.extent(1); ++j)
      for (int k=0; k<from.extent(2); ++k)
        hsl_to_rgb_one(from(0,j,k), from(1,j,k), from(2,j,k),
                       to(0,j,k), to(1,j,k), to(2,j,k));
  }

  /**
   * Takes a 3-dimensional array encoded as RGB and sets the second array with
   * YUV (Y'CbCr) equivalents as determined by rgb_to_yuv_one(). The array must
   * be organized in such a way that the color bands are represented by the
   * first dimension.  Its shape should be something like (3, width, height) or
   * (3, height, width). The output array will be automatically resized if
   * required.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void rgb_to_yuv (const blitz::Array<T,3>& from,
      blitz::Array<T,3>& to) {
    if (from.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % from.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameShape(from, to);
    for (int j=0; j<from.extent(1); ++j)
      for (int k=0; k<from.extent(2); ++k)
        rgb_to_yuv_one(from(0,j,k), from(1,j,k), from(2,j,k),
                       to(0,j,k), to(1,j,k), to(2,j,k));
  }

  /**
   * Takes a 3-dimensional array encoded as YUV (Y'CbCr) and sets the second
   * array with RGB equivalents as determined by yuv_to_rgb_one(). The array
   * must be organized in such a way that the color bands are represented by
   * the first dimension.  Its shape should be something like (3, width,
   * height) or (3, height, width). The output array will be checked for shape
   * conformity.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void yuv_to_rgb (const blitz::Array<T,3>& from,
      blitz::Array<T,3>& to) {
    if (from.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % from.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameShape(from, to);
    for (int j=0; j<from.extent(1); ++j)
      for (int k=0; k<from.extent(2); ++k)
        yuv_to_rgb_one(from(0,j,k), from(1,j,k), from(2,j,k),
                       to(0,j,k), to(1,j,k), to(2,j,k));
  }

  /**
   * Takes a 3-dimensional array encoded as RGB and sets the second array with
   * gray equivalents as determined by rgb_to_gray_one(). The array must be
   * organized in such a way that the color bands are represented by the first
   * dimension. Its shape should be something like (3, width, height) or (3,
   * height, width). The output array is a 2D array with the same element type.
   * The output array will be checked for shape conformity.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void rgb_to_gray (const blitz::Array<T,3>& from,
      blitz::Array<T,2>& to) {
    if (from.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % from.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameDimensionLength(from.extent(1), to.extent(0));
    bob::core::array::assertSameDimensionLength(from.extent(2), to.extent(1));
    for (int j=0; j<from.extent(1); ++j)
      for (int k=0; k<from.extent(2); ++k)
        rgb_to_gray_one(from(0,j,k), from(1,j,k), from(2,j,k), to(j,k));
  }

  /**
   * Takes a 2-dimensional array encoded as grays and sets the second array
   * with RGB equivalents as determined by gray_to_rgb_one(). The output array
   * will be checked for shape conformity.
   *
   * \warning As of this time only C-style storage arrays are supported
   */
  template <typename T> void gray_to_rgb (const blitz::Array<T,2>& from,
      blitz::Array<T,3>& to) {
    if (to.extent(0) != 3) {
      boost::format m("color conversion requires an array with size 3 on the first dimension, but I got one with size %d instead");
      m % to.extent(0);
      throw std::runtime_error(m.str());
    }
    bob::core::array::assertSameDimensionLength(to.extent(1), from.extent(0));
    bob::core::array::assertSameDimensionLength(to.extent(2), from.extent(1));
    for (int j=0; j<to.extent(1); ++j)
      for (int k=0; k<to.extent(2); ++k)
        gray_to_rgb_one(from(j,k), to(0,j,k), to(1,j,k), to(2,j,k));
  }

} } } // namespaces

#endif /* BOB_IP_COLOR_COLOR_H */

