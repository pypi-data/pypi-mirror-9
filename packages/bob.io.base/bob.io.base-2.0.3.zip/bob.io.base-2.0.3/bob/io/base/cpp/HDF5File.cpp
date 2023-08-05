/**
 * @date Wed Jun 22 17:50:08 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implementation of the read/write functionality for HDF5 files
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/format.hpp>

#include <bob.io.base/HDF5File.h>

static unsigned int getH5Access (bob::io::base::HDF5File::mode_t v) {
  switch(v) {
    case 0: return H5F_ACC_RDONLY;
    case 1: return H5F_ACC_RDWR;
    case 2: return H5F_ACC_TRUNC;
    case 4: return H5F_ACC_EXCL;
    default:
            {
              boost::format m("Trying to use an undefined access mode '%d'");
              m % v;
              throw std::runtime_error(m.str());
            }
  }
}

bob::io::base::HDF5File::HDF5File(const std::string& filename, mode_t mode):
  m_file(new bob::io::base::detail::hdf5::File(filename, getH5Access(mode))),
  m_cwd(m_file->root()) ///< we start by looking at the root directory
{
}

bob::io::base::HDF5File::HDF5File(const std::string& filename, const char mode):
m_file(),
m_cwd()
{
  bob::io::base::HDF5File::mode_t new_mode = bob::io::base::HDF5File::inout;
  switch (mode){
    case 'r': new_mode = bob::io::base::HDF5File::in; break;
    case 'a': new_mode = bob::io::base::HDF5File::inout; break;
    case 'w': new_mode = bob::io::base::HDF5File::trunc; break;
    case 'x': new_mode = bob::io::base::HDF5File::excl; break;
    default:
      throw std::runtime_error("Supported flags are 'r' (read-only), 'a' (read/write/append), 'w' (read/write/truncate) or 'x' (read/write/exclusive)");
  }
  m_file.reset(new bob::io::base::detail::hdf5::File(filename, getH5Access(new_mode)));
  m_cwd = m_file->root(); ///< we start by looking at the root directory

}

bob::io::base::HDF5File::HDF5File(const bob::io::base::HDF5File& other_file):
  m_file(other_file.m_file),
  m_cwd(other_file.m_cwd)
{
}

bob::io::base::HDF5File::~HDF5File() {
}

bob::io::base::HDF5File& bob::io::base::HDF5File::operator =(const bob::io::base::HDF5File& other_file){
  m_file = other_file.m_file;
  m_cwd = other_file.m_cwd;
  return *this;
}

void bob::io::base::HDF5File::close() {
  m_file.reset();
  m_cwd.reset();
}

void bob::io::base::HDF5File::cd(const std::string& path) {
  check_open();
  m_cwd = m_cwd->cd(path);
}

bool bob::io::base::HDF5File::hasGroup(const std::string& path) {
  check_open();
  return m_cwd->has_group(path);
}

void bob::io::base::HDF5File::createGroup(const std::string& path) {
  check_open();
  if (!m_file->writable()) {
    boost::format m("cannot create group '%s' at path '%s' of file '%s' because it is not writeable");
    m % path % m_cwd->path() % m_file->filename();
    throw std::runtime_error(m.str());
  }
  m_cwd->create_group(path);
}

std::string bob::io::base::HDF5File::cwd() const {
  check_open();
  return m_cwd->path();
}

bool bob::io::base::HDF5File::contains (const std::string& path) const {
  check_open();
  return m_cwd->has_dataset(path);
}

const std::vector<bob::io::base::HDF5Descriptor>& bob::io::base::HDF5File::describe
(const std::string& path) const {
  check_open();
  return (*m_cwd)[path]->m_descr;
}

void bob::io::base::HDF5File::unlink (const std::string& path) {
  check_open();
  if (!m_file->writable()) {
    boost::format m("cannot remove dataset at path '%s' of file '%s' because it is not writeable");
    m % path % m_cwd->path() % m_file->filename();
    throw std::runtime_error(m.str());
  }
  m_cwd->remove_dataset(path);
}

void bob::io::base::HDF5File::rename (const std::string& from, const std::string& to) {
  check_open();
  if (!m_file->writable()) {
    boost::format m("cannot rename dataset '%s' -> '%s' at path '%s' of file '%s' because it is not writeable");
    m % from % to % m_cwd->path() % m_file->filename();
    throw std::runtime_error(m.str());
  }
  m_cwd->rename_dataset(from, to);
  std::string current_path = m_cwd->path();
  m_file->reset(); //re-read the whole structure
  m_cwd = m_file->root();
  m_cwd = m_cwd->cd(current_path); //go back to the path we were before
}

void bob::io::base::HDF5File::copy (HDF5File& other) {
  check_open();
  if (!m_file->writable()) {
    boost::format m("cannot copy data of file '%s' to path '%s' of file '%s' because it is not writeable");
    m % other.filename() % m_cwd->path() % m_file->filename();
    throw std::runtime_error(m.str());
  }

  //groups
  typedef std::map<std::string, boost::shared_ptr<bob::io::base::detail::hdf5::Group> > group_map_type;
  const group_map_type& group_map = other.m_file->root()->groups();
  for (group_map_type::const_iterator it=group_map.begin();
      it != group_map.end(); ++it) {
    m_cwd->copy_group(it->second, it->first);
  }

  //datasets
  typedef std::map<std::string, boost::shared_ptr<bob::io::base::detail::hdf5::Dataset> > dataset_map_type;
  const dataset_map_type& dataset_map = other.m_file->root()->datasets();
  for (dataset_map_type::const_iterator it=dataset_map.begin();
      it != dataset_map.end(); ++it) {
    m_cwd->copy_dataset(it->second, it->first);
  }
}

void bob::io::base::HDF5File::create (const std::string& path, const bob::io::base::HDF5Type& type,
    bool list, size_t compression) {
  check_open();
  if (!m_file->writable()) {
    boost::format m("cannot create dataset '%s' at path '%s' of file '%s' because it is not writeable");
    m % path % m_cwd->path() % m_file->filename();
    throw std::runtime_error(m.str());
  }
  if (!contains(path)) m_cwd->create_dataset(path, type, list, compression);
  else (*m_cwd)[path]->size(type);
}

void bob::io::base::HDF5File::read_buffer (const std::string& path, size_t pos,
    const bob::io::base::HDF5Type& type, void* buffer) const {
  check_open();
  (*m_cwd)[path]->read_buffer(pos, type, buffer);
}

void bob::io::base::HDF5File::write_buffer (const std::string& path,
    size_t pos, const bob::io::base::HDF5Type& type, const void* buffer) {
  check_open();
  if (!m_file->writable()) {
    boost::format m("cannot write to object '%s' at path '%s' of file '%s' because it is not writeable");
    m % path % m_cwd->path() % m_file->filename();
    throw std::runtime_error(m.str());
  }
  (*m_cwd)[path]->write_buffer(pos, type, buffer);
}

void bob::io::base::HDF5File::extend_buffer(const std::string& path,
    const bob::io::base::HDF5Type& type, const void* buffer) {
  check_open();
  if (!m_file->writable()) {
    boost::format m("cannot extend object '%s' at path '%s' of file '%s' because the file is not writeable");
    m % path % m_cwd->path() % m_file->filename();
    throw std::runtime_error(m.str());
  }
  (*m_cwd)[path]->extend_buffer(type, buffer);
}

bool bob::io::base::HDF5File::hasAttribute(const std::string& path,
    const std::string& name) const {
  check_open();
  if (m_cwd->has_dataset(path)) {
    return (*m_cwd)[path]->has_attribute(name);
  }
  else if (m_cwd->has_group(path)) {
    return m_cwd->cd(path)->has_attribute(name);
  }
  return false;
}

void bob::io::base::HDF5File::getAttributeType(const std::string& path,
    const std::string& name, HDF5Type& type) const {
  check_open();
  if (m_cwd->has_dataset(path)) {
    (*m_cwd)[path]->gettype_attribute(name, type);
  }
  else if (m_cwd->has_group(path)) {
    m_cwd->cd(path)->gettype_attribute(name, type);
  }
  else {
    boost::format m("cannot read attribute '%s' type at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
    m % name % path % m_file->filename() % m_cwd->path();
    throw std::runtime_error(m.str());
  }
}

void bob::io::base::HDF5File::deleteAttribute(const std::string& path,
    const std::string& name) {
  check_open();
  if (m_cwd->has_dataset(path)) {
    (*m_cwd)[path]->delete_attribute(name);
  }
  else if (m_cwd->has_group(path)) {
    m_cwd->cd(path)->delete_attribute(name);
  }
  else {
    boost::format m("cannot delete attribute '%s' at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
    m % name % path % m_file->filename() % m_cwd->path();
    throw std::runtime_error(m.str());
  }
}

void bob::io::base::HDF5File::listAttributes(const std::string& path,
    std::map<std::string, bob::io::base::HDF5Type>& attributes) const {
  check_open();
  if (m_cwd->has_dataset(path)) {
    (*m_cwd)[path]->list_attributes(attributes);
  }
  else if (m_cwd->has_group(path)) {
    m_cwd->cd(path)->list_attributes(attributes);
  }
  else {
    boost::format m("cannot list attributes at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
    m % path % m_file->filename() % m_cwd->path();
    throw std::runtime_error(m.str());
  }
}

void bob::io::base::HDF5File::read_attribute(const std::string& path,
    const std::string& name, const bob::io::base::HDF5Type& type, void* buffer) const {
  check_open();
  if (m_cwd->has_dataset(path)) {
    (*m_cwd)[path]->read_attribute(name, type, buffer);
  }
  else if (m_cwd->has_group(path)) {
    m_cwd->cd(path)->read_attribute(name, type, buffer);
  }
  else {
    boost::format m("cannot get attribute '%s' at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
    m % name % path % m_file->filename() % m_cwd->path();
    throw std::runtime_error(m.str());
  }
}

void bob::io::base::HDF5File::write_attribute(const std::string& path,
    const std::string& name, const bob::io::base::HDF5Type& type, const void* buffer) {
  check_open();
  if (m_cwd->has_dataset(path)) {
    (*m_cwd)[path]->write_attribute(name, type, buffer);
  }
  else if (m_cwd->has_group(path)) {
    m_cwd->cd(path)->write_attribute(name, type, buffer);
  }
  else {
    boost::format m("cannot set attribute '%s' at path/dataset '%s' of file '%s' (cwd: '%s') because this path/dataset does not currently exist");
    m % name % path % m_file->filename() % m_cwd->path();
    throw std::runtime_error(m.str());
  }
}

void bob::io::base::HDF5File::check_open() const{
  if (!m_cwd || ! m_file){
    throw std::runtime_error("The file is not opened yet / any more");
  }
}
