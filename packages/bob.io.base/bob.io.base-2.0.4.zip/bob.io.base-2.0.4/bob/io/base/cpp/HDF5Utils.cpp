/**
 * @date Wed Jun 22 17:50:08 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implements a set of utilities to read HDF5 files.
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/format.hpp>
#include <boost/make_shared.hpp>

#include <bob.core/logging.h>

#include <bob.io.base/HDF5Utils.h>

/**
 * Opens/Creates an "auto-destructible" HDF5 file
 */
static void delete_h5file (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Fclose(*p);
    if (err < 0) {
      bob::core::error << "H5Fclose(hid=" << *p << ") exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
    }
  }
  delete p;
}

/**
 * Opens/Creates and "auto-destructible" HDF5 file creation property list
 */
static void delete_h5p (hid_t* p) {
  if (*p >= 0) {
    herr_t err = H5Pclose(*p);
    if (err < 0) {
      bob::core::error << "H5Pclose(hid=" << *p << ") exited with an error (" << err << "). The stack trace follows:" << std::endl;
      bob::core::error << bob::io::base::format_hdf5_error() << std::endl;
      return;
    }
  }
  delete p;
}

static boost::shared_ptr<hid_t> open_file(const boost::filesystem::path& path,
    unsigned int flags, boost::shared_ptr<hid_t>& fcpl) {

  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5file));

  if (!boost::filesystem::exists(path) && flags == H5F_ACC_RDONLY) {
    //file was opened for reading, but does not exist... Raise
    boost::format m("cannot open file `%s'");
    m % path.string();
    throw std::runtime_error(m.str());
  }

  if (boost::filesystem::exists(path) && flags != H5F_ACC_TRUNC) { //open
    *retval = H5Fopen(path.string().c_str(), flags, H5P_DEFAULT);
    if (*retval < 0) {
      boost::format m("call to HDF5 C-function H5Fopen() returned error %d on file '%s'. HDF5 error statck follows:\n%s");
      m % *retval % path.string().c_str() % bob::io::base::format_hdf5_error();
      throw std::runtime_error(m.str());
    }
    //replaces the file create list properties with the one from the file
    fcpl = boost::shared_ptr<hid_t>(new hid_t(-1), std::ptr_fun(delete_h5p));
    *fcpl = H5Fget_create_plist(*retval);
    if (*fcpl < 0) {
      boost::format m("call to HDF5 C-function H5Fget_create_list() returned error %d on file '%s'. HDF5 error statck follows:\n%s");
      m % *fcpl % path.string().c_str() % bob::io::base::format_hdf5_error();
      throw std::runtime_error(m.str());
    }
  }
  else { //file needs to be created or truncated (can set user block)
    *retval = H5Fcreate(path.string().c_str(), H5F_ACC_TRUNC,
        *fcpl, H5P_DEFAULT);
    if (*retval < 0) {
      boost::format m("call to HDF5 C-function H5Fcreate() returned error %d on file '%s'. HDF5 error statck follows:\n%s");
      m % *retval % path.string().c_str() % bob::io::base::format_hdf5_error();
      throw std::runtime_error(m.str());
    }
  }
  return retval;
}

static boost::shared_ptr<hid_t> create_fcpl(hsize_t userblock_size) {
  if (!userblock_size) return boost::make_shared<hid_t>(H5P_DEFAULT);
  //otherwise we have to go through the settings
  boost::shared_ptr<hid_t> retval(new hid_t(-1), std::ptr_fun(delete_h5p));
  *retval = H5Pcreate(H5P_FILE_CREATE);
  if (*retval < 0) {
    boost::format m("call to HDF5 C-function H5Pcreate() returned error %d. HDF5 error statck follows:\n%s");
    m % *retval % bob::io::base::format_hdf5_error();
    throw std::runtime_error(m.str());
  }
  herr_t err = H5Pset_userblock(*retval, userblock_size);
  if (err < 0) {
    boost::format m("call to HDF5 C-function H5Pset_userblock() returned error %d. HDF5 error statck follows:\n%s");
    m % err % bob::io::base::format_hdf5_error();
    throw std::runtime_error(m.str());
  }
  return retval;
}

bob::io::base::detail::hdf5::File::File(const boost::filesystem::path& path, unsigned int flags,
    size_t userblock_size):
  m_path(path),
  m_flags(flags),
  m_fcpl(create_fcpl(userblock_size)),
  m_id(open_file(m_path, m_flags, m_fcpl))
{
}

bob::io::base::detail::hdf5::File::~File() {
}

boost::shared_ptr<bob::io::base::detail::hdf5::RootGroup> bob::io::base::detail::hdf5::File::root() {
  if (!m_root) {
    m_root = boost::make_shared<bob::io::base::detail::hdf5::RootGroup>(shared_from_this());
    m_root->open_recursively();
  }
  return m_root;
}

void bob::io::base::detail::hdf5::File::reset() {
  m_root.reset();
}

void bob::io::base::detail::hdf5::File::flush() {
  herr_t err = H5Fflush(*m_id, H5F_SCOPE_GLOBAL);
  if (err < 0){
    std::runtime_error("H5Fflush returned with an error code.");
  }
}

bool bob::io::base::detail::hdf5::File::writable() const {
  return (m_flags != H5F_ACC_RDONLY);
}

size_t bob::io::base::detail::hdf5::File::userblock_size() const {
  hsize_t retval;
  herr_t err = H5Pget_userblock(*m_fcpl, &retval);
  if (err < 0) {
    boost::format m("Call to HDF5 C-function H5Pget_create_plist() returned error %d. HDF5 error statck follows:\n%s");
    m % err % bob::io::base::format_hdf5_error();
    throw std::runtime_error(m.str());
  }
  return retval;
}

void bob::io::base::detail::hdf5::File::get_userblock(std::string& data) const {
  //TODO
}

void bob::io::base::detail::hdf5::File::set_userblock(const std::string& data) {
  //TODO
}
