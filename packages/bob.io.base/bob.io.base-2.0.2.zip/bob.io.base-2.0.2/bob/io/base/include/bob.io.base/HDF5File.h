/**
 * @date Wed Jun 22 17:50:08 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief bob support for HDF5 files. HDF5 is a open standard for
 * self-describing data files. You can get more information in this webpage:
 * http://www.hdfgroup.org/HDF5
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IO_BASE_HDF5FILE_H
#define BOB_IO_BASE_HDF5FILE_H

#include <boost/format.hpp>

#include <bob.io.base/HDF5Utils.h>

namespace bob { namespace io { namespace base {

  /**
   * This is the main type for interfacing bob with HDF5. It allows the user
   * to create, delete and modify data objects using a very-level API. The
   * total functionality provided by this API is, of course, much smaller than
   * what is provided if you use the HDF5 C-APIs directly, but is much simpler
   * as well.
   */
  class HDF5File {

    public:

      /**
       * This enumeration defines the different values with which you can open
       * the files with
       */
      typedef enum mode_t {
        in = 0, //H5F_ACC_RDONLY    < can only read file
        inout = 1, //H5F_ACC_RDWR   < open file for reading and writing
        trunc = 2, //H5F_ACC_TRUNC  < if file exists, truncate it and open
        excl = 4 //H5F_ACC_EXCL    < if file exists, raise, otherwise == inout
      } mode_t;

    public: //api

      /**
       * Constructor, starts a new HDF5File object giving it a file name and an
       * action: excl/trunc/in/inout
       */
      HDF5File (const std::string& filename, mode_t mode);

      /**
       * Constructor, starts a new HDF5File object giving it a file name and an
       * action: 'r' (read-only), 'a' (read/write/append), 'w' (read/write/truncate) or 'x' (read/write/exclusive)
       */
      HDF5File (const std::string& filename, const char mode='r');

      /**
       * Destructor virtualization
       */
      virtual ~HDF5File();

      /**
       * Flushes the current content of the file to disk.
       */
      void flush() {m_file->flush();}

      /**
       * Closes the file after writing its content to disk
       */
      void close();

      /**
       * Changes the current prefix path. When this object is started, it
       * points to the root of the file. If you set this to a different
       * value, it will be used as a prefix to any subsequent operation on
       * relative paths until you reset it.
       *
       * @param path If path starts with '/', it is treated as an absolute
       * path. '..' and '.' are supported. This object should be a std::string.
       * If the value is relative, it is added to the current path.
       *
       * @note All operations taking a relative path, following a cd(), will be
       * considered relative to the value returned by cwd().
       */
      void cd(const std::string& path);

      /**
       * Tells if a certain directory exists in a file.
       */
      bool hasGroup(const std::string& path);

      /**
       * Creates a directory within the file. It is an error to recreate a path
       * that already exists. You can check this with hasGroup()
       */
      void createGroup(const std::string& path);

      /**
       * Returns the name of the file currently opened
       */
      const std::string filename() const {check_open(); return m_file->filename(); }

      /**
       * Checks if the file is open for writing
       */
      bool writable() const {check_open(); return m_file->writable();}

      /**
       * Returns the current working path, fully resolved. This is
       * re-calculated every time you call this method.
       */
      std::string cwd() const;

      /**
       * Tells if we have a variable with the given name inside the HDF5 file.
       * If the file path given is a relative file path, it is taken w.r.t. the
       * current working directory, as returned by cwd().
       */
      bool contains(const std::string& path) const;

      /**
       * Describe a certain dataset path. If the file path is a relative one,
       * it is taken w.r.t. the current working directory, as returned by
       * cwd().
       */
      const std::vector<HDF5Descriptor>& describe (const std::string& path) const;

      /**
       * Unlinks a particular dataset from the file. Note that this will
       * not erase the data on the current file as that functionality is not
       * provided by HDF5. To actually reclaim the space occupied by the
       * unlinked structure, you must re-save this file to another file. The
       * new file will not contain the data of any dangling datasets (datasets
       * w/o names or links). Relative paths are allowed.
       */
      void unlink (const std::string& path);

      /**
       * Renames an existing dataset
       */
      void rename (const std::string& from, const std::string& to);

      /**
       * Accesses all existing paths in one shot. Input has to be a std
       * container with T = std::string and accepting push_back()
       */
      template <typename T> void paths (T& container, const bool relative = false) const {
        m_cwd->dataset_paths(container);
        check_open();
        if (relative){
          const std::string d = cwd();
          const int len = d.length()+1;
          for (typename T::iterator it = container.begin(); it != container.end(); ++it){
            // assert that the string contains the current path
            assert(it->find(d) == 0);
            // subtract current path
            *it = it->substr(len);
          }
        }
      }

      /**
       * Accesses all existing paths in one shot. Input has to be a std
       * container with T = std::string and accepting push_back()
       */
      template <typename T> void sub_groups (T& container, bool relative = false, bool recursive = true) const {
        check_open();
        m_cwd->subgroup_paths(container, recursive);
        if (!relative){
          const std::string d = cwd() + "/";
          for (typename T::iterator it = container.begin(); it != container.end(); ++it){
            // add current path
            *it = d + *it;
          }
        }
      }

      /**
       * Copies the contents of the other file to this file. This is a blind
       * operation, so we try to copy everything from the given file to the
       * current one. It is the user responsibility to make sure the "path"
       * slots in the other file are not already taken. If that is detected, an
       * exception will be raised.
       *
       * This operation will be conducted w.r.t. the currently set prefix path
       * (verifiable using cwd()).
       */
      void copy (HDF5File& other);

      /**
       * Reads data from the file into a scalar. Raises an exception if the
       * type is incompatible. Relative paths are accepted.
       */
      template <typename T>
        void read(const std::string& path, size_t pos, T& value) {
          check_open();
          (*m_cwd)[path]->read(pos, value);
        }

      /**
       * Reads data from the file into a scalar. Returns by copy. Raises if the
       * type T is incompatible. Relative paths are accepted.
       */
      template <typename T> T read(const std::string& path, size_t pos) {
        check_open();
        return (*m_cwd)[path]->read<T>(pos);
      }

      /**
       * Reads data from the file into a scalar. Raises an exception if the
       * type is incompatible. Relative paths are accepted. Calling this method
       * is equivalent to calling read(path, 0). Returns by copy.
       */
      template <typename T> T read(const std::string& path) {
        return read<T>(path, 0);
      }

      /**
       * Reads data from the file into a array. Raises an exception if the type
       * is incompatible. Relative paths are accepted.
       */
      template <typename T, int N> void readArray(const std::string& path,
          size_t pos, blitz::Array<T,N>& value) {
        check_open();
        (*m_cwd)[path]->readArray(pos, value);
      }

      /**
       * Reads data from the file into a array. Raises an exception if the type
       * is incompatible. Relative paths are accepted. Destination array is
       * allocated internally and returned by value.
       */
      template <typename T, int N> blitz::Array<T,N> readArray
        (const std::string& path, size_t pos) {
        check_open();
        return (*m_cwd)[path]->readArray<T,N>(pos);
      }

      /**
       * Reads data from the file into a array. Raises an exception if the type
       * is incompatible. Relative paths are accepted. Calling this method is
       * equivalent to calling readArray(path, 0, value).
       */
      template <typename T, int N> void readArray(const std::string& path,
          blitz::Array<T,N>& value) {
        readArray(path, 0, value);
      }

      /**
       * Reads data from the file into a array. Raises an exception if the type
       * is incompatible. Relative paths are accepted. Calling this method is
       * equivalent to calling readArray(path, 0). Destination array is
       * allocated internally.
       */
      template <typename T, int N> blitz::Array<T,N> readArray
        (const std::string& path) {
          return readArray<T,N>(path, 0);
      }

      /**
       * Modifies the value of a scalar inside the file. Relative paths are
       * accepted.
       */
      template <typename T> void replace(const std::string& path, size_t pos,
          const T& value) {
        check_open();
        if (!m_file->writable()) {
          boost::format m("cannot replace value at dataset '%s' at path '%s' of file '%s' because it is not writeable");
          m % path % m_cwd->path() % m_file->filename();
          throw std::runtime_error(m.str());
        }
        (*m_cwd)[path]->replace(pos, value);
      }

      /**
       * Modifies the value of a scalar inside the file. Relative paths are
       * accepted. Calling this method is equivalent to calling replace(path,
       * 0, value).
       */
      template <typename T> void replace(const std::string& path,
          const T& value) {
        replace(path, 0, value);
      }

      /**
       * Modifies the value of a array inside the file. Relative paths are
       * accepted.
       */
      template <typename T> void replaceArray(const std::string& path,
          size_t pos, const T& value) {
        check_open();
        if (!m_file->writable()) {
          boost::format m("cannot replace array at dataset '%s' at path '%s' of file '%s' because it is not writeable");
          m % path % m_cwd->path() % m_file->filename();
          throw std::runtime_error(m.str());
        }
        (*m_cwd)[path]->replaceArray(pos, value);
      }

      /**
       * Modifies the value of a array inside the file. Relative paths are
       * accepted. Calling this method is equivalent to calling
       * replaceArray(path, 0, value).
       */
      template <typename T> void replaceArray(const std::string& path,
          const T& value) {
        replaceArray(path, 0, value);
      }

      /**
       * Appends a scalar in a dataset. If the dataset does not yet exist, one
       * is created with the type characteristics. Relative paths are accepted.
       */
      template <typename T> void append(const std::string& path,
          const T& value) {
        check_open();
        if (!m_file->writable()) {
          boost::format m("cannot append value to dataset '%s' at path '%s' of file '%s' because it is not writeable");
          m % path % m_cwd->path() % m_file->filename();
          throw std::runtime_error(m.str());
        }
        if (!contains(path)) m_cwd->create_dataset(path, bob::io::base::HDF5Type(value), true, 0);
        (*m_cwd)[path]->add(value);
      }

      /**
       * Appends a array in a dataset. If the dataset does not yet exist, one
       * is created with the type characteristics. Relative paths are accepted.
       *
       * If a new Dataset is to be created, you can also set the compression
       * level. Note this setting has no effect if the Dataset already exists
       * on file, in which case the current setting for that dataset is
       * respected. The maximum value for the gzip compression is 9. The value
       * of zero turns compression off (the default).
       */
      template <typename T> void appendArray(const std::string& path,
          const T& value, size_t compression=0) {
        check_open();
        if (!m_file->writable()) {
          boost::format m("cannot append array to dataset '%s' at path '%s' of file '%s' because it is not writeable");
          m % path % m_cwd->path() % m_file->filename();
          throw std::runtime_error(m.str());
        }
        if (!contains(path)) m_cwd->create_dataset(path, bob::io::base::HDF5Type(value), true, compression);
        (*m_cwd)[path]->addArray(value);
      }

      /**
       * Sets the scalar at position 0 to the given value. This method is
       * equivalent to checking if the scalar at position 0 exists and then
       * replacing it. If the path does not exist, we append the new scalar.
       */
      template <typename T> void set(const std::string& path, const T& value) {
        check_open();
        if (!m_file->writable()) {
          boost::format m("cannot set value at dataset '%s' at path '%s' of file '%s' because it is not writeable");
          m % path % m_cwd->path() % m_file->filename();
          throw std::runtime_error(m.str());
        }
        if (!contains(path)) m_cwd->create_dataset(path, bob::io::base::HDF5Type(value), false, 0);
        (*m_cwd)[path]->replace(0, value);
      }

      /**
       * Sets the array at position 0 to the given value. This method is
       * equivalent to checking if the array at position 0 exists and then
       * replacing it. If the path does not exist, we append the new array.
       *
       * If a new Dataset is to be created, you can also set the compression
       * level. Note this setting has no effect if the Dataset already exists
       * on file, in which case the current setting for that dataset is
       * respected. The maximum value for the gzip compression is 9. The value
       * of zero turns compression off (the default).
       */
      template <typename T> void setArray(const std::string& path,
          const T& value, size_t compression=0) {
        check_open();
        if (!m_file->writable()) {
          boost::format m("cannot set array at dataset '%s' at path '%s' of file '%s' because it is not writeable");
          m % path % m_cwd->path() % m_file->filename();
          throw std::runtime_error(m.str());
        }
        if (!contains(path)) m_cwd->create_dataset(path, bob::io::base::HDF5Type(value), false, compression);
        (*m_cwd)[path]->replaceArray(0, value);
      }

    public: //api shortcuts to deal with buffers -- avoid these at all costs!

      /**
       * creates a new dataset. If the dataset already exists, checks if the
       * existing data is compatible with the required type.
       */
      void create (const std::string& path, const HDF5Type& dest, bool list,
          size_t compression);

      /**
       * Reads data from the file into a buffer. The given buffer contains
       * sufficient space to hold the type described in "dest". Raises an
       * exception if the type is incompatible with the expected data in the
       * file. Relative paths are accepted.
       */
      void read_buffer (const std::string& path, size_t pos,
          const HDF5Type& type, void* buffer) const;

      /**
       * writes the contents of a given buffer into the file. the area that the
       * data will occupy should have been selected beforehand.
       */
      void write_buffer (const std::string& path, size_t pos,
          const HDF5Type& type, const void* buffer);

      /**
       * extend the dataset with one extra variable.
       */
      void extend_buffer (const std::string& path,
          const HDF5Type& type, const void* buffer);

      /**
       * Copy construct an already opened HDF5File; just creates a shallow copy
       * of the file
       */
      HDF5File (const HDF5File& other);

      /**
       * Drop the current settings and load new ones from the other file.
       */
      HDF5File& operator= (const HDF5File& other);

    public: // attribute handling

      /**
       * Tells if there is an attribute with a given name on the given path,
       * relative to the current location, possibly.
       */
      bool hasAttribute(const std::string& path, const std::string& name) const;

      /**
       * Reads data from an attribute into a scalar. If the attribute does not
       * exist, raise an exception. Raises a TypeError if the types are not
       * compatible.
       */
      template <typename T>
        void getAttribute(const std::string& path, const std::string& name,
            T& value) const {
          check_open();
          if (m_cwd->has_dataset(path)) {
            value = (*m_cwd)[path]->get_attribute<T>(name);
          }
          else if (m_cwd->has_group(path)) {
            value = m_cwd->cd(path)->get_attribute<T>(name);
          }
          else {
            boost::format m("cannot read attribute '%s' at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
            m % name % path % m_file->filename() % m_cwd->path();
            throw std::runtime_error(m.str());
          }
        }

      /**
       * Reads data from an attribute into an array. If the attribute does not
       * exist, raise an exception. Raises a type error if the types are not
       * compatible.
       */
      template <typename T, int N>
        void getArrayAttribute(const std::string& path,
            const std::string& name, blitz::Array<T,N>& value) const {
          check_open();
          if (m_cwd->has_dataset(path)) {
            value = (*m_cwd)[path]->get_array_attribute<T,N>(name);
          }
          else if (m_cwd->has_group(path)) {
            value = m_cwd->cd(path)->get_array_attribute<T,N>(name);
          }
          else {
            boost::format m("cannot read (array) attribute '%s' at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
            m % name % path % m_file->filename() % m_cwd->path();
            throw std::runtime_error(m.str());
          }
        }

      /**
       * Writes a scalar as an attribute to a path in this file.
       */
      template <typename T>
        void setAttribute(const std::string& path, const std::string& name,
            const T value) {
          check_open();
          if (m_cwd->has_dataset(path)) {
            (*m_cwd)[path]->set_attribute(name, value);
          }
          else if (m_cwd->has_group(path)) {
            m_cwd->cd(path)->set_attribute(name, value);
          }
          else {
            boost::format m("cannot write attribute '%s' at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
            m % name % path % m_file->filename() % m_cwd->path();
            throw std::runtime_error(m.str());
          }
        }

      /**
       * Writes an array as an attribute to a path in this file.
       */
      template <typename T, int N>
        void setArrayAttribute(const std::string& path,
            const std::string& name, const blitz::Array<T,N>& value) {
          check_open();
          if (m_cwd->has_dataset(path)) {
            (*m_cwd)[path]->set_array_attribute(name, value);
          }
          else if (m_cwd->has_group(path)) {
            m_cwd->cd(path)->set_array_attribute(name, value);
          }
          else {
            boost::format m("cannot write (array) attribute '%s' at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
            m % name % path % m_file->filename() % m_cwd->path();
            throw std::runtime_error(m.str());
          }
        }

      /**
       * Gets the type information of an attribute
       */
      void getAttributeType(const std::string& path,
          const std::string& name, bob::io::base::HDF5Type& type) const;

      /**
       * Deletes a given attribute
       */
      void deleteAttribute(const std::string& path,
          const std::string& name);

      /**
       * List attributes available on a certain object.
       */
      void listAttributes(const std::string& path,
          std::map<std::string, bob::io::base::HDF5Type>& attributes) const;

    public: //raw accessors to attributes

      void read_attribute(const std::string& path, const std::string& name,
          const bob::io::base::HDF5Type& type, void* buffer) const;

      void write_attribute(const std::string& path, const std::string& name,
          const bob::io::base::HDF5Type& type, const void* buffer);

    private: //representation

      void check_open() const;

      boost::shared_ptr<detail::hdf5::File> m_file; ///< the file itself
      boost::shared_ptr<detail::hdf5::Group> m_cwd; ///< current working dir

  };

}}}

#endif /* BOB_IO_BASE_HDF5FILE_H */
