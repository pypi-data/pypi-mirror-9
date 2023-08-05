/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 29 Feb 17:24:10 2012
 *
 * @brief Describes HDF5 groups.
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IO_BASE_HDF5GROUP_H
#define BOB_IO_BASE_HDF5GROUP_H

#include <boost/shared_ptr.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <hdf5.h>

#include <bob.io.base/HDF5Types.h>
#include <bob.io.base/HDF5Dataset.h>
#include <bob.io.base/HDF5Attribute.h>

namespace bob { namespace io { namespace base { namespace detail { namespace hdf5 {

  class File;

  /**
   * A group represents a path inside the HDF5 file. It can contain Datasets or
   * other Groups.
   */
  class Group: public boost::enable_shared_from_this<Group> {

    public: //better to protect?

      /**
       * Creates a new group in a given parent.
       */
      Group(boost::shared_ptr<Group> parent, const std::string& name);

      /**
       * Binds to an existing group in a parent, reads all the group contents
       * recursively. Note that the last parameter is there only to
       * differentiate from the above constructor. It is ignored.
       */
      Group(boost::shared_ptr<Group> parent,  const std::string& name,
          bool open);

      /**
       * Constructor used by the root group, just open the root group
       */
      Group(boost::shared_ptr<File> parent);

      /**
       * Recursively open sub-groups and datasets. This cannot be done at the
       * constructor because of a enable_shared_from_this<> restriction that
       * results in a bad weak pointer exception being raised.
       */
      void open_recursively();

    public: //api

      /**
       * D'tor - presently, does nothing
       */
      virtual ~Group();

      /**
       * Get parent group
       */
      virtual const boost::shared_ptr<Group> parent() const;
      virtual boost::shared_ptr<Group> parent();

      /**
       * Filename where I'm sitting
       */
      virtual const std::string& filename() const;

      /**
       * Full path to myself. Constructed each time it is called.
       */
      virtual std::string path() const;

      /**
       * Access file
       */
      virtual const boost::shared_ptr<File> file() const;
      virtual boost::shared_ptr<File> file();

      /**
       * My name
       */
      virtual const std::string& name() const {
        return m_name;
      }

      /**
       * Deletes all children nodes and properties in this group.
       *
       * Note that removing data already written in a file will only be
       * effective in terms of space saving when you actually re-write that
       * file. This instruction just unlinks all data from this group and makes
       * them inaccessible to any further read operation.
       */
      virtual void reset();

      /**
       * Accesses the current location id of this group
       */
      const boost::shared_ptr<hid_t> location() const {
        return m_id;
      }

      boost::shared_ptr<hid_t> location() {
        return m_id;
      }

      /**
       * Path with filename. Constructed each time it is called.
       */
      virtual std::string url() const;

      /**
       * move up-down on the group hierarchy
       */
      virtual boost::shared_ptr<Group> cd(const std::string& path);
      virtual const boost::shared_ptr<Group> cd(const std::string& path) const;

      /**
       * Get a mapping of all child groups
       */
      virtual const std::map<std::string, boost::shared_ptr<Group> >& groups()
        const {
        return m_groups;
      }

      /**
       * Create a new subgroup with a given name.
       */
      virtual boost::shared_ptr<Group> create_group(const std::string& name);

      /**
       * Deletes an existing subgroup with a given name. If a relative name is
       * given, it is interpreted w.r.t. to this group.
       *
       * Note that removing data already written in a file will only be
       * effective in terms of space saving when you actually re-write that
       * file. This instruction just unlinks all data from this group and makes
       * them inaccessible to any further read operation.
       */
      virtual void remove_group(const std::string& path);

      /**
       * Rename an existing group under me.
       */
      virtual void rename_group(const std::string& from, const std::string& to);

      /**
       * Copies all data from an existing group into myself, creating a new
       * subgroup, by default, with the same name as the other group. If a
       * relative name is given, it is interpreted w.r.t. to this group.
       *
       * If an empty string is given as "dir", copies the other group name.
       */
      virtual void copy_group(const boost::shared_ptr<Group> other, const
          std::string& path="");

      /**
       * Says if a group with a certain path exists in this group.
       */
      virtual bool has_group(const std::string& path) const;

      /**
       * Get all datasets attached to this group
       */
      virtual const std::map<std::string, boost::shared_ptr<Dataset> >&
        datasets() const {
          return m_datasets;
        }

      /**
       * Creates a new HDF5 dataset from scratch and inserts it in this group.
       * If the Dataset already exists on file and the types are compatible, we
       * attach to that type, otherwise, we raise an exception.
       *
       * You can set if you would like to have the dataset created as a list
       * and the compression level.
       *
       * The effect of setting "list" to false is that the created dataset:
       *
       * a) Will not be expandible (chunked) b) Will contain the exact number
       * of dimensions of the input type.
       *
       * When you set "list" to true (the default), datasets are created with
       * chunking automatically enabled (the chunk size is set to the size of
       * the given variable) and an extra dimension is inserted to accomodate
       * list operations.
       */
      virtual boost::shared_ptr<Dataset> create_dataset
        (const std::string& path, const bob::io::base::HDF5Type& type, bool list=true,
         size_t compression=0);

      /**
       * Deletes a dataset in this group
       *
       * Note that removing data already written in a file will only be
       * effective in terms of space saving when you actually re-write that
       * file. This instruction just unlinks all data from this group and makes
       * them inaccessible to any further read operation.
       */
      virtual void remove_dataset(const std::string& path);

      /**
       * Rename an existing dataset under me.
       */
      virtual void rename_dataset(const std::string& from,
          const std::string& to);

      /**
       * Copies the contents of the given dataset into this. By default, use
       * the same name.
       */
      virtual void copy_dataset(const boost::shared_ptr<Dataset> other,
          const std::string& path="");

      /**
       * Says if a dataset with a certain name exists in the current file.
       */
      virtual bool has_dataset(const std::string& path) const;

      /**
       * Accesses a certain dataset from this group
       */
      boost::shared_ptr<Dataset> operator[] (const std::string& path);
      const boost::shared_ptr<Dataset> operator[] (const std::string& path) const;

      /**
       * Accesses all existing paths in one shot. Input has to be a std
       * container with T = std::string and accepting push_back()
       */
      template <typename T> void dataset_paths (T& container) const {
        for (std::map<std::string, boost::shared_ptr<io::base::detail::hdf5::Dataset> >::const_iterator it=m_datasets.begin(); it != m_datasets.end(); ++it) container.push_back(it->second->path());
        for (std::map<std::string, boost::shared_ptr<io::base::detail::hdf5::Group> >::const_iterator it=m_groups.begin(); it != m_groups.end(); ++it) it->second->dataset_paths(container);
      }

      /**
       * Accesses all existing sub-groups in one shot. Input has to be a std
       * container with T = std::string and accepting push_back()
       */
      template <typename T> void subgroup_paths (T& container, bool recursive = true) const {
        for (std::map<std::string, boost::shared_ptr<io::base::detail::hdf5::Group> >::const_iterator it=m_groups.begin(); it != m_groups.end(); ++it){
          container.push_back(it->first);
          if (recursive){
            unsigned pos = container.size();
            it->second->subgroup_paths(container);
            for (unsigned p = pos; p < container.size(); ++p){
              container[p] = it->first + "/" + container[p];
            }
          }
        }
      }

      /**
       * Callback function for group iteration. Two cases are blessed here:
       *
       * 1. Object is another group. In this case just instantiate the group and
       *    recursively iterate from there
       * 2. Object is a dataset. Instantiate it.
       *
       * Only hard-links are considered. At the time being, no soft links.
       */
      herr_t iterate_callback(hid_t group, const char *name,
          const H5L_info_t *info);

    public: //attribute support

      /**
       * Gets the current type set for an attribute
       */
      void gettype_attribute(const std::string& name, HDF5Type& type) const;

      /**
       * Sets a scalar attribute on the current group. Setting an existing
       * attribute overwrites its value.
       *
       * @note Only simple scalars are supported for the time being
       */
      template <typename T> void set_attribute(const std::string& name,
          const T& v) {
        bob::io::base::HDF5Type dest_type(v);
        write_attribute(name, dest_type, reinterpret_cast<const void*>(&v));
      }

      /**
       * Reads an attribute from the current group. Raises an error if such
       * attribute does not exist on the group. To check for existence, use
       * has_attribute().
       */
      template <typename T> T get_attribute(const std::string& name) const {
        T v;
        bob::io::base::HDF5Type dest_type(v);
        read_attribute(name, dest_type, reinterpret_cast<void*>(&v));
        return v;
      }

      /**
       * Checks if a certain attribute exists in this group.
       */
      bool has_attribute(const std::string& name) const;

      /**
       * Deletes an attribute
       */
      void delete_attribute(const std::string& name);

      /**
       * List attributes available on this dataset.
       */
      void list_attributes(std::map<std::string, bob::io::base::HDF5Type>& attributes) const;

    public: //array attribute support

      /**
       * Sets a array attribute on the current group. Setting an existing
       * attribute overwrites its value. If the attribute exists it is erased
       * and re-written.
       */
      template <typename T, int N> void set_array_attribute(const std::string& name,
          const blitz::Array<T,N>& v) {
        bob::io::base::HDF5Type dest_type(v);
        if(!bob::core::array::isCZeroBaseContiguous(v)) {
          blitz::Array<T,N> tmp = bob::core::array::ccopy(v);
          write_attribute(name, dest_type, reinterpret_cast<const void*>(tmp.data()));
        }
        else {
          write_attribute(name, dest_type, reinterpret_cast<const void*>(v.data()));
        }
      }

      /**
       * Reads an attribute from the current dataset. Raises an error if such
       * attribute does not exist on the group. To check for existence, use
       * has_attribute().
       */
      template <typename T, int N> blitz::Array<T,N> get_array_attribute
        (const std::string& name) const {
        blitz::Array<T,N> v;
        bob::io::base::HDF5Type dest_type(v);
        read_attribute(name, dest_type, reinterpret_cast<void*>(v.data()));
        return v;
      }

      /**
       * Reads an attribute from the current dataset. Places the data in an
       * already allocated array.
       */
      template <typename T, int N> void get_array_attribute
        (const std::string& name, blitz::Array<T,N>& v) const {
        bob::io::base::HDF5Type dest_type(v);
        read_attribute(name, dest_type, reinterpret_cast<void*>(v.data()));
      }

    public: //buffer attribute support

      /**
       * Reads an attribute into a user buffer. It is the user's responsibility
       * to have a buffer that represents the given type.
       */
      void read_attribute (const std::string& name,
          const bob::io::base::HDF5Type& dest, void* buffer) const;

      /**
       * Writes the contents of a given buffer into the attribute.
       */
      void write_attribute (const std::string& name,
          const bob::io::base::HDF5Type& dest, const void* buffer);

    private: //not implemented

      /**
       * Copies the contents of an existing group -- not implemented
       */
      Group(const Group& other);

      /**
       * Assigns the contents of an existing group to myself -- not
       * implemented
       */
      Group& operator= (const Group& other);

    private: //representation

      std::string m_name; ///< my name
      boost::shared_ptr<hid_t> m_id; ///< the HDF5 Group this object points to
      boost::weak_ptr<Group> m_parent;
      std::map<std::string, boost::shared_ptr<Group> > m_groups;
      std::map<std::string, boost::shared_ptr<Dataset> > m_datasets;
      //std::map<std::string, boost::shared_ptr<Attribute> > m_attributes;

  };

  /**
   * The RootGroup is a special case of the Group object that is directly
   * attached to the File (no parents).
   */
  class RootGroup: public Group {

    public: //api

      /**
       * Binds to the root group of a file.
       */
      RootGroup(boost::shared_ptr<File> parent);

      /**
       * D'tor - presently, does nothing
       */
      virtual ~RootGroup();

      /**
       * Get parent group
       */
      virtual const boost::shared_ptr<Group> parent() const {
        return boost::shared_ptr<Group>();
      }

      /**
       * Get parent group
       */
      virtual boost::shared_ptr<Group> parent() {
        return boost::shared_ptr<Group>();
      }

      /**
       * Filename where I'm sitting
       */
      virtual const std::string& filename() const;

      /**
       * Full path to myself. Constructed each time it is called.
       */
      virtual std::string path() const {
        return "";
      }

      /**
       * Access file
       */
      virtual const boost::shared_ptr<File> file() const {
        return m_parent.lock();
      }

      virtual boost::shared_ptr<File> file() {
        return m_parent.lock();
      }

    private: //representation

      boost::weak_ptr<File> m_parent; ///< the file I belong to

  };

  /**
   * std::string specialization
   */
  template <> void Group::set_attribute<std::string>(const std::string& name, const std::string& v);
  template <> std::string Group::get_attribute(const std::string& name) const;

}}}}}

#endif /* BOB_IO_BASE_HDF5GROUP_H */
