/**
 * @date Wed Oct 26 17:11:16 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implements the TensorArrayCodec type
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include "TensorFile.h"
#include <bob.io.base/CodecRegistry.h>

class TensorArrayFile: public bob::io::base::File {

  public: //api

    TensorArrayFile(const char* path, bob::io::base::TensorFile::openmode mode):
      m_file(path, mode),
      m_filename(path) {
        if (m_file.size()) m_file.peek(m_type);
      }

    virtual ~TensorArrayFile() { }

    virtual const char* filename() const {
      return m_filename.c_str();
    }

    virtual const bob::io::base::array::typeinfo& type_all () const {
      return m_type;
    }

    virtual const bob::io::base::array::typeinfo& type () const {
      return m_type;
    }

    virtual size_t size() const {
      return m_file.size();
    }

    virtual const char* name() const {
      return s_codecname.c_str();
    }

    virtual void read_all(bob::io::base::array::interface& buffer) {

      if(!m_file)
        throw std::runtime_error("uninitialized binary file cannot be read");

      m_file.read(0, buffer);

    }

    virtual void read(bob::io::base::array::interface& buffer, size_t index) {

      if(!m_file)
        throw std::runtime_error("uninitialized binary file cannot be read");

      m_file.read(index, buffer);

    }

    virtual size_t append (const bob::io::base::array::interface& buffer) {

      m_file.write(buffer);

      if (size() == 1) m_file.peek(m_type);

      return size() - 1;

    }

    virtual void write (const bob::io::base::array::interface& buffer) {

      //we don't have a special way to treat write()'s like in HDF5.
      append(buffer);

    }

  private: //representation

    bob::io::base::TensorFile m_file;
    bob::io::base::array::typeinfo m_type;
    std::string m_filename;

    static std::string s_codecname;

};

std::string TensorArrayFile::s_codecname = "bob.tensor";

/**
 * From this point onwards we have the registration procedure. If you are
 * looking at this file for a coding example, just follow the procedure bellow,
 * minus local modifications you may need to apply.
 */

/**
 * This defines the factory method F that can create codecs of this type.
 *
 * Here are the meanings of the mode flag that should be respected by your
 * factory implementation:
 *
 * 'r': opens for reading only - no modifications can occur; it is an
 *      error to open a file that does not exist for read-only operations.
 * 'w': opens for reading and writing, but truncates the file if it
 *      exists; it is not an error to open files that do not exist with
 *      this flag.
 * 'a': opens for reading and writing - any type of modification can
 *      occur. If the file does not exist, this flag is effectively like
 *      'w'.
 *
 * Returns a newly allocated File object that can read and write data to the
 * file using a specific backend.
 *
 * @note: This method can be static.
 */
static boost::shared_ptr<bob::io::base::File> make_file (const char* path, char mode) {

  bob::io::base::TensorFile::openmode _mode;
  if (mode == 'r') _mode = bob::io::base::TensorFile::in;
  else if (mode == 'w') _mode = bob::io::base::TensorFile::out;
  else if (mode == 'a') _mode = bob::io::base::TensorFile::append;
  else throw std::runtime_error("unsupported tensor file opening mode");

  return boost::make_shared<TensorArrayFile>(path, _mode);

}

/**
 * Takes care of codec registration per se.
 */
static bool register_codec() {

  boost::shared_ptr<bob::io::base::CodecRegistry> instance =
    bob::io::base::CodecRegistry::instance();

  instance->registerExtension(".tensor", "torch3vision v2.1 tensor files", &make_file);

  return true;

}

static bool codec_registered = register_codec();
