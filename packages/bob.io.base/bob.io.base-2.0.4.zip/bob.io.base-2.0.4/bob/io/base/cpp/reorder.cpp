/**
 * @date Tue Nov 22 11:24:44 2011 +0100
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implementation of row-major/column-major reordering
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/format.hpp>
#include <cstring> //for memcpy

#include <bob.io.base/reorder.h>

void bob::io::base::rc2d(size_t& row, size_t& col, const size_t i, const size_t j,
    const size_t* shape) {
  row = (i * shape[1]) + j;
  col = (j * shape[0]) + i;
}

void bob::io::base::rc3d(size_t& row, size_t& col, const size_t i, const size_t j,
    const size_t k, const size_t* shape) {
  row = ( (i * shape[1]) + j ) * shape[2] + k;
  col = ( (k * shape[1]) + j ) * shape[0] + i;
}

void bob::io::base::rc4d(size_t& row, size_t& col, const size_t i, const size_t j,
    const size_t k, const size_t l, const size_t* shape) {
  row = ( ( i * shape[1] + j ) * shape[2] + k ) * shape[3] + l;
  col = ( ( l * shape[2] + k ) * shape[1] + j ) * shape[0] + i;
}

void bob::io::base::row_to_col_order(const void* src_, void* dst_,
    const bob::io::base::array::typeinfo& info) {

  size_t dsize = info.item_size();

  //cast to byte type so we can manipulate the pointers...
  const uint8_t* src = static_cast<const uint8_t*>(src_);
  uint8_t* dst = static_cast<uint8_t*>(dst_);

  switch(info.nd) {

    case 1:
      std::memcpy(dst, src, info.buffer_size());
      break;

    case 2:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j) {
          size_t row_major, col_major;
          bob::io::base::rc2d(row_major, col_major, i, j, info.shape);
          row_major *= dsize;
          col_major *= dsize;
          std::memcpy(&dst[col_major], &src[row_major], dsize);
        }
      break;

    case 3:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k) {
            size_t row_major, col_major;
            bob::io::base::rc3d(row_major, col_major, i, j, k, info.shape);
            row_major *= dsize;
            col_major *= dsize;
            std::memcpy(&dst[col_major], &src[row_major], dsize);
          }
      break;

    case 4:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k)
            for (size_t l=0; l<info.shape[3]; ++l) {
              size_t row_major, col_major;
              bob::io::base::rc4d(row_major, col_major, i, j, k, l, info.shape);
              row_major *= dsize;
              col_major *= dsize;
              std::memcpy(&dst[col_major], &src[row_major], dsize);
            }
      break;

    default:
      {
        boost::format m("row_to_col_order() can only flip arrays with up to %u dimensions - you passed one with %u dimensions");
        m % BOB_MAX_DIM % info.nd;
        throw std::runtime_error(m.str());
      }
  }
}

void bob::io::base::col_to_row_order(const void* src_, void* dst_,
    const bob::io::base::array::typeinfo& info) {

  size_t dsize = info.item_size();

  //cast to byte type so we can manipulate the pointers...
  const uint8_t* src = static_cast<const uint8_t*>(src_);
  uint8_t* dst = static_cast<uint8_t*>(dst_);

  switch(info.nd) {

    case 1:
      std::memcpy(dst, src, info.buffer_size());
      break;

    case 2:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j) {
          size_t row_major, col_major;
          bob::io::base::rc2d(row_major, col_major, i, j, info.shape);
          row_major *= dsize;
          col_major *= dsize;
          std::memcpy(&dst[row_major], &src[col_major], dsize);
        }
      break;

    case 3:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k) {
            size_t row_major, col_major;
            bob::io::base::rc3d(row_major, col_major, i, j, k, info.shape);
            row_major *= dsize;
            col_major *= dsize;
            std::memcpy(&dst[row_major], &src[col_major], dsize);
          }
      break;

    case 4:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k)
            for (size_t l=0; l<info.shape[3]; ++l) {
              size_t row_major, col_major;
              bob::io::base::rc4d(row_major, col_major, i, j, k, l, info.shape);
              row_major *= dsize;
              col_major *= dsize;
              std::memcpy(&dst[row_major], &src[col_major], dsize);
            }
      break;

    default:
      {
        boost::format m("col_to_row_order() can only flip arrays with up to %u dimensions - you passed one with %u dimensions");
        m % BOB_MAX_DIM % info.nd;
        throw std::runtime_error(m.str());
      }
  }
}

void bob::io::base::row_to_col_order_complex(const void* src_, void* dst_re_,
    void* dst_im_, const bob::io::base::array::typeinfo& info) {

  size_t dsize = info.item_size();
  size_t dsize2 = dsize/2; ///< size of each complex component (real, imaginary)

  //cast to byte type so we can manipulate the pointers...
  const uint8_t* src = static_cast<const uint8_t*>(src_);
  uint8_t* dst_re = static_cast<uint8_t*>(dst_re_);
  uint8_t* dst_im = static_cast<uint8_t*>(dst_im_);

  switch(info.nd) {

    case 1:
      for (size_t i=0; i<info.shape[0]; ++i) {
        std::memcpy(&dst_re[dsize2*i], &src[dsize*i]       , dsize2);
        std::memcpy(&dst_im[dsize2*i], &src[dsize*i]+dsize2, dsize2);
      }
      break;

    case 2:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j) {
          size_t row_major, col_major;
          bob::io::base::rc2d(row_major, col_major, i, j, info.shape);
          row_major *= dsize;
          col_major *= dsize2;
          std::memcpy(&dst_re[col_major], &src[row_major]       , dsize2);
          std::memcpy(&dst_im[col_major], &src[row_major]+dsize2, dsize2);
        }
      break;

    case 3:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k) {
            size_t row_major, col_major;
            bob::io::base::rc3d(row_major, col_major, i, j, k, info.shape);
            row_major *= dsize;
            col_major *= dsize2;
            std::memcpy(&dst_re[col_major], &src[row_major]       , dsize2);
            std::memcpy(&dst_im[col_major], &src[row_major]+dsize2, dsize2);
          }
      break;

    case 4:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k)
            for (size_t l=0; l<info.shape[3]; ++l) {
              size_t row_major, col_major;
              bob::io::base::rc4d(row_major, col_major, i, j, k, l, info.shape);
              row_major *= dsize;
              col_major *= dsize2;
              std::memcpy(&dst_re[col_major], &src[row_major]       , dsize2);
              std::memcpy(&dst_im[col_major], &src[row_major]+dsize2, dsize2);
            }
      break;

    default:
      {
        boost::format m("row_to_col_order_complex() can only flip arrays with up to %u dimensions - you passed one with %u dimensions");
        m % BOB_MAX_DIM % info.nd;
        throw std::runtime_error(m.str());
      }
  }
}

void bob::io::base::col_to_row_order_complex(const void* src_re_, const void* src_im_,
    void* dst_, const bob::io::base::array::typeinfo& info) {

  size_t dsize = info.item_size();
  size_t dsize2 = dsize/2; ///< size of each complex component (real, imaginary)

  //cast to byte type so we can manipulate the pointers...
  const uint8_t* src_re = static_cast<const uint8_t*>(src_re_);
  const uint8_t* src_im = static_cast<const uint8_t*>(src_im_);
  uint8_t* dst = static_cast<uint8_t*>(dst_);

  switch(info.nd) {

    case 1:
      for (size_t i=0; i<info.shape[0]; ++i) {
        std::memcpy(&dst[dsize*i]       , &src_re[dsize2*i], dsize2);
        std::memcpy(&dst[dsize*i]+dsize2, &src_im[dsize2*i], dsize2);
      }
      break;

    case 2:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j) {
          size_t row_major, col_major;
          bob::io::base::rc2d(row_major, col_major, i, j, info.shape);
          row_major *= dsize;
          col_major *= dsize2;
          std::memcpy(&dst[row_major],        &src_re[col_major], dsize2);
          std::memcpy(&dst[row_major]+dsize2, &src_im[col_major], dsize2);
        }
      break;

    case 3:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k) {
            size_t row_major, col_major;
            bob::io::base::rc3d(row_major, col_major, i, j, k, info.shape);
            row_major *= dsize;
            col_major *= dsize2;
            std::memcpy(&dst[row_major]       , &src_re[col_major], dsize2);
            std::memcpy(&dst[row_major]+dsize2, &src_im[col_major], dsize2);
          }
      break;

    case 4:
      for (size_t i=0; i<info.shape[0]; ++i)
        for (size_t j=0; j<info.shape[1]; ++j)
          for (size_t k=0; k<info.shape[2]; ++k)
            for (size_t l=0; l<info.shape[3]; ++l) {
              size_t row_major, col_major;
              bob::io::base::rc4d(row_major, col_major, i, j, k, l, info.shape);
              row_major *= dsize;
              col_major *= dsize2;
              std::memcpy(&dst[row_major]       , &src_re[col_major], dsize2);
              std::memcpy(&dst[row_major]+dsize2, &src_im[col_major], dsize2);
            }
      break;

    default:
      {
        boost::format m("col_to_row_order_complex() can only flip arrays with up to %u dimensions - you passed one with %u dimensions");
        m % BOB_MAX_DIM % info.nd;
        throw std::runtime_error(m.str());
      }
  }
}

