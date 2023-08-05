/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri  2 Mar 08:23:47 2012
 *
 * @brief Implements attribute read/write for HDF5 files
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/format.hpp>

#include <bob.core/logging.h>

#include <bob.io.base/HDF5Attribute.h>

static std::runtime_error status_error(const char* f, herr_t s) {
  boost::format m("call to HDF5 C-function %s() returned error %d. HDF5 error statck follows:\n%s");
  m % f % s % bob::io::base::format_hdf5_error();
  return std::runtime_error(m.str());
}

bool bob::io::base::detail::hdf5::has_attribute(const boost::shared_ptr<hid_t> location,
    const std::string& name) {
  return H5Aexists(*location, name.c_str());
}

/**
 * Opens an "auto-destructible" HDF5 dataspace
 */
static void delete_h5dataspace (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Sclose(*p);
    if (err < 0) {
      bob::core::error << "H5Sclose() exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
    }
  }
  delete p;
}

static boost::shared_ptr<hid_t> open_memspace(const bob::io::base::HDF5Shape& s) {
  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5dataspace));
  *retval = H5Screate_simple(s.n(), s.get(), 0);
  if (*retval < 0) throw status_error("H5Screate_simple", *retval);
  return retval;
}

/**
 * Opens the memory space of attribute
 */
static boost::shared_ptr<hid_t> get_memspace(hid_t attr) {
  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5dataspace));
  *retval = H5Aget_space(attr);
  if (*retval < 0) throw status_error("H5Aget_space", *retval);
  return retval;
}

/**
 * Auto-destructing HDF5 type
 */
static void delete_h5type (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Tclose(*p);
    if (err < 0) {
      bob::core::error << "H5Tclose() exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
    }
  }
  delete p;
}

/**
 * Gets datatype of attribute
 */
static boost::shared_ptr<hid_t> get_type(hid_t attr) {
  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5type));
  *retval = H5Aget_type(attr);
  if (*retval < 0) throw status_error("H5Aget_type", *retval);
  return retval;
}

/**
 * Figures out the extents of an attribute
 */
static bob::io::base::HDF5Shape get_extents(hid_t space) {
  int rank = H5Sget_simple_extent_ndims(space);
  if (rank < 0) throw status_error("H5Sget_simple_extent_ndims", rank);
  //is at least a list of scalars, but could be a list of arrays
  bob::io::base::HDF5Shape shape(rank);
  herr_t status = H5Sget_simple_extent_dims(space, shape.get(), 0);
  if (status < 0) throw status_error("H5Sget_simple_extent_dims",status);
  return shape;
}

/**
 * Opens an "auto-destructible" HDF5 attribute
 */
static void delete_h5attribute (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Aclose(*p);
    if (err < 0) {
      bob::core::error << "H5Aclose() exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
    }
  }
  delete p;
}

static boost::shared_ptr<hid_t> open_attribute
(const boost::shared_ptr<hid_t> location, const std::string& name,
 const bob::io::base::HDF5Type& t) {

  boost::shared_ptr<hid_t> retval(new hid_t(-1),
      std::ptr_fun(delete_h5attribute));

  *retval = H5Aopen(*location, name.c_str(), H5P_DEFAULT);

  if (*retval < 0) throw status_error("H5Aopen", *retval);

  //checks if the opened attribute is compatible w/ the expected type
  bob::io::base::HDF5Type expected;
  boost::shared_ptr<hid_t> atype = get_type(*retval);
  if (H5Tget_class(*atype) == H5T_STRING) {
    expected = bob::io::base::HDF5Type(atype);
  }
  else {
    boost::shared_ptr<hid_t> aspace = get_memspace(*retval);
    bob::io::base::HDF5Shape shape = get_extents(*aspace);
    expected = bob::io::base::HDF5Type(atype, shape);
  }

  if (expected != t) {
    boost::format m("Trying to access attribute '%s' with incompatible buffer - expected `%s', but you gave me `%s'");
    m % name % expected.str() % t.str();
    throw std::runtime_error(m.str());
  }

  return retval;
}

void bob::io::base::detail::hdf5::delete_attribute (boost::shared_ptr<hid_t> location,
    const std::string& name) {
  herr_t err = H5Adelete(*location, name.c_str());
  if (err < 0) throw status_error("H5Adelete", err);
}

void bob::io::base::detail::hdf5::read_attribute (const boost::shared_ptr<hid_t> location,
    const std::string& name, const bob::io::base::HDF5Type& dest,
    void* buffer) {
  boost::shared_ptr<hid_t> attribute = open_attribute(location, name, dest);
  herr_t err = H5Aread(*attribute, *dest.htype(), buffer);
  if (err < 0) throw status_error("H5Aread", err);
}

void bob::io::base::detail::hdf5::gettype_attribute (const boost::shared_ptr<hid_t> location,
    const std::string& name, bob::io::base::HDF5Type& type) {

  boost::shared_ptr<hid_t> attr(new hid_t(-1),
      std::ptr_fun(delete_h5attribute));

  *attr = H5Aopen(*location, name.c_str(), H5P_DEFAULT);

  if (*attr < 0) throw status_error("H5Aopen", *attr);

  boost::shared_ptr<hid_t> atype = get_type(*attr);
  if (H5Tget_class(*atype) == H5T_STRING) {
    type = bob::io::base::HDF5Type(atype);
  }
  else {
    boost::shared_ptr<hid_t> aspace = get_memspace(*attr);
    bob::io::base::HDF5Shape shape = get_extents(*aspace);
    type = bob::io::base::HDF5Type(atype, shape);
  }
}

static boost::shared_ptr<hid_t> create_attribute(boost::shared_ptr<hid_t> loc,
    const std::string& name, const bob::io::base::HDF5Type& t,
    boost::shared_ptr<hid_t> space) {

  boost::shared_ptr<hid_t> retval(new hid_t(-1),
      std::ptr_fun(delete_h5attribute));

  *retval = H5Acreate2(*loc, name.c_str(), *t.htype(), *space, H5P_DEFAULT,
      H5P_DEFAULT);

  if (*retval < 0) throw status_error("H5Acreate", *retval);
  return retval;
}

void bob::io::base::detail::hdf5::write_attribute (boost::shared_ptr<hid_t> location,
    const std::string& name, const bob::io::base::HDF5Type& dest, const void* buffer)
{
  boost::shared_ptr<hid_t> dataspace;
  //strings have to be treated slightly differently
  if (dest.type() == bob::io::base::s) {
    hsize_t strings = 1;
    HDF5Shape shape(1, &strings);
    dataspace = open_memspace(shape);
  }
  else {
    dataspace = open_memspace(dest.shape());
  }

  if (bob::io::base::detail::hdf5::has_attribute(location, name)) bob::io::base::detail::hdf5::delete_attribute(location, name);
  boost::shared_ptr<hid_t> attribute =
    create_attribute(location, name, dest, dataspace);

  /* Write the attribute data. */
  herr_t err = H5Awrite(*attribute, *dest.htype(), buffer);
  if (err < 0) throw status_error("H5Awrite", err);
}

static herr_t attr_iterator (hid_t obj, const char* name, const H5A_info_t*,
    void* cookie) {
  std::map<std::string, bob::io::base::HDF5Type>& dict =
    *static_cast<std::map<std::string, bob::io::base::HDF5Type>*>(cookie);

  boost::shared_ptr<hid_t> attr(new hid_t(-1),
      std::ptr_fun(delete_h5attribute));

  *attr = H5Aopen(obj, name, H5P_DEFAULT);

  if (*attr < 0) throw status_error("H5Aopen", *attr);

  boost::shared_ptr<hid_t> atype = get_type(*attr);
  if (H5Tget_class(*atype) == H5T_STRING) {
    dict[name] = bob::io::base::HDF5Type(atype);
  }
  else {
    boost::shared_ptr<hid_t> aspace = get_memspace(*attr);
    bob::io::base::HDF5Shape shape = get_extents(*aspace);
    dict[name] = bob::io::base::HDF5Type(atype, shape);
  }

  return 0;
}

void bob::io::base::detail::hdf5::list_attributes(boost::shared_ptr<hid_t> location,
    std::map<std::string, bob::io::base::HDF5Type>& attributes) {
  hsize_t offset=0;
  H5Aiterate2(*location, H5_INDEX_NAME, H5_ITER_NATIVE, &offset, attr_iterator,
      static_cast<void*>(&attributes));
}
