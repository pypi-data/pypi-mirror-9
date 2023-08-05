/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 29 Feb 17:51:21 2012
 *
 * @brief Implementation of the Dataset class
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/format.hpp>
#include <boost/make_shared.hpp>
#include <boost/shared_array.hpp>

#include <bob.core/logging.h>

#include <bob.io.base/HDF5Utils.h>
#include <bob.io.base/HDF5Group.h>
#include <bob.io.base/HDF5Dataset.h>

static std::runtime_error status_error(const char* f, herr_t s) {
  boost::format m("call to HDF5 C-function %s() returned error %d. HDF5 error statck follows:\n%s");
  m % f % s % bob::io::base::format_hdf5_error();
  return std::runtime_error(m.str());
}

/**
 * Opens an "auto-destructible" HDF5 dataset
 */
static void delete_h5dataset (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Dclose(*p);
    if (err < 0) {
      bob::core::error << "H5Dclose() exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
    }
  }
  delete p;
}

static boost::shared_ptr<hid_t> open_dataset
(boost::shared_ptr<bob::io::base::detail::hdf5::Group>& par, const std::string& name) {
  if (!name.size() || name == "." || name == "..") {
    boost::format m("Cannot open dataset with illegal name `%s' at `%s:%s'");
    m % name % par->file()->filename() % par->path();
    throw std::runtime_error(m.str());
  }

  boost::shared_ptr<hid_t> retval(new hid_t(-1),
      std::ptr_fun(delete_h5dataset));
  *retval = H5Dopen2(*par->location(), name.c_str(), H5P_DEFAULT);
  if (*retval < 0) {
    throw status_error("H5Dopen2", *retval);
  }
  return retval;
}

/**
 * Opens an "auto-destructible" HDF5 datatype
 */
static void delete_h5datatype (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Tclose(*p);
    if (err < 0) {
      bob::core::error << "H5Tclose() exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
    }
  }
  delete p;
}

static boost::shared_ptr<hid_t> open_datatype
(const boost::shared_ptr<hid_t>& ds) {
  boost::shared_ptr<hid_t> retval(new hid_t(-1),
      std::ptr_fun(delete_h5datatype));
  *retval = H5Dget_type(*ds);
  if (*retval < 0) {
    throw status_error("H5Dget_type", *retval);
  }
  return retval;
}

/**
 * Opens an "auto-destructible" HDF5 property list
 */
static void delete_h5plist (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Pclose(*p);
    if (err < 0) {
      bob::core::error << "H5Pclose() exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
    }
  }
  delete p;
}

static boost::shared_ptr<hid_t> open_plist(hid_t classid) {
  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5plist));
  *retval = H5Pcreate(classid);
  if (*retval < 0) {
    throw status_error("H5Pcreate", *retval);
  }
  return retval;
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

static boost::shared_ptr<hid_t> open_filespace
(const boost::shared_ptr<hid_t>& ds) {
  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5dataspace));
  *retval = H5Dget_space(*ds);
  if (*retval < 0) throw status_error("H5Dget_space", *retval);
  return retval;
}

static boost::shared_ptr<hid_t> open_memspace(const bob::io::base::HDF5Shape& sh) {
  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5dataspace));
  *retval = H5Screate_simple(sh.n(), sh.get(), 0);
  if (*retval < 0) throw status_error("H5Screate_simple", *retval);
  return retval;
}

static void set_memspace(boost::shared_ptr<hid_t> s, const bob::io::base::HDF5Shape& sh) {
  herr_t status = H5Sset_extent_simple(*s, sh.n(), sh.get(), 0);
  if (status < 0) throw status_error("H5Sset_extent_simple", status);
}

/**
 * Figures out if a dataset is expandible
 */
static bool is_extensible(boost::shared_ptr<hid_t>& space) {

  //has unlimited size on first dimension?
  int rank = H5Sget_simple_extent_ndims(*space);
  if (rank < 0) throw status_error("H5Sget_simple_extent_ndims", rank);

  bob::io::base::HDF5Shape maxshape(rank);
  herr_t status = H5Sget_simple_extent_dims(*space, 0, maxshape.get());
  if (status < 0) throw status_error("H5Sget_simple_extent_dims",status);

  return (maxshape[0] == H5S_UNLIMITED);
}

/**
 * Figures out the extents of a dataset
 */
static bob::io::base::HDF5Shape get_extents(boost::shared_ptr<hid_t>& space) {
  int rank = H5Sget_simple_extent_ndims(*space);
  if (rank < 0) throw status_error("H5Sget_simple_extent_ndims", rank);
  //is at least a list of scalars, but could be a list of arrays
  bob::io::base::HDF5Shape shape(rank);
  herr_t status = H5Sget_simple_extent_dims(*space, shape.get(), 0);
  if (status < 0) throw status_error("H5Sget_simple_extent_dims",status);
  return shape;
}

/**
 * Creates the extensive list of compatible types for each of possible ways to
 * read/write this dataset.
 */
static void reset_compatibility_list(boost::shared_ptr<hid_t>& space,
    const bob::io::base::HDF5Type& file_base, std::vector<bob::io::base::HDF5Descriptor>& descr) {

  if (!file_base.shape()) throw std::runtime_error("empty HDF5 dataset");

  descr.clear();

  switch (file_base.shape().n()) {

    case 1: ///< file type has 1 dimension
      descr.push_back(bob::io::base::HDF5Descriptor(file_base.type(),
            file_base.shape()[0], is_extensible(space)));
      break;

    case 2:
    case 3:
    case 4:
    case 5:
      {
        bob::io::base::HDF5Shape alt = file_base.shape();
        alt <<= 1; ///< contract shape
        descr.push_back(bob::io::base::HDF5Descriptor(bob::io::base::HDF5Type(file_base.type(), alt),
              file_base.shape()[0], is_extensible(space)).subselect());
      }
      break;

    default:
      {
        boost::format m("%d exceeds the number of supported dimensions");
        m % file_base.shape().n();
        throw std::runtime_error(m.str());
      }
  }

  //can always read the data as a single, non-expandible array
  descr.push_back(bob::io::base::HDF5Descriptor(file_base, 1, false));
}

bob::io::base::detail::hdf5::Dataset::Dataset(boost::shared_ptr<Group> parent,
    const std::string& name) :
  m_parent(parent),
  m_name(name),
  m_id(open_dataset(parent, name)),
  m_dt(open_datatype(m_id)),
  m_filespace(open_filespace(m_id)),
  m_descr(),
  m_memspace()
{
  bob::io::base::HDF5Type type(m_dt, get_extents(m_filespace));
  reset_compatibility_list(m_filespace, type, m_descr);

  //strings have to be treated slightly differently
  if (H5Tget_class(*m_dt) == H5T_STRING) {
    hsize_t strings = 1;
    HDF5Shape shape(1, &strings);
    m_memspace = open_memspace(shape);
  }
  else {
    m_memspace = open_memspace(m_descr[0].type.shape());
  }
}

/**
 * Creates and writes an "empty" Dataset in an existing file.
 */
static void create_dataset (boost::shared_ptr<bob::io::base::detail::hdf5::Group> par,
 const std::string& name, const bob::io::base::HDF5Type& type, bool list,
 size_t compression) {

  if (!name.size() || name == "." || name == "..") {
    boost::format m("Cannot create dataset with illegal name `%s' at `%s:%s'");
    m % name % par->file()->filename() % par->path();
    throw std::runtime_error(m.str());
  }

  bob::io::base::HDF5Shape xshape(type.shape());

  if (list) { ///< if it is a list, add and extra dimension as dimension 0
    xshape = type.shape();
    xshape >>= 1;
    xshape[0] = 0; ///< no elements for the time being
  }

  bob::io::base::HDF5Shape maxshape(xshape);
  if (list) maxshape[0] = H5S_UNLIMITED; ///< can expand forever

  //creates the data space.
  boost::shared_ptr<hid_t> space(new hid_t(-1),
      std::ptr_fun(delete_h5dataspace));
  *space = H5Screate_simple(xshape.n(), xshape.get(), maxshape.get());
  if (*space < 0) throw status_error("H5Screate_simple", *space);

  //creates the property list saying we need the data to be chunked if this is
  //supposed to be a list -- HDF5 only supports expandability like this.
  boost::shared_ptr<hid_t> dcpl = open_plist(H5P_DATASET_CREATE);

  //according to the HDF5 manual, chunks have to have the same rank as the
  //array shape.
  bob::io::base::HDF5Shape chunking(xshape);
  chunking[0] = 1;
  if (list || compression) { ///< note: compression requires chunking
    herr_t status = H5Pset_chunk(*dcpl, chunking.n(), chunking.get());
    if (status < 0) throw status_error("H5Pset_chunk", status);
  }

  //if the user has decided to compress the dataset, do it with gzip.
  if (compression) {
    if (compression > 9) compression = 9;
    herr_t status = H5Pset_deflate(*dcpl, compression);
    if (status < 0) throw status_error("H5Pset_deflate", status);
  }

  //our link creation property list for HDF5
  boost::shared_ptr<hid_t> lcpl = open_plist(H5P_LINK_CREATE);
  herr_t status = H5Pset_create_intermediate_group(*lcpl, 1); //1 == true
  if (status < 0)
    throw status_error("H5Pset_create_intermediate_group", status);

  //please note that we don't define the fill value as in the example, but
  //according to the HDF5 documentation, this value is set to zero by default.

  boost::shared_ptr<hid_t> cls = type.htype();

  //finally create the dataset on the file.
  boost::shared_ptr<hid_t> dataset(new hid_t(-1),
      std::ptr_fun(delete_h5dataset));
  *dataset = H5Dcreate2(*par->location(), name.c_str(),
      *cls, *space, *lcpl, *dcpl, H5P_DEFAULT);

  if (*dataset < 0) throw status_error("H5Dcreate2", *dataset);
}

/**
 * Creates and writes an "empty" std::string Dataset in an existing file.
 */
static void create_string_dataset (boost::shared_ptr<bob::io::base::detail::hdf5::Group> par,
 const std::string& name, const bob::io::base::HDF5Type& type, size_t compression) {

  if (!name.size() || name == "." || name == "..") {
    boost::format m("Cannot create dataset with illegal name `%s' at `%s:%s'");
    m % name % par->file()->filename() % par->path();
    throw std::runtime_error(m.str());
  }

  //there can be only 1 string in a string dataset (for the time being)
  hsize_t strings = 1;
  bob::io::base::HDF5Shape xshape(1, &strings);

  //creates the data space.
  boost::shared_ptr<hid_t> space(new hid_t(-1),
      std::ptr_fun(delete_h5dataspace));
  *space = H5Screate_simple(xshape.n(), xshape.get(), xshape.get());
  if (*space < 0) throw status_error("H5Screate_simple", *space);

  //creates the property list saying we need the data to be chunked if this is
  //supposed to be a list -- HDF5 only supports expandability like this.
  boost::shared_ptr<hid_t> dcpl = open_plist(H5P_DATASET_CREATE);

  //if the user has decided to compress the dataset, do it with gzip.
  if (compression) {
    if (compression > 9) compression = 9;
    herr_t status = H5Pset_deflate(*dcpl, compression);
    if (status < 0) throw status_error("H5Pset_deflate", status);
  }

  //our link creation property list for HDF5
  boost::shared_ptr<hid_t> lcpl = open_plist(H5P_LINK_CREATE);
  herr_t status = H5Pset_create_intermediate_group(*lcpl, 1); //1 == true
  if (status < 0)
    throw status_error("H5Pset_create_intermediate_group", status);

  //please note that we don't define the fill value as in the example, but
  //according to the HDF5 documentation, this value is set to zero by default.

  boost::shared_ptr<hid_t> cls = type.htype();

  //finally create the dataset on the file.
  boost::shared_ptr<hid_t> dataset(new hid_t(-1),
      std::ptr_fun(delete_h5dataset));
  *dataset = H5Dcreate2(*par->location(), name.c_str(),
      *cls, *space, *lcpl, *dcpl, H5P_DEFAULT);

  if (*dataset < 0) throw status_error("H5Dcreate2", *dataset);
}

bob::io::base::detail::hdf5::Dataset::Dataset(boost::shared_ptr<Group> parent,
    const std::string& name, const bob::io::base::HDF5Type& type,
    bool list, size_t compression):
  m_parent(parent),
  m_name(name),
  m_id(),
  m_dt(),
  m_filespace(),
  m_descr(),
  m_memspace()
{
  //First, we test to see if we can find the named dataset.
  bob::io::base::DefaultHDF5ErrorStack->mute();
  hid_t set_id = H5Dopen2(*parent->location(),m_name.c_str(),H5P_DEFAULT);
  bob::io::base::DefaultHDF5ErrorStack->unmute();

  if (set_id < 0) {
    if (type.type() == bob::io::base::s)
      create_string_dataset(parent, m_name, type, compression);
    else
      create_dataset(parent, m_name, type, list, compression);
  }
  else H5Dclose(set_id); //close it, will re-open it properly

  m_id = open_dataset(parent, m_name);
  m_dt = open_datatype(m_id);
  m_filespace = open_filespace(m_id);
  bob::io::base::HDF5Type file_type(m_dt, get_extents(m_filespace));
  reset_compatibility_list(m_filespace, file_type, m_descr);

  //strings have to be treated slightly differently
  if (H5Tget_class(*m_dt) == H5T_STRING) {
    hsize_t strings = 1;
    HDF5Shape shape(1, &strings);
    m_memspace = open_memspace(shape);
  }
  else {
    m_memspace = open_memspace(m_descr[0].type.shape());
  }
}

bob::io::base::detail::hdf5::Dataset::~Dataset() { }

size_t bob::io::base::detail::hdf5::Dataset::size () const {
  return m_descr[0].size;
}

size_t bob::io::base::detail::hdf5::Dataset::size (const bob::io::base::HDF5Type& type) const {
  for (size_t k=0; k<m_descr.size(); ++k) {
    if (m_descr[k].type == type) return m_descr[k].size;
  }
  boost::format m("trying to read or write `%s' at `%s' that only accepts `%s'");
  m % type.str() % url() % m_descr[0].type.str();
  throw std::runtime_error(m.str());
}

const boost::shared_ptr<bob::io::base::detail::hdf5::Group> bob::io::base::detail::hdf5::Dataset::parent() const {
  return m_parent.lock();
}

boost::shared_ptr<bob::io::base::detail::hdf5::Group> bob::io::base::detail::hdf5::Dataset::parent() {
  return m_parent.lock();
}

const std::string& bob::io::base::detail::hdf5::Dataset::filename() const {
  return parent()->filename();
}

std::string bob::io::base::detail::hdf5::Dataset::url() const {
  return filename() + ":" + path();
}

std::string bob::io::base::detail::hdf5::Dataset::path() const {
  return parent()->path() + "/" + m_name;
}

const boost::shared_ptr<bob::io::base::detail::hdf5::File> bob::io::base::detail::hdf5::Dataset::file() const {
  return parent()->file();
}

boost::shared_ptr<bob::io::base::detail::hdf5::File> bob::io::base::detail::hdf5::Dataset::file() {
  return parent()->file();
}

/**
 * Locates a compatible type or returns end().
 */
static std::vector<bob::io::base::HDF5Descriptor>::iterator
  find_type_index(std::vector<bob::io::base::HDF5Descriptor>& descr,
      const bob::io::base::HDF5Type& user_type) {
  std::vector<bob::io::base::HDF5Descriptor>::iterator it = descr.begin();
  for (; it != descr.end(); ++it) {
    if (it->type == user_type) break;
  }
  return it;
}

std::vector<bob::io::base::HDF5Descriptor>::iterator
bob::io::base::detail::hdf5::Dataset::select (size_t index, const bob::io::base::HDF5Type& dest) {

  //finds compatibility type
  std::vector<bob::io::base::HDF5Descriptor>::iterator it = find_type_index(m_descr, dest);

  //if we cannot find a compatible type, we throw
  if (it == m_descr.end()) {
    boost::format m("trying to read or write `%s' at `%s' that only accepts `%s'");
    m % dest.str() % url() % m_descr[0].type.str();
    throw std::runtime_error(m.str());
  }

  //checks indexing
  if (index >= it->size) {
    boost::format m("trying to access element %d in Dataset '%s' that only contains %d elements");
    m % index % url() % it->size;
    throw std::runtime_error(m.str());
  }

  set_memspace(m_memspace, it->type.shape());

  it->hyperslab_start[0] = index;

  herr_t status = H5Sselect_hyperslab(*m_filespace, H5S_SELECT_SET,
      it->hyperslab_start.get(), 0, it->hyperslab_count.get(), 0);
  if (status < 0) throw status_error("H5Sselect_hyperslab", status);

  return it;
}

void bob::io::base::detail::hdf5::Dataset::read_buffer (size_t index, const bob::io::base::HDF5Type& dest, void* buffer) {

  std::vector<bob::io::base::HDF5Descriptor>::iterator it = select(index, dest);

  herr_t status = H5Dread(*m_id, *it->type.htype(),
      *m_memspace, *m_filespace, H5P_DEFAULT, buffer);

  if (status < 0) throw status_error("H5Dread", status);
}

void bob::io::base::detail::hdf5::Dataset::write_buffer (size_t index, const bob::io::base::HDF5Type& dest,
    const void* buffer) {

  std::vector<bob::io::base::HDF5Descriptor>::iterator it = select(index, dest);

  herr_t status = H5Dwrite(*m_id, *it->type.htype(),
      *m_memspace, *m_filespace, H5P_DEFAULT, buffer);

  if (status < 0) throw status_error("H5Dwrite", status);
}

void bob::io::base::detail::hdf5::Dataset::extend_buffer (const bob::io::base::HDF5Type& dest, const void* buffer) {

  //finds compatibility type
  std::vector<bob::io::base::HDF5Descriptor>::iterator it = find_type_index(m_descr, dest);

  //if we cannot find a compatible type, we throw
  if (it == m_descr.end()) {
    boost::format m("trying to read or write `%s' at `%s' that only accepts `%s'");
    m % dest.str() % url() % m_descr[0].type.str();
    throw std::runtime_error(m.str());
  }

  if (!it->expandable) {
    boost::format m("trying to append to '%s' that is not expandible");
    m % url();
    throw std::runtime_error(m.str());
  }

  //if it is expandible, try expansion
  bob::io::base::HDF5Shape tmp(it->type.shape());
  tmp >>= 1;
  tmp[0] = it->size + 1;
  herr_t status = H5Dset_extent(*m_id, tmp.get());
  if (status < 0) throw status_error("H5Dset_extent", status);

  //if expansion succeeded, update all compatible types
  for (size_t k=0; k<m_descr.size(); ++k) {
    if (m_descr[k].expandable) { //updated only the length
      m_descr[k].size += 1;
    }
    else { //not expandable, update the shape/count for a straight read/write
      m_descr[k].type.shape()[0] += 1;
      m_descr[k].hyperslab_count[0] += 1;
    }
  }

  m_filespace = open_filespace(m_id); //update filespace

  write_buffer(tmp[0]-1, dest, buffer);
}

void bob::io::base::detail::hdf5::Dataset::gettype_attribute(const std::string& name,
          bob::io::base::HDF5Type& type) const {
  bob::io::base::detail::hdf5::gettype_attribute(m_id, name, type);
}

bool bob::io::base::detail::hdf5::Dataset::has_attribute(const std::string& name) const {
  return bob::io::base::detail::hdf5::has_attribute(m_id, name);
}

void bob::io::base::detail::hdf5::Dataset::delete_attribute (const std::string& name) {
  bob::io::base::detail::hdf5::delete_attribute(m_id, name);
}

void bob::io::base::detail::hdf5::Dataset::read_attribute (const std::string& name,
    const bob::io::base::HDF5Type& dest_type, void* buffer) const {
  bob::io::base::detail::hdf5::read_attribute(m_id, name, dest_type, buffer);
}

void bob::io::base::detail::hdf5::Dataset::write_attribute (const std::string& name,
    const bob::io::base::HDF5Type& dest_type, const void* buffer) {
  bob::io::base::detail::hdf5::write_attribute(m_id, name, dest_type, buffer);
}

void bob::io::base::detail::hdf5::Dataset::list_attributes(std::map<std::string, bob::io::base::HDF5Type>& attributes) const {
  bob::io::base::detail::hdf5::list_attributes(m_id, attributes);
}

template <> void bob::io::base::detail::hdf5::Dataset::read<std::string>(size_t index, std::string& value) {
  if (index != 0) throw std::runtime_error("Bob's HDF5 bindings do not (yet) support string vectors - reading something on position > 0 is therefore not possible");

  size_t str_size = H5Tget_size(*m_dt); ///< finds out string size
  boost::shared_array<char> storage(new char[str_size+1]);
  storage[str_size] = 0; ///< null termination

  herr_t status = H5Dread(*m_id, *m_dt, *m_memspace, *m_filespace, H5P_DEFAULT, storage.get());
  if (status < 0) throw status_error("H5Dread", status);

  value = storage.get();
}

template <> void bob::io::base::detail::hdf5::Dataset::replace<std::string>(size_t index, const std::string& value) {
  if (index != 0) throw std::runtime_error("Bob's HDF5 bindings do not (yet) support string vectors - indexing something on position > 0 is therefore not possible");

  herr_t status = H5Dwrite(*m_id, *m_dt, *m_memspace, *m_filespace, H5P_DEFAULT, value.c_str());
  if (status < 0) throw status_error("H5Dwrite", status);
}

template <> void bob::io::base::detail::hdf5::Dataset::add<std::string>(const std::string& value) {
  herr_t status = H5Dwrite(*m_id, *m_dt, *m_memspace, *m_filespace, H5P_DEFAULT, value.c_str());
  if (status < 0) throw status_error("H5Dwrite", status);
}

template <> void bob::io::base::detail::hdf5::Dataset::set_attribute<std::string>(const std::string& name, const std::string& v) {
  bob::io::base::HDF5Type dest_type(v);
  write_attribute(name, dest_type, reinterpret_cast<const void*>(v.c_str()));
}

template <> std::string bob::io::base::detail::hdf5::Dataset::get_attribute(const std::string& name) const {
  HDF5Type type;
  gettype_attribute(name, type);
  boost::shared_array<char> v(new char[type.shape()[0]+1]);
  v[type.shape()[0]] = 0; ///< null termination
  read_attribute(name, type, reinterpret_cast<void*>(v.get()));
  std::string retval(v.get());
  return retval;
}
