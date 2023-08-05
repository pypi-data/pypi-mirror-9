/**
 * @date Tue Nov 8 15:34:31 2011 +0100
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief A class that implements the polimorphic behaviour required when
 * reading and writing blitz arrays to disk or memory.
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IO_BASE_BLITZ_ARRAY_H
#define BOB_IO_BASE_BLITZ_ARRAY_H

#include <stdexcept>
#include <boost/make_shared.hpp>
#include <boost/format.hpp>
#include <blitz/array.h>

#include <bob.core/check.h>
#include <bob.core/cast.h>
#include <bob.core/array_copy.h>

#include <bob.io.base/array.h>
#include <bob.io.base/array_utils.h>
#include <bob.io.base/array_type.h>

namespace bob { namespace io { namespace base { namespace array {

  /**
   * @brief A blitz::Array representation of an array.
   */
  class blitz_array: public interface {

    public:

      /**
       * @brief Starts by refering to the data from another blitz array.
       */
      blitz_array(boost::shared_ptr<blitz_array> other);

      /**
       * @brief Starts by copying the data from another blitz array.
       */
      blitz_array(const blitz_array& other);

      /**
       * @brief Starts by refering to the data from another buffer.
       */
      blitz_array(boost::shared_ptr<interface> other);

      /**
       * @brief Starts by copying the data from another buffer.
       */
      blitz_array(const interface& other);

      /**
       * @brief Starts with an uninitialized, pre-allocated array.
       */
      blitz_array(const typeinfo& info);

      /**
       * @brief Borrows the given pointer - if you use this constructor, you
       * must make sure the pointed data outlives this object.
       */
      blitz_array(void* data, const typeinfo& info);

      /**
       * @brief Destroyes me
       */
      virtual ~blitz_array();

      /**
       * @brief Copies the data from another buffer.
       */
      virtual void set(const interface& other);

      /**
       * @brief Refers to the data of another buffer.
       */
      virtual void set(boost::shared_ptr<interface> other);

      /**
       * @brief Re-allocates this buffer taking into consideration new
       * requirements. The internal memory should be considered uninitialized.
       */
      virtual void set (const typeinfo& req);

      /**
       * @brief Refers to the data of another blitz array.
       */
      void set(boost::shared_ptr<blitz_array> other);

      /**
       * @brief Element type
       */
      virtual const typeinfo& type() const { return m_type; }

      /**
       * @brief Borrows a reference from the underlying memory. This means
       * this object continues to be responsible for deleting the memory and
       * you should make sure that it outlives the usage of the returned
       * pointer.
       */
      virtual void* ptr() { return m_ptr; }
      virtual const void* ptr() const { return m_ptr; }

      virtual boost::shared_ptr<void> owner() { return m_data; }
      virtual boost::shared_ptr<const void> owner() const { return m_data; }


      /******************************************************************
       * Blitz Array specific manipulations
       ******************************************************************/


      /**
       * @brief Starts me with new arbitrary data. Please note we refer to the
       * given array. External modifications to the array memory will affect
       * me. If you don't want that to be the case, use the const variant.
       */
      template <typename T, int N>
        blitz_array(boost::shared_ptr<blitz::Array<T,N> > data) {
          set(data);
        }

      /**
       * @brief Starts me with new arbitrary data. Please note we copy the
       * given array. External modifications to the array memory will not
       * affect me. If you don't want that to be the case, start with a
       * non-const reference.
       */
      template <typename T, int N>
        blitz_array(const blitz::Array<T,N>& data) {
          set(data);
        }

      /**
       * @brief Starts me with new arbitrary data. Please note we don't copy
       * the given array.
       * @warning Any resize of the given blitz::Array after this call leads to
       * unexpected results
       */
      template <typename T, int N>
        blitz_array(blitz::Array<T,N>& data) {
          set(data);
        }

      /**
       * @brief This method will set my internal data to the value you
       * specify. We will do this by referring to the data you gave.
       */
      template <typename T, int N>
        void set(boost::shared_ptr<blitz::Array<T,N> > data) {

          if (getElementType<T>() == t_unknown)
            throw std::runtime_error("unsupported element type on blitz::Array<>");
          if (N > BOB_MAX_DIM)
            throw std::runtime_error("unsupported number of dimensions on blitz::Array<>");

          if (!bob::core::array::isCContiguous(*data.get()))
            throw std::runtime_error("cannot buffer'ize non-c contiguous array");

          m_type.set(data);

          m_data = data;
          m_ptr = reinterpret_cast<void*>(data->data());
          m_is_blitz = true;
        }

      /**
       * @brief This method will set my internal data to the value you
       * specify. We will do this by copying the data you gave.
       */
      template <typename T, int N> void set(const blitz::Array<T,N>& data) {
        set(boost::make_shared<blitz::Array<T,N> >(ccopy(data)));
      }

      /**
       * @brief This method will set my internal data to the value you specify.
       * We will do this by referencing the data you gave.
       * @warning Any resize of the given blitz::Array after this call leads to
       * unexpected results
       */
      template <typename T, int N> void set(blitz::Array<T,N>& data) {
        set(boost::make_shared<blitz::Array<T,N> >(data));
      }

      /**
       * @brief This method returns a reference to my internal data. It is the
       * fastest way to get access to my data because it involves no data
       * copying. This method has two limitations:
       *
       * 1) You need to know the correct type and number of dimensions or I'll
       * throw an exception.
       *
       * 2) If this buffer was started by refering to another buffer's data
       * which is not a blitz array, an exception will be raised.
       * Unfortunately, blitz::Array<>'s do not offer a management mechanism
       * for tracking external data allocation. The exception can be avoided
       * and the referencing mechanism forced if you set the flag "temporary"
       * to "true". In this mode, this method will always suceed, but the
       * object returned will have its lifetime associated to this buffer. In
       * other words, you should make sure this buffer outlives the returned
       * blitz::Array<T,N>.
       */
      template <typename T, int N> blitz::Array<T,N> get(bool temporary=false) {

        if (m_is_blitz) {

          if (!m_data) throw std::runtime_error("empty blitz array");

          if (m_type.dtype != getElementType<T>()) {
            boost::format m("cannot efficiently retrieve blitz::Array<%s,%d> from buffer of type '%s'");
            m % stringize<T>() % N % m_type.str();
            throw std::runtime_error(m.str());
          }

          if (m_type.nd != N) {
            boost::format m("cannot retrieve blitz::Array<%s,%d> from buffer of type '%s'");
            m % stringize<T>() % N % m_type.str();
            throw std::runtime_error(m.str());
          }

          return *boost::static_pointer_cast<blitz::Array<T,N> >(m_data).get();
        }

        else {

          if (temporary) { //returns a temporary reference
            return bob::io::base::array::wrap<T,N>(*this);
          }

          else {
            throw std::runtime_error("cannot get() external non-temporary non-blitz array buffer -- for a temporary object, set temporary=true; if you need the returned object to outlive this buffer; use copy() or cast()");
          }
        }

      }

      /**
       * @brief This method returns a copy to my internal data (not a
       * reference) in the type you wish. It is the easiest method to use
       * because I'll never throw, no matter which type you want to receive
       * data at. Only get the number of dimensions right!
       */
      template <typename T, int N> blitz::Array<T,N> cast() const {
        return bob::core::array::cast<T,N>(*this);
      }

    private: //representation

      typeinfo m_type; ///< type information
      void* m_ptr; ///< pointer to the data
      bool m_is_blitz; ///< true if initiated with a blitz::Array<>
      boost::shared_ptr<void> m_data; ///< Pointer to the data owner

  };

}}}}

#endif /* BOB_IO_BASE_BLITZ_ARRAY_H */
