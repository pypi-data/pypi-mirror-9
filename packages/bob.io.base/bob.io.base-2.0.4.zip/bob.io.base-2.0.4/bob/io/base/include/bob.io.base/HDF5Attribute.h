/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri  2 Mar 08:19:03 2012
 *
 * @brief Simple attribute support for HDF5 files
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IO_BASE_HDF5ATTRIBUTE_H
#define BOB_IO_BASE_HDF5ATTRIBUTE_H

#include <string>
#include <map>
#include <boost/shared_ptr.hpp>
#include <hdf5.h>

#include <bob.io.base/HDF5Types.h>

namespace bob { namespace io { namespace base { namespace detail { namespace hdf5 {

  /**
   * Finds out the type of the attribute, if it exists, raises otherwise.
   */
  void gettype_attribute (const boost::shared_ptr<hid_t> location,
      const std::string& name, HDF5Type& type);

  /**
   * Reads the attribute value, place it in "buffer"
   */
  void read_attribute (const boost::shared_ptr<hid_t> location,
      const std::string& name, const bob::io::base::HDF5Type& dest, void* buffer);

  /**
   * Writes an attribute value from "buffer"
   */
  void write_attribute (boost::shared_ptr<hid_t> location,
      const std::string& name, const bob::io::base::HDF5Type& dest,
      const void* buffer);

  /**
   * Sets a scalar attribute on the given location. Setting an existing
   * attribute overwrites its value.
   *
   * @note Only simple scalars are supported for the time being
   */
  template <typename T> void set_attribute(boost::shared_ptr<hid_t> location,
      const std::string& name, const T& v) {
    bob::io::base::HDF5Type dest_type(v);
    write_attribute(location, name, dest_type,
        reinterpret_cast<const void*>(&v));
  }

  /**
   * Reads an attribute from the current group. Raises an error if such
   * attribute does not exist on the group. To check for existence, use
   * has_attribute().
   */
  template <typename T> T get_attribute(const boost::shared_ptr<hid_t> location,
      const std::string& name) {
    T v;
    bob::io::base::HDF5Type dest_type(v);
    read_attribute(location, name, dest_type, reinterpret_cast<void*>(&v));
    return v;
  }

  /**
   * Checks if a certain attribute exists in this location.
   */
  bool has_attribute(const boost::shared_ptr<hid_t> location,
      const std::string& name);

  /**
   * Deletes an attribute from a location.
   */
  void delete_attribute(boost::shared_ptr<hid_t> location,
      const std::string& name);

  /**
   * Lists all attributes and associated types currently available somewhere
   */
  void list_attributes(boost::shared_ptr<hid_t> location,
    std::map<std::string, bob::io::base::HDF5Type>& attributes);

}}}}}

#endif /* BOB_IO_BASE_HDF5ATTRIBUTE_H */
