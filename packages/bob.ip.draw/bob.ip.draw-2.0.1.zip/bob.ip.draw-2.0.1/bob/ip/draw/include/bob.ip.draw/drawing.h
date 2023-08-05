/**
 * @date Sun Jul 24 21:13:21 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Methods to draw lines, points and simple things on images
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IP_DRAW_DRAWING_H
#define BOB_IP_DRAW_DRAWING_H

#include <stdexcept>
#include <algorithm>
#include <blitz/array.h>
#include <boost/tuple/tuple.hpp>

namespace bob { namespace ip { namespace draw {

  /**
   * Draws a point in the 2D gray-scale image. No checks, if you try to access
   * an area outside the image using this method, you may trigger a
   * segmentation fault.
   */
  template <typename T>
  void draw_point_ (blitz::Array<T,2>& image, int y, int x, T color) {
    image(y,x) = color;
  }

  /**
   * Draws a point in the 3D colored image. No checks, if you try to access an
   * area outside the image using this method, you may trigger a segmentation
   * fault.
   */
  template <typename T>
  void draw_point_ (blitz::Array<T,3>& image, int y, int x,
      const boost::tuple<T,T,T>& color) {
    image(0,y,x) = boost::get<0>(color);
    image(1,y,x) = boost::get<1>(color);
    image(2,y,x) = boost::get<2>(color);
  }

  /**
   * Draws a point in the given image. Trying to access outside the image range
   * will trigger a std::range_error.
   */
  template <typename T>
  void draw_point (blitz::Array<T,2>& image, int y, int x, T color) {
    if (x >= image.extent(1) || y >= image.extent(0))
      throw std::out_of_range("out of range");
    draw_point_(image, y, x, color);
  }

  /**
   * Draws a point in the given image. Trying to access outside the image range
   * will trigger a std::range_error.
   */
  template <typename T>
  void draw_point (blitz::Array<T,3>& image, int y, int x,
      const boost::tuple<T,T,T>& color) {
    if (x >= image.extent(2) || y >= image.extent(1))
      throw std::out_of_range("out of range");
    draw_point_(image, y, x, color);
  }

  /**
   * Tries to draw a point at the given image. If the point is out of range,
   * just ignores the request. This is what is used for drawing lines.
   */
  template <typename T>
  void try_draw_point (blitz::Array<T,2>& image, int y, int x, T color) {
    if (x < 0 || y < 0 || x >= image.extent(1) || y >= image.extent(0)) return;
    draw_point_(image, y, x, color);
  }

  /**
   * Tries to draw a point at the given image. If the point is out of range,
   * just ignores the request. This is what is used for drawing lines.
   */
  template <typename T>
  void try_draw_point (blitz::Array<T,3>& image, int y, int x,
      const boost::tuple<T,T,T>& color) {
    if (x < 0 || y < 0 || x >= image.extent(2) || y >= image.extent(1)) return;
    draw_point_(image, y, x, color);
  }

  /**
   * Draws a line between two points p1(p1x,p1y) and p2(p2x,p2y).  This
   * function is based on the Bresenham's line algorithm and is highly
   * optimized to be able to draw lines very quickly. There is no floating
   * point arithmetic nor multiplications and divisions involved. Only
   * addition, subtraction and bit shifting are used.
   *
   * The line may go out of the image bounds in which case such points (lying
   * outside the image boundary are ignored).
   *
   * References:
   * http://en.wikipedia.org/wiki/Bresenham's_line_algorithm
   */
  template <typename ImageType, typename ColorType>
  void draw_line (ImageType& image, int p1y, int p1x,
      int p2y, int p2x, const ColorType& color) {

    int F, x, y;

    if (p1x > p2x) {
      // Swap points if p1 is on the right of p2
      std::swap(p1x, p2x);
      std::swap(p1y, p2y);
    }

    // Handle trivial cases separately for algorithm speed up.
    // Trivial case 1: m = +/-INF (Vertical line)
    if (p1x == p2x) {

      if (p1y > p2y) {
        // Swap y-coordinates if p1 is above p2
        std::swap(p1y, p2y);
      }

      x = p1x;
      y = p1y;
      while (y <= p2y) {
        try_draw_point(image, y, x, color);
        ++y;
      }
      return;
    }

    // Trivial case 2: m = 0 (Horizontal line)
    else if (p1y == p2y) {
      x = p1x;
      y = p1y;

      while (x <= p2x) {
        try_draw_point(image, y, x, color);
        ++x;
      }
      return;
    }

    int dy            = p2y - p1y;  // y-increment from p1 to p2
    int dx            = p2x - p1x;  // x-increment from p1 to p2
    int dy2           = (dy << 1);  // dy << 1 == 2*dy
    int dx2           = (dx << 1);
    int dy2_minus_dx2 = dy2 - dx2;  // precompute constant for speed up
    int dy2_plus_dx2  = dy2 + dx2;

    if (dy >= 0) { // m >= 0

      // Case 1: 0 <= m <= 1 (Original case)
      if (dy <= dx) {
        F = dy2 - dx; // initial F

        x = p1x;
        y = p1y;
        while (x <= p2x) {
          try_draw_point(image, y, x, color);
          if (F <= 0) {
            F += dy2;
          }
          else {
            y++;
            F += dy2_minus_dx2;
          }
          x++;
        }
      }

      // Case 2: 1 < m < INF (Mirror about y=x line
      // replace all dy by dx and dx by dy)
      else {
        F = dx2 - dy; // initial F

        y = p1y;
        x = p1x;
        while (y <= p2y) {
          try_draw_point(image, y, x, color);
          if (F <= 0) {
            F += dx2;
          }
          else {
            x++;
            F -= dy2_minus_dx2;
          }
          y++;
        }
      }
    }
    else { // m < 0

      // Case 3: -1 <= m < 0 (Mirror about x-axis, replace all dy by -dy)
      if (dx >= -dy) {
        F = -dy2 - dx; // initial F

        x = p1x;
        y = p1y;
        while (x <= p2x) {
          try_draw_point(image, y, x, color);
          if (F <= 0) {
            F -= dy2;
          }
          else {
            y--;
            F -= dy2_plus_dx2;
          }
          x++;
        }
      }

      // Case 4: -INF < m < -1 (Mirror about x-axis and mirror
      // about y=x line, replace all dx by -dy and dy by dx)
      else {
        F = dx2 + dy; // initial F

        y = p1y;
        x = p1x;
        while (y >= p2y) {
          try_draw_point(image, y, x, color);
          if (F <= 0)
          {
            F += dx2;
          }
          else
          {
            x++;
            F += dy2_plus_dx2;
          }
          y--;
        }
      }
    }

  }

  /**
   * Draws a cross with a given radius and color at the image. Uses the
   * draw_line() primitive above. The cross will look like an 'x' and not like
   * a '+'. To get a '+' sign, use the draw_cross_plus() variant.
   */
  template <typename ImageType, typename ColorType>
  void draw_cross (ImageType& image, int y, int x, size_t radius,
      const ColorType& color) {
    draw_line(image, y-radius, x-radius, y+radius, x+radius, color);
    draw_line(image, y+radius, x-radius, y-radius, x+radius, color);
  }

  /**
   * Draws a cross with a given radius and color at the image. Uses the
   * draw_line() primitive above. The cross will look like an '+' and not like
   * a 'x'. To get an 'x' sign, use the draw_cross() variant.
   */
  template <typename ImageType, typename ColorType>
  void draw_cross_plus (ImageType& image, int y, int x, int radius,
      const ColorType& color) {
    draw_line(image, y-radius, x, y+radius, x, color);
    draw_line(image, y, x-radius, y, x+radius, color);
  }

  /**
   * Draws a box at the image using the draw_line() primitive above.
   */
  template <typename ImageType, typename ColorType>
  void draw_box (ImageType& image, int y, int x, size_t height,
      size_t width, const ColorType& color) {
    draw_line(image, y, x, y, x + width, color);
    draw_line(image, y + height, x, y+ height, x + width, color);
    draw_line(image, y, x, y + height, x, color);
    draw_line(image, y, x + width, y + height, x + width, color);
  }

} } } // namespaces

#endif /* BOB_IP_DRAW_DRAWING_H */
