/**
 * @date Wed Jun 22 17:50:08 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief This class can be used to load and store arrays from/to .tensor files
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IO_TENSORFILE_H
#define BOB_IO_TENSORFILE_H

#include <boost/format.hpp>
#include <stdexcept>

#include <bob.io.base/blitz_array.h>

#include "TensorFileHeader.h"

namespace bob { namespace io { namespace base {

  /**
   * Defines the flags that might be used when loading/storing a file
   * containing blitz arrays.
   */
  enum _TensorFileFlag {
    _unset   = 0,
    _append  = 1L << 0,
    _in      = 1L << 3,
    _out     = 1L << 4
  };

  /**
   * This class can be used for loading and storing multiarrays from/to
   * tensor files
   */
  class TensorFile
  {
    public:
      /**
       * Defines the bitmask type for providing information about the type of
       * the stream.
       */
      typedef _TensorFileFlag openmode;
      static const openmode append  = _append;
      static const openmode in      = _in;
      static const openmode out     = _out;

      /**
       * Constructor
       */
      TensorFile(const std::string& filename, openmode f);

      /**
       * Destructor
       */
      ~TensorFile();

      /**
       * Tests if next operation will succeed.
       */
      inline bool operator!() const { return !m_stream; }

      /**
       * Closes the TensorFile
       */
      void close();

      /**
       * Puts an Array of a given type into the output stream/file. If the
       * type/shape have not yet been set, it is set according to the type
       * and shape given in the blitz array, otherwise the type/shape should
       * match or an exception is thrown.
       *
       * Please note that blitz::Array<> will be implicitly constructed as
       * required and respecting those norms.
       *
       * @warning: Please convert your files to HDF5, this format is
       * deprecated starting on 16.04.2011 - AA
       */
      void write(const bob::io::base::array::interface& data);

      /**
       * Reads the file data into a bob::io::base::array::interface - this variant reads the next
       * variable. The bob::io::base::array::interface size will be reset if required.
       */
      void read(bob::io::base::array::interface& data);

      /**
       * Reads the file data into a bob::io::base::array::interface - this variant allows the
       * specification of a position to read data from. The bob::io::base::array::interface size will be
       * reset if required.
       */
      void read (size_t index, bob::io::base::array::interface& data);

      /**
       * Peeks the file and returns the currently set typeinfo
       */
      void peek(bob::io::base::array::typeinfo& info) const;

      /**
       * Gets the number of samples/arrays written so far
       *
       * @warning An exception is thrown if nothing was written so far
       */
      inline size_t size() const {
        return (m_header_init)? m_n_arrays_written : 0;
      }

      /**
       * Gets the number of elements per array
       *
       * @warning An exception is thrown if nothing was written so far
       */
      inline size_t getNElements() const {
        headerInitialized();
        return m_header.getNElements();
      }

      /**
       * Gets the size along a particular dimension
       *
       * @warning An exception is thrown if nothing was written so far
       */
      inline size_t getSize(size_t dim_index) const {
        headerInitialized();
        return m_header.m_type.shape[dim_index];
      }

      /**
       * Initializes the tensor file with the given type and shape.
       */
      inline void initTensorFile(const bob::io::base::array::typeinfo& info) {
        initHeader(info);
      }

    private: //Some stuff I need privately

      /**
       * Checks if the end of the tensor file is reached
       */
      inline void endOfFile() {
        if(m_current_array >= m_header.m_n_samples ) {
          boost::format m("TensorFile::endOfFile(): current array index == %d is outside the bounds of declared object with size %d");
          m % m_current_array % m_header.m_n_samples;
          throw std::runtime_error(m.str());
        }
      }

      /**
       * Checks that the header has been initialized, and raise an
       * exception if not
       */
      inline void headerInitialized() const {
        if (!m_header_init) {
          throw std::runtime_error("TensorFile: header is not initialized");
        }
      }

      /**
       * Initializes the header of the (output) stream with the given type
       * and shape
       */
      void initHeader(const bob::io::base::array::typeinfo& info);

    public:

      /********************************************************************
       * Specific blitz::Array<> operations
       ********************************************************************/


      /**
       * A shortcut to write a blitz::Array<T,D>
       *
       * @warning: Please convert your files to HDF5, this format is
       * deprecated starting on 16.04.2011 - AA
       */
      template <typename T, int D>
        inline void write(blitz::Array<T,D>& bz) {
          write(bob::io::base::array::blitz_array(bz));
        }

      /**
       * Load one blitz++ multiarray from the input stream/file All the
       * multiarrays saved have the same dimensions.
       */
      template <typename T, int D> inline blitz::Array<T,D> read() {
        bob::io::base::array::typeinfo info;
        peek(info);
        bob::io::base::array::blitz_array buf(info);
        read(buf);
        return bob::io::base::array::cast<T,D>(buf);
      }

      template <typename T, int D> inline blitz::Array<T,D> read(size_t
          index) {
        bob::io::base::array::typeinfo info;
        peek(info);
        bob::io::base::array::blitz_array buf(info);
        read(index, buf);
        return bob::io::base::array::cast<T,D>(buf);
      }

    private: //representation

      bool m_header_init;
      size_t m_current_array;
      size_t m_n_arrays_written;
      std::fstream m_stream;
      detail::TensorFileHeader m_header;
      openmode m_openmode;
      boost::shared_ptr<void> m_buffer;
  };

  inline _TensorFileFlag operator&(_TensorFileFlag a, _TensorFileFlag b) {
    return _TensorFileFlag(static_cast<int>(a) & static_cast<int>(b));
  }

  inline _TensorFileFlag operator|(_TensorFileFlag a, _TensorFileFlag b) {
    return _TensorFileFlag(static_cast<int>(a) | static_cast<int>(b));
  }

  inline _TensorFileFlag operator^(_TensorFileFlag a, _TensorFileFlag b) {
    return _TensorFileFlag(static_cast<int>(a) ^ static_cast<int>(b));
  }

  inline _TensorFileFlag& operator|=(_TensorFileFlag& a, _TensorFileFlag b) {
    return a = a | b;
  }

  inline _TensorFileFlag& operator&=(_TensorFileFlag& a, _TensorFileFlag b) {
    return a = a & b;
  }

  inline _TensorFileFlag& operator^=(_TensorFileFlag& a, _TensorFileFlag b) {
    return a = a ^ b;
  }

  inline _TensorFileFlag operator~(_TensorFileFlag a) {
    return _TensorFileFlag(~static_cast<int>(a));
  }

}}}

#endif /* BOB_IO_BINFILE_H */
