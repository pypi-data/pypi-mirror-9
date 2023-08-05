/**
 * @file io/cxx/ImageNetpbmFile.cc
 * @date Tue Oct 9 18:13:00 2012 +0200
 * @author Laurent El Shafey <laurent.el-shafey@idiap.ch>
 *
 * @brief Implements an image format reader/writer using libnetpbm.
 * This codec is only able to work with 2D and 3D input.
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/filesystem.hpp>
#include <boost/shared_array.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/make_shared.hpp>
#include <boost/format.hpp>
#include <boost/algorithm/string.hpp>
#include <string>

#include <bob.io.base/File.h>

extern "C" {
// This header must come last, as it brings a lot of global stuff that messes up other headers...
#include <pam.h>
}

static boost::shared_ptr<std::FILE> make_cfile(const char *filename, const char *flags)
{
  std::FILE* fp;
  if(strcmp(flags, "r") == 0)
    fp = pm_openr(filename);
  else // write
    fp = pm_openw(filename);
  if(fp == 0) {
    boost::format m("cannot open file `%s'");
    m % filename;
    throw std::runtime_error(m.str());
  }
  return boost::shared_ptr<std::FILE>(fp, pm_close);
}

/**
 * LOADING
 */
static void im_peek(const std::string& path, bob::io::base::array::typeinfo& info) {

  struct pam in_pam;
  boost::shared_ptr<std::FILE> in_file = make_cfile(path.c_str(), "r");
#ifdef PAM_STRUCT_SIZE
  // For version >= 10.23
  pnm_readpaminit(in_file.get(), &in_pam, PAM_STRUCT_SIZE(tuple_type));
#else
  pnm_readpaminit(in_file.get(), &in_pam, sizeof(struct pam));
#endif

  if( in_pam.depth != 1 && in_pam.depth != 3)
  {
    boost::format m("unsupported number of planes (%d) when reading file. Image depth must be 1 or 3.");
    m % in_pam.depth;
    throw std::runtime_error(m.str());
  }

  info.nd = (in_pam.depth == 1? 2 : 3);
  if(info.nd == 2)
  {
    info.shape[0] = in_pam.height;
    info.shape[1] = in_pam.width;
  }
  else
  {
    info.shape[0] = 3;
    info.shape[1] = in_pam.height;
    info.shape[2] = in_pam.width;
  }
  info.update_strides();

  // Set depth
  if (in_pam.bytes_per_sample == 1) info.dtype = bob::io::base::array::t_uint8;
  else if (in_pam.bytes_per_sample == 2) info.dtype = bob::io::base::array::t_uint16;
  else {
    boost::format m("unsupported image depth (%d bytes per samples) when reading file");
    m % in_pam.bytes_per_sample;
    throw std::runtime_error(m.str());
  }
}

template <typename T> static
void im_load_gray(struct pam *in_pam, bob::io::base::array::interface& b) {
  const bob::io::base::array::typeinfo& info = b.type();

  T *element = static_cast<T*>(b.ptr());
  tuple *tuplerow = pnm_allocpamrow(in_pam);
  for(size_t y=0; y<info.shape[0]; ++y)
  {
    pnm_readpamrow(in_pam, tuplerow);
    for(size_t x=0; x<info.shape[1]; ++x)
    {
      *element = tuplerow[x][0];
      ++element;
    }
  }
  pnm_freepamrow(tuplerow);
}

template <typename T> static
void imbuffer_to_rgb(size_t size, const tuple* tuplerow, T* r, T* g, T* b) {
  for (size_t k=0; k<size; ++k) {
    r[k] = tuplerow[k][0];
    g[k] = tuplerow[k][1];
    b[k] = tuplerow[k][2];
  }
}

template <typename T> static
void im_load_color(struct pam *in_pam, bob::io::base::array::interface& b) {
  const bob::io::base::array::typeinfo& info = b.type();

  long unsigned int frame_size = info.shape[2] * info.shape[1];
  T *element_r = static_cast<T*>(b.ptr());
  T *element_g = element_r+frame_size;
  T *element_b = element_g+frame_size;

  int row_color_stride = info.shape[2]; // row_stride for each component
  tuple *tuplerow = pnm_allocpamrow(in_pam);
  for(size_t y=0; y<info.shape[1]; ++y)
  {
    pnm_readpamrow(in_pam, tuplerow);
    imbuffer_to_rgb(row_color_stride, tuplerow, element_r, element_g, element_b);
    element_r += row_color_stride;
    element_g += row_color_stride;
    element_b += row_color_stride;
  }
  pnm_freepamrow(tuplerow);
}

static void im_load (const std::string& filename, bob::io::base::array::interface& b) {

  struct pam in_pam;
  boost::shared_ptr<std::FILE> in_file = make_cfile(filename.c_str(), "r");
#ifdef PAM_STRUCT_SIZE
  // For version >= 10.23
  pnm_readpaminit(in_file.get(), &in_pam, PAM_STRUCT_SIZE(tuple_type));
#else
  pnm_readpaminit(in_file.get(), &in_pam, sizeof(struct pam));
#endif

  const bob::io::base::array::typeinfo& info = b.type();

  if (info.dtype == bob::io::base::array::t_uint8) {
    if(info.nd == 2) im_load_gray<uint8_t>(&in_pam, b);
    else if( info.nd == 3) im_load_color<uint8_t>(&in_pam, b);
    else {
      boost::format m("(netpbm) unsupported image type found in file `%s': %s");
      m % filename % info.str();
      throw std::runtime_error(m.str());
    }
  }

  else if (info.dtype == bob::io::base::array::t_uint16) {
    if(info.nd == 2) im_load_gray<uint16_t>(&in_pam, b);
    else if( info.nd == 3) im_load_color<uint16_t>(&in_pam, b);
    else {
      boost::format m("(netpbm) unsupported image type found in file `%s': %s");
      m % filename % info.str();
      throw std::runtime_error(m.str());
    }
  }

  else {
    boost::format m("(netpbm) unsupported image type found in file `%s': %s");
    m % filename % info.str();
    throw std::runtime_error(m.str());
  }
}

/**
 * SAVING
 */
template <typename T>
static void im_save_gray(const bob::io::base::array::interface& b, struct pam *out_pam) {
  const bob::io::base::array::typeinfo& info = b.type();

  const T *element = static_cast<const T*>(b.ptr());

  tuple *tuplerow = pnm_allocpamrow(out_pam);
  for(size_t y=0; y<info.shape[0]; ++y) {
    for(size_t x=0; x<info.shape[1]; ++x) {
      tuplerow[x][0] = *element;
      ++element;
    }
    pnm_writepamrow(out_pam, tuplerow);
  }
  pnm_freepamrow(tuplerow);
}

template <typename T> static
void rgb_to_imbuffer(size_t size, const T* r, const T* g, const T* b, tuple* tuplerow) {
  for (size_t k=0; k<size; ++k) {
    tuplerow[k][0] = r[k];
    tuplerow[k][1] = g[k];
    tuplerow[k][2] = b[k];
  }
}

template <typename T>
static void im_save_color(const bob::io::base::array::interface& b, struct pam *out_pam) {
  const bob::io::base::array::typeinfo& info = b.type();

  long unsigned int frame_size = info.shape[2] * info.shape[1];
  const T *element_r = static_cast<const T*>(b.ptr());
  const T *element_g = element_r + frame_size;
  const T *element_b = element_g + frame_size;

  int row_color_stride = info.shape[2]; // row_stride for each component
  tuple *tuplerow = pnm_allocpamrow(out_pam);
  for(size_t y=0; y<info.shape[1]; ++y) {
    rgb_to_imbuffer(row_color_stride, element_r, element_g, element_b, tuplerow);
    pnm_writepamrow(out_pam, tuplerow);
    element_r += row_color_stride;
    element_g += row_color_stride;
    element_b += row_color_stride;
  }
  pnm_freepamrow(tuplerow);
}

static void im_save (const std::string& filename, const bob::io::base::array::interface& array) {

  const bob::io::base::array::typeinfo& info = array.type();

  struct pam out_pam;
  boost::shared_ptr<std::FILE> out_file = make_cfile(filename.c_str(), "w");

  std::string ext = boost::filesystem::path(filename).extension().c_str();
  boost::algorithm::to_lower(ext);

  // Sets the parameters of the pam structure according to the bca::interface properties
  out_pam.size = sizeof(out_pam);
#ifdef PAM_STRUCT_SIZE
  // For version >= 10.23
  out_pam.len = PAM_STRUCT_SIZE(tuple_type);
#else
  out_pam.len = out_pam.size;
#endif
  out_pam.file = out_file.get();
  out_pam.plainformat = 0; // writes in binary
  out_pam.height = (info.nd == 2 ? info.shape[0] : info.shape[1]);
  out_pam.width = (info.nd == 2 ? info.shape[1] : info.shape[2]);
  out_pam.depth = (info.nd == 2 ? 1 : 3);
  out_pam.maxval = (bob::io::base::array::t_uint8 ? 255 : 65535);
  out_pam.bytes_per_sample = (info.dtype == bob::io::base::array::t_uint8 ? 1 : 2);
  out_pam.format = PAM_FORMAT;
  if( ext.compare(".pbm") == 0)
  {
    out_pam.maxval = 1;
    out_pam.format = PBM_FORMAT;
    strcpy(out_pam.tuple_type, PAM_PBM_TUPLETYPE);
  }
  else if( ext.compare(".pgm") == 0)
  {
    out_pam.format = PGM_FORMAT;
    strcpy(out_pam.tuple_type, PAM_PGM_TUPLETYPE);
  }
  else
  {
    out_pam.format = PPM_FORMAT;
    strcpy(out_pam.tuple_type, PAM_PPM_TUPLETYPE);
  }

  if(out_pam.depth == 3 && ext.compare(".ppm")) {
    throw std::runtime_error("cannot save a color image into a file of this type.");
  }

  // Writes header in file
  pnm_writepaminit(&out_pam);

  // Writes content
  if(info.dtype == bob::io::base::array::t_uint8) {

    if(info.nd == 2) im_save_gray<uint8_t>(array, &out_pam);
    else if(info.nd == 3) {
      if(info.shape[0] != 3) throw std::runtime_error("color image does not have 3 planes on 1st. dimension");
      im_save_color<uint8_t>(array, &out_pam);
    }
    else {
      boost::format m("(netpbm) cannot write object of type `%s' to file `%s'");
      m % info.str() % filename;
      throw std::runtime_error(m.str());
    }

  }

  else if(info.dtype == bob::io::base::array::t_uint16) {

    if(info.nd == 2) im_save_gray<uint16_t>(array, &out_pam);
    else if(info.nd == 3) {
      if(info.shape[0] != 3) throw std::runtime_error("color image does not have 3 planes on 1st. dimension");
      im_save_color<uint16_t>(array, &out_pam);
    }
    else {
      boost::format m("(netpbm) cannot write object of type `%s' to file `%s'");
      m % info.str() % filename;
      throw std::runtime_error(m.str());
    }

  }

  else {
    boost::format m("(netpbm) cannot write object of type `%s' to file `%s'");
    m % info.str() % filename;
    throw std::runtime_error(m.str());
  }
}



class ImageNetpbmFile: public bob::io::base::File {

  public: //api

    ImageNetpbmFile(const char* path, char mode):
      m_filename(path),
      m_newfile(true) {

        //checks if file exists
        if (mode == 'r' && !boost::filesystem::exists(path)) {
          boost::format m("file '%s' is not readable");
          m % path;
          throw std::runtime_error(m.str());
        }

        if (mode == 'r' || (mode == 'a' && boost::filesystem::exists(path))) {
          {
            im_peek(path, m_type);
            m_length = 1;
            m_newfile = false;
          }
        }
        else {
          m_length = 0;
          m_newfile = true;
        }
      }

    virtual ~ImageNetpbmFile() { }

    virtual const char* filename() const {
      return m_filename.c_str();
    }

    virtual const bob::io::base::array::typeinfo& type_all() const {
      return m_type;
    }

    virtual const bob::io::base::array::typeinfo& type() const {
      return m_type;
    }

    virtual size_t size() const {
      return m_length;
    }

    virtual const char* name() const {
      return s_codecname.c_str();
    }

    virtual void read_all(bob::io::base::array::interface& buffer) {
      read(buffer, 0); ///we only have 1 image in an image file anyways
    }

    virtual void read(bob::io::base::array::interface& buffer, size_t index) {

      if (m_newfile)
        throw std::runtime_error("uninitialized image file cannot be read");

      if (!buffer.type().is_compatible(m_type)) buffer.set(m_type);

      if (index != 0)
        throw std::runtime_error("cannot read image with index > 0 -- there is only one image in an image file");

      if(!buffer.type().is_compatible(m_type)) buffer.set(m_type);
      im_load(m_filename, buffer);
    }

    virtual size_t append (const bob::io::base::array::interface& buffer) {
      if (m_newfile) {
        im_save(m_filename, buffer);
        m_type = buffer.type();
        m_newfile = false;
        m_length = 1;
        return 0;
      }

      throw std::runtime_error("image files only accept a single array");
    }

    virtual void write (const bob::io::base::array::interface& buffer) {
      //overwriting position 0 should always work
      if (m_newfile) {
        append(buffer);
        return;
      }

      throw std::runtime_error("image files only accept a single array");
    }

  private: //representation
    std::string m_filename;
    bool m_newfile;
    bob::io::base::array::typeinfo m_type;
    size_t m_length;

    static std::string s_codecname;

};

std::string ImageNetpbmFile::s_codecname = "bob.image_netpbm";

static bool netpbm_initialized = false;

boost::shared_ptr<bob::io::base::File> make_netpbm_file (const char* path, char mode) {
  if (!netpbm_initialized) {
    pm_init("bob",0);
    netpbm_initialized = true;
  }
  return boost::make_shared<ImageNetpbmFile>(path, mode);
}
