/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 14 May 14:42:44 2014 CEST
 *
 * @brief Implements the matlab (.mat) array codec using matio
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <algorithm>
#include <boost/make_shared.hpp>
#include <boost/filesystem.hpp>
#include <boost/format.hpp>

#include "utils.h"
#include "file.h"

/**
 * TODO:
 * 1. Current known limitation: does not support full read-out of all data if
 * an array_read() is issued. What we do, presently, is just to read the first
 * variable.
 */
class MatFile: public bob::io::base::File {

  public: //api

    MatFile(const char* path, char mode):
      m_filename(path),
      m_mode( (mode=='r')? MAT_ACC_RDONLY : MAT_ACC_RDWR ),
      m_map(new std::map<size_t, std::pair<std::string, bob::io::base::array::typeinfo> >()),
      m_size(0) {
        if (mode == 'r' || mode == 'a') try_reload_map();
        if (mode == 'w' && boost::filesystem::exists(path)) boost::filesystem::remove(path);
      }

    virtual ~MatFile() { }

    void try_reload_map () {
      if (boost::filesystem::exists(m_filename)) {
        m_map = list_variables(m_filename.c_str());
        m_type = m_map->begin()->second.second;
        m_size = m_map->size();
        m_id.reserve(m_size);
        for (map_type::iterator
            it = m_map->begin(); it != m_map->end(); ++it) {
          m_id.push_back(it->first);
        }
        std::sort(m_id.begin(), m_id.end()); //get the right order...

        //double checks some parameters
        if (m_type.nd == 0 || m_type.nd > 4) {
          boost::format m("number of dimensions for object at file `%s' (%u) exceeds the maximum supported (%u)");
          m % m_filename % m_type.nd % BOB_MAX_DIM;
          throw std::runtime_error(m.str());
        }
        if (m_type.dtype == bob::io::base::array::t_unknown) {
          boost::format m("unsupported data type while loading matlab file `%s': %s");
          m % m_filename % m_type.str();
          throw std::runtime_error(m.str());
        }
      }
    }

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
      return m_size;
    }

    virtual const char* name() const {
      return s_codecname.c_str();
    }

    virtual void read_all(bob::io::base::array::interface& buffer) {

      //do we need to reload the file?
      if (!m_type.is_valid()) try_reload_map();

      //now open it for reading
      boost::shared_ptr<mat_t> mat = make_matfile(m_filename.c_str(), m_mode);

      if (!mat) {
        boost::format f("uninitialized matlab file (%s) cannot be read");
        f % m_filename;
        throw std::runtime_error(f.str());
      }

      read_array(mat, buffer);

    }

    virtual void read(bob::io::base::array::interface& buffer, size_t index) {

      //do we need to reload the file?
      if (!m_type.is_valid()) try_reload_map();

      //now open it for reading
      boost::shared_ptr<mat_t> mat = make_matfile(m_filename.c_str(), m_mode);

      if (!mat) {
        boost::format f("uninitialized matlab file (%s) cannot be read");
        f % m_filename;
        throw std::runtime_error(f.str());
      }

      read_array(mat, buffer, (*m_map)[m_id[index]].first.c_str());

    }

    virtual size_t append (const bob::io::base::array::interface& buffer) {

      //do we need to reload the file?
      if (!m_type.is_valid()) try_reload_map();

      //now open it for writing.
      boost::shared_ptr<mat_t> mat =
        make_matfile(m_filename.c_str(), m_mode);

      if (!mat) {
        boost::format f("cannot open matlab file at '%s' for writing");
        f % m_filename;
        throw std::runtime_error(f.str());
      }

      //checks typing is right
      if (m_type.is_valid() && !m_type.is_compatible(buffer.type())) {
        boost::format f("cannot append with different buffer type (%s) than the one already initialized (%s)");
        f % buffer.type().str() % m_type.str();
        throw std::runtime_error(f.str());
      }

      //all is good at this point, just write it.

      //choose variable name
      size_t next_index = 0;
      if (m_id.size()) next_index = *m_id.rbegin() + 1;
      std::ostringstream varname("array_");
      varname << next_index;

      write_array(mat, varname.str().c_str(), buffer);

      mat.reset(); ///< force data flushing

      if (!m_type.is_valid()) try_reload_map();
      else {
        //optimization: don't reload the map, just update internal cache
        ++m_size;
        (*m_map)[next_index] = std::make_pair(varname.str(), buffer.type());
        m_id.push_back(next_index);
      }

      return m_size-1;
    }

    virtual void write (const bob::io::base::array::interface& buffer) {

      static const char* varname = "array";

      //this file is supposed to hold a single array. delete it if it exists
      boost::filesystem::path path (m_filename);
      if (boost::filesystem::exists(m_filename)) boost::filesystem::remove(m_filename);

      boost::shared_ptr<mat_t> mat = make_matfile(m_filename.c_str(),
          m_mode);
      if (!mat) {
        boost::format f("cannot open matlab file at '%s' for writing");
        f % m_filename;
        throw std::runtime_error(f.str());
      }

      write_array(mat, varname, buffer);

      mat.reset(); ///< forces data flushing (not really required here...)

      //updates internal map w/o looking to the output file.
      m_size = 1;
      (*m_map)[0] = std::make_pair(varname, buffer.type());
      m_id.push_back(0);

    }

  private: //representation

    typedef std::map<size_t, std::pair<std::string, bob::io::base::array::typeinfo> > map_type;

    std::string m_filename;
    enum mat_acc m_mode;
    boost::shared_ptr<map_type> m_map;
    bob::io::base::array::typeinfo m_type;
    size_t       m_size;
    std::vector<size_t> m_id;

    static std::string s_codecname;

};

std::string MatFile::s_codecname = "bob.matlab";

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
boost::shared_ptr<bob::io::base::File> make_file (const char* path, char mode) {
  return boost::make_shared<MatFile>(path, mode);
}
