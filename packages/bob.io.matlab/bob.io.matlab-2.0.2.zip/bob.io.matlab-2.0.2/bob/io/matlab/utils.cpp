/**
 * @file io/cxx/MatUtils.cc
 * @date Wed Jun 22 17:50:08 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implementation of MatUtils (handling of matlab .mat files)
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include "utils.h"

#include <boost/format.hpp>
#include <boost/filesystem.hpp>
#include <bob.io.base/reorder.h>

#if MATIO_MAJOR_VERSION > 1 || (MATIO_MAJOR_VERSION == 1 && MATIO_MINOR_VERSION > 3)
#define MATIO_1_3_OR_OLDER 0
#else
#define MATIO_1_3_OR_OLDER 1
#endif

boost::shared_ptr<mat_t> make_matfile(const char* filename, int flags) {
  if ((flags == MAT_ACC_RDWR) && !boost::filesystem::exists(filename)) {
    return boost::shared_ptr<mat_t>(Mat_Create(filename, 0), std::ptr_fun(Mat_Close));
  }
  return boost::shared_ptr<mat_t>(Mat_Open(filename, flags), std::ptr_fun(Mat_Close));
}

/**
 * This method will create a new boost::shared_ptr to matvar_t that knows how
 * to delete itself
 *
 * You pass it the file and the variable name to be read out or a combination
 * of parameters required to build a new matvar_t from scratch (see matio API
 * for details).
 */
static boost::shared_ptr<matvar_t> make_matvar(boost::shared_ptr<mat_t>& file) {

  return boost::shared_ptr<matvar_t>(Mat_VarReadNext(file.get()), std::ptr_fun(Mat_VarFree));

}

/**
 * This is essentially like make_matvar(), but uses VarReadNextInfo() instead
 * of VarReadNext(), so it does not load the data, but it is faster.
 */
static boost::shared_ptr<matvar_t>
make_matvar_info(boost::shared_ptr<mat_t>& file) {

  return boost::shared_ptr<matvar_t>(Mat_VarReadNextInfo(file.get()), std::ptr_fun(Mat_VarFree));

}

static boost::shared_ptr<matvar_t> make_matvar(boost::shared_ptr<mat_t>& file,
   const char* varname) {

  if (!varname) {
    throw std::runtime_error("empty variable name - cannot lookup the file this way");
  }
  return boost::shared_ptr<matvar_t>(Mat_VarRead(file.get(), const_cast<char*>(varname)), std::ptr_fun(Mat_VarFree));

}

/**
 * Returns the MAT_C_* enumeration for the given ElementType
 */
static enum matio_classes mio_class_type (bob::io::base::array::ElementType i) {
  switch (i) {
    case bob::io::base::array::t_int8:
      return MAT_C_INT8;
    case bob::io::base::array::t_int16:
      return MAT_C_INT16;
    case bob::io::base::array::t_int32:
      return MAT_C_INT32;
    case bob::io::base::array::t_int64:
      return MAT_C_INT64;
    case bob::io::base::array::t_uint8:
      return MAT_C_UINT8;
    case bob::io::base::array::t_uint16:
      return MAT_C_UINT16;
    case bob::io::base::array::t_uint32:
      return MAT_C_UINT32;
    case bob::io::base::array::t_uint64:
      return MAT_C_UINT64;
    case bob::io::base::array::t_float32:
      return MAT_C_SINGLE;
    case bob::io::base::array::t_complex64:
      return MAT_C_SINGLE;
    case bob::io::base::array::t_float64:
      return MAT_C_DOUBLE;
    case bob::io::base::array::t_complex128:
      return MAT_C_DOUBLE;
    default:
      {
        boost::format f("data type '%s' is not supported by matio backend");
        f % bob::io::base::array::stringize(i);
        throw std::runtime_error(f.str());
      }
  }
}

/**
 * Returns the MAT_T_* enumeration for the given ElementType
 */
static enum matio_types mio_data_type (bob::io::base::array::ElementType i) {
  switch (i) {
    case bob::io::base::array::t_int8:
      return MAT_T_INT8;
    case bob::io::base::array::t_int16:
      return MAT_T_INT16;
    case bob::io::base::array::t_int32:
      return MAT_T_INT32;
    case bob::io::base::array::t_int64:
      return MAT_T_INT64;
    case bob::io::base::array::t_uint8:
      return MAT_T_UINT8;
    case bob::io::base::array::t_uint16:
      return MAT_T_UINT16;
    case bob::io::base::array::t_uint32:
      return MAT_T_UINT32;
    case bob::io::base::array::t_uint64:
      return MAT_T_UINT64;
    case bob::io::base::array::t_float32:
      return MAT_T_SINGLE;
    case bob::io::base::array::t_complex64:
      return MAT_T_SINGLE;
    case bob::io::base::array::t_float64:
      return MAT_T_DOUBLE;
    case bob::io::base::array::t_complex128:
      return MAT_T_DOUBLE;
    default:
      {
        boost::format f("data type '%s' is not supported by matio backend");
        f % bob::io::base::array::stringize(i);
        throw std::runtime_error(f.str());
      }
  }
}

/**
 * Returns the ElementType given the matio MAT_T_* enum and a flag indicating
 * if the array is complex or not (also returned by matio at matvar_t)
 */
static bob::io::base::array::ElementType bob_element_type (int mio_type, bool is_complex) {

  bob::io::base::array::ElementType eltype = bob::io::base::array::t_unknown;

  switch(mio_type) {

    case(MAT_T_INT8):
      eltype = bob::io::base::array::t_int8;
      break;
    case(MAT_T_INT16):
      eltype = bob::io::base::array::t_int16;
      break;
    case(MAT_T_INT32):
      eltype = bob::io::base::array::t_int32;
      break;
    case(MAT_T_INT64):
      eltype = bob::io::base::array::t_int64;
      break;
    case(MAT_T_UINT8):
      eltype = bob::io::base::array::t_uint8;
      break;
    case(MAT_T_UINT16):
      eltype = bob::io::base::array::t_uint16;
      break;
    case(MAT_T_UINT32):
      eltype = bob::io::base::array::t_uint32;
      break;
    case(MAT_T_UINT64):
      eltype = bob::io::base::array::t_uint64;
      break;
    case(MAT_T_SINGLE):
      eltype = bob::io::base::array::t_float32;
      break;
    case(MAT_T_DOUBLE):
      eltype = bob::io::base::array::t_float64;
      break;
    default:
      return bob::io::base::array::t_unknown;
  }

  //if type is complex, it is signalled slightly different
  if (is_complex) {
    if (eltype == bob::io::base::array::t_float32) return bob::io::base::array::t_complex64;
    else if (eltype == bob::io::base::array::t_float64) return bob::io::base::array::t_complex128;
    else return bob::io::base::array::t_unknown;
  }

  return eltype;
}

boost::shared_ptr<matvar_t> make_matvar
(const char* varname, const bob::io::base::array::interface& buf) {

  const bob::io::base::array::typeinfo& info = buf.type();
  char* cdata = new char[info.buffer_size()];
  void* fdata = static_cast<void*>(cdata);

  boost::shared_ptr<matvar_t> retval;
  //matio gets dimensions as integers
# if MATIO_1_3_OR_OLDER == 1
  int mio_dims[BOB_MAX_DIM];
# else
  size_t mio_dims[BOB_MAX_DIM];
# endif
  for (size_t i=0; i<info.nd; ++i) mio_dims[i] = info.shape[i];

  switch (info.dtype) {
    case bob::io::base::array::t_complex64:
    case bob::io::base::array::t_complex128:
    case bob::io::base::array::t_complex256:
      {
        //special treatment for complex arrays
        uint8_t* real = static_cast<uint8_t*>(fdata);
        uint8_t* imag = real + (info.buffer_size()/2);
        bob::io::base::row_to_col_order_complex(buf.ptr(), real, imag, info);
#       if MATIO_1_3_OR_OLDER == 1
        ComplexSplit mio_complex = {real, imag};
#       else
        mat_complex_split_t mio_complex = {real, imag};
#       endif
        retval.reset(Mat_VarCreate(varname,
              mio_class_type(info.dtype), mio_data_type(info.dtype),
              info.nd, mio_dims, static_cast<void*>(&mio_complex),
              MAT_F_COMPLEX),
            std::ptr_fun(Mat_VarFree));
      }
    default:
      break;
  }

  if (!retval){
    bob::io::base::row_to_col_order(buf.ptr(), fdata, info); ///< data copying!

    retval.reset(Mat_VarCreate(varname,
          mio_class_type(info.dtype), mio_data_type(info.dtype),
          info.nd, mio_dims, fdata, 0), std::ptr_fun(Mat_VarFree));
  }

  delete[] cdata;
  return retval;
}

/**
 * Assigns a single matvar variable to an bob::io::base::array::interface. Re-allocates the buffer
 * if required.
 */
static void assign_array (boost::shared_ptr<matvar_t> matvar, bob::io::base::array::interface& buf) {

  bob::io::base::array::typeinfo info(bob_element_type(matvar->data_type, matvar->isComplex),
#     if MATIO_1_3_OR_OLDER == 1
      matvar->rank, matvar->dims);
#     else
      (size_t)matvar->rank, matvar->dims);
#     endif

  if(!buf.type().is_compatible(info)) buf.set(info);

  if (matvar->isComplex) {
#   if MATIO_1_3_OR_OLDER == 1
    ComplexSplit mio_complex = *static_cast<ComplexSplit*>(matvar->data);
#   else
    mat_complex_split_t mio_complex = *static_cast<mat_complex_split_t*>(matvar->data);
#   endif
    bob::io::base::col_to_row_order_complex(mio_complex.Re, mio_complex.Im, buf.ptr(), info);
  }
  else bob::io::base::col_to_row_order(matvar->data, buf.ptr(), info);

}

void read_array (boost::shared_ptr<mat_t> file, bob::io::base::array::interface& buf,
    const char* varname) {

  boost::shared_ptr<matvar_t> matvar;
  if (varname) matvar = make_matvar(file, varname);
  else matvar = make_matvar(file);
  if (!matvar) {
    boost::format m("mat file variable could not be created - error while reading object `%s'");
    m % varname;
    throw std::runtime_error(m.str());
  }
  assign_array(matvar, buf);

}

void write_array(boost::shared_ptr<mat_t> file,
    const char* varname, const bob::io::base::array::interface& buf) {

  boost::shared_ptr<matvar_t> matvar = make_matvar(varname, buf);
# if MATIO_1_3_OR_OLDER == 1
  Mat_VarWrite(file.get(), matvar.get(), 0);
# else
  Mat_VarWrite(file.get(), matvar.get(), (matio_compression)0);
# endif

}

/**
 * Given a matvar_t object, returns our equivalent bob::io::base::array::typeinfo struct.
 */
static void get_var_info(boost::shared_ptr<const matvar_t> matvar,
    bob::io::base::array::typeinfo& info) {
  info.set(bob_element_type(matvar->data_type, matvar->isComplex),
#     if MATIO_1_3_OR_OLDER == 1
      matvar->rank, matvar->dims);
#     else
      (size_t)matvar->rank, matvar->dims);
#     endif
}

void mat_peek(const char* filename, bob::io::base::array::typeinfo& info, const char* varname) {

  boost::shared_ptr<mat_t> mat = make_matfile(filename, MAT_ACC_RDONLY);
  if (!mat) {
    boost::format m("cannot open file `%s'");
    m % filename;
    throw std::runtime_error(m.str());
  }
  boost::shared_ptr<matvar_t> matvar = varname ? make_matvar(mat,varname) : make_matvar(mat); //gets the given variable name
  if (!matvar) {
    if (varname){
      boost::format m("Cannot locate variable `%s' in file '%s'");
      m % varname % filename;
      throw std::runtime_error(m.str());
    }else{
      boost::format m("Cannot find any variable in file '%s'");
      m % filename;
      throw std::runtime_error(m.str());
    }
  }
  get_var_info(matvar, info);

}

void mat_peek_set(const char* filename, bob::io::base::array::typeinfo& info, const char* varname) {
  boost::shared_ptr<mat_t> mat = make_matfile(filename, MAT_ACC_RDONLY);
  if (!mat) {
    boost::format m("cannot open file `%s'");
    m % filename;
    throw std::runtime_error(m.str());
  }
  boost::shared_ptr<matvar_t> matvar = varname ? make_matvar(mat,varname) : make_matvar(mat); //gets the first var.
  if (!matvar) {
    if (varname){
      boost::format m("Cannot locate variable `%s' in file '%s'");
      m % varname % filename;
      throw std::runtime_error(m.str());
    }else{
      boost::format m("Cannot find any variable in file '%s'");
      m % filename;
      throw std::runtime_error(m.str());
    }
  }
  get_var_info(matvar, info);
}

boost::shared_ptr<std::map<size_t, std::pair<std::string, bob::io::base::array::typeinfo> > >
list_variables(const char* filename) {

  boost::shared_ptr<std::map<size_t, std::pair<std::string, bob::io::base::array::typeinfo> > > retval(new std::map<size_t, std::pair<std::string, bob::io::base::array::typeinfo> >());

  boost::shared_ptr<mat_t> mat = make_matfile(filename, MAT_ACC_RDONLY);
  if (!mat) {
    boost::format m("cannot open file `%s'");
    m % filename;
    throw std::runtime_error(m.str());
  }
  boost::shared_ptr<matvar_t> matvar = make_matvar(mat); //gets the first var.

  size_t id = 0;

  //now that we have found a variable, fill the array
  //properties taking that variable as basis
  (*retval)[id] = std::make_pair(matvar->name, bob::io::base::array::typeinfo());
  get_var_info(matvar, (*retval)[id].second);
  const bob::io::base::array::typeinfo& type_cache = (*retval)[id].second;

  if ((*retval)[id].second.dtype == bob::io::base::array::t_unknown) {
    boost::format m("unknown data type (%s) for object named `%s' at file `%s'");
    m % (*retval)[id].second.str() % id % filename;
    throw std::runtime_error(m.str());
  }

  //if we got here, just continue counting the variables inside. we
  //only read their info since that is faster -- but attention! if we just read
  //the varinfo, we don't get typing correct, so we copy that from the previous
  //read variable and hope for the best.

  while ((matvar = make_matvar_info(mat))) {
    (*retval)[++id] = std::make_pair(matvar->name, type_cache);
  }

  return retval;
}
