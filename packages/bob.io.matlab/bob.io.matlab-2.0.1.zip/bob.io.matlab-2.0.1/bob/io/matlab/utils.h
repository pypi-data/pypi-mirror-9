/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 14 May 14:35:08 2014 CEST
 *
 * @brief Utilities to read and write .mat (Matlab) binary files
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_IO_MATLAB_UTILS_H
#define BOB_IO_MATLAB_UTILS_H

#include <map>
#include <string>
#include <boost/shared_ptr.hpp>
#include <matio.h>

#include <bob.io.base/array.h>

/**
 * This method will create a new boost::shared_ptr to mat_t that knows how to
 * delete itself
 */
boost::shared_ptr<mat_t> make_matfile(const char* filename, int flags);

/**
 * Retrieves information about the first variable found on a file.
 */
void mat_peek(const char* filename, bob::io::base::array::typeinfo& info,
    const char* varname=0);

/**
 * Retrieves information about the first variable with a certain name
 * (array_%d) that exists in a .mat file (if it exists)
 */
void mat_peek_set(const char* filename, bob::io::base::array::typeinfo& info,
    const char* varname=0);

/**
 * Retrieves information about all variables with a certain name (array_%d)
 * that exist in a .mat file
 */
boost::shared_ptr<std::map<size_t, std::pair<std::string,
  bob::io::base::array::typeinfo> > > list_variables(const char* filename);

/**
 * Reads a variable on the (already opened) mat_t file. If you don't
 * specify the variable name, I'll just read the next one. Re-allocates the
 * buffer if required.
 */
void read_array (boost::shared_ptr<mat_t> file,
    bob::io::base::array::interface& buf, const char* varname=0);

/**
 * Appends a single Array into the given matlab file and with a given name
 */
void write_array(boost::shared_ptr<mat_t> file, const char* varname,
    const bob::io::base::array::interface& buf);

#endif /* BOB_IO_MATLAB_UTILS_H */
