/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed  3 Oct 07:46:49 2012
 *
 * @brief Utilities for easy manipulation of filed data.
 */

#ifndef BOB_IO_BASE_BASE_UTILS_H
#define BOB_IO_BASE_BASE_UTILS_H

#include <boost/shared_ptr.hpp>

#include <bob.io.base/File.h>

namespace bob { namespace io { namespace base {

  /**
   * Creates a new array codec using the filename extension to determine which
   * codec to use. The opening mode is passed to the underlying registered File
   * implementation.
   *
   * Here are the meanings of the mode flag:
   *
   * 'r': opens for reading only - no modifications can occur; it is an
   *      error to open a file that does not exist for read-only operations.
   * 'w': opens for reading and writing, but truncates the file if it
   *      exists; it is not an error to open files that do not exist with
   *      this flag.
   * 'a': opens for reading and writing - any type of modification can
   *      occur. If the file does not exist, this flag is effectively like
   *      'w'.
   */
  boost::shared_ptr<File> open (const char* filename, char mode);

  /**
   * Opens the file pretending it has a different extension (that is, using a
   * different codec) then the one expected (if any). This allows you to write
   * a file with the extension you want, but still using one of the available
   * codecs.
   */
  boost::shared_ptr<File> open (const char* filename, char mode,
      const char* pretend_extension);

  /**
   * Peeks the file and returns the typeinfo for reading individual frames (or
   * samples) from the file.
   *
   * This method is equivalent to calling open() with 'r' as mode flag and then
   * calling type() on the returned bob::io::base::File object.
   */
  bob::io::base::array::typeinfo peek (const char* filename);

  /**
   * Peeks the file and returns the typeinfo for reading the whole contents in
   * a single shot.
   *
   * This method is equivalent to calling open() with 'r' as mode flag and then
   * calling type_all() on the returned bob::io::base::File object.
   */
  bob::io::base::array::typeinfo peek_all (const char* filename);

  /**
   * Opens for reading and load all contents
   *
   * This method is equivalent to calling open() with 'r' as mode flag and then
   * calling read_all() on the returned bob::io::base::File object.
   */
  template <typename T, int N> blitz::Array<T,N> load (const char* filename) {
    return open(filename, 'r')->read_all<T,N>();
  }

  /**
   * Opens for reading and load a particular frame (or sample)
   *
   * This method is equivalent to calling open() with 'r' as mode flag and then
   * calling read(index) on the returned bob::io::base::File object.
   */
  template <typename T, int N> blitz::Array<T,N> load (const char* filename, size_t index) {
    return open(filename, 'r')->read<T,N>(index);
  }

  /**
   * Opens for appending and add an array to it
   *
   * This method is equivalent to calling open() with 'a' as mode flag and then
   * calling append(data) on the returned bob::io::base::File object.
   */
  template <typename T, int N> void append (const char* filename, const blitz::Array<T,N>& data) {
    open(filename, 'a')->append(data);
  }

  /**
   * Opens for writing and write an array to it. If the file exists before the
   * call to this method, it is truncated.
   *
   * This method is equivalent to calling open() with 'w' as mode flag and then
   * calling write(data) on the returned bob::io::base::File object.
   */
  template <typename T, int N> void save (const char* filename, const blitz::Array<T,N>& data) {
    open(filename, 'w')->write(data);
  }

}}}

#endif /* BOB_IO_BASE_BASE_UTILS_H */
