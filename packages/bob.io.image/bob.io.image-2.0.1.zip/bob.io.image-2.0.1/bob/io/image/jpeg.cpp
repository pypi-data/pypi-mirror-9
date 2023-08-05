/**
 * @file io/cxx/ImageJpegFile.cc
 * @date Wed Oct 10 16:38:00 2012 +0200
 * @author Laurent El Shafey <laurent.el-shafey@idiap.ch>
 *
 * @brief Implements an image format reader/writer using libjpeg.
 * This codec is only able to work with 3D input/output.
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/filesystem.hpp>
#include <boost/shared_array.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/make_shared.hpp>
#include <boost/format.hpp>
#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>
#include <string>

#include <bob.io.base/File.h>

#include <jpeglib.h>

// Default JPEG quality
static int s_jpeg_quality = 92;

static boost::shared_ptr<std::FILE> make_cfile(const char *filename, const char *flags)
{
  std::FILE* fp = std::fopen(filename, flags);
  if(fp == 0) {
    boost::format m("the file `%s' could not be opened - verify permissions and availability");
    m % filename;
    throw std::runtime_error(m.str());
  }
  return boost::shared_ptr<std::FILE>(fp, std::fclose);
}


/**
 * ERROR HANDLING
 */
static void my_error_exit (j_common_ptr cinfo){
  // get error message
  char message[JMSG_LENGTH_MAX];
  cinfo->err->format_message(cinfo, message);
  // format error
  boost::format m("Fatal JPEG error (%d) has occurred -> %s");
  m % cinfo->err->msg_code % message;

  // Clean-up JPEG structures IS NOT required,
  // just raise the exception
  throw std::runtime_error(m.str());
}


/**
 * LOADING
 */
static void im_peek(const std::string& path, bob::io::base::array::typeinfo& info) {
  // 1. JPEG structures
  struct jpeg_decompress_struct cinfo;
  struct jpeg_error_mgr jerr;
  cinfo.err = jpeg_std_error(&jerr);
  jerr.error_exit = my_error_exit;
  jpeg_create_decompress(&cinfo);

  // 2. JPEG file opening
  boost::shared_ptr<std::FILE> in_file = make_cfile(path.c_str(), "rb");
  jpeg_stdio_src(&cinfo, in_file.get());

  // 3. Read header
  jpeg_read_header(&cinfo, TRUE);

  // 4. Set parameters for decompression if any

  // 5. Start decompression and get information
  jpeg_start_decompress(&cinfo);

  if( cinfo.output_components != 1 && cinfo.output_components != 3)
  {
    // 6. clean up
    jpeg_destroy_decompress(&cinfo);

    boost::format m("unsupported number of planes (%d) when reading file. Image depth must be 1 or 3.");
    m % cinfo.output_components;
    throw std::runtime_error(m.str());
  }

  // Set depth and number of dimensions
  info.dtype = bob::io::base::array::t_uint8;
  info.nd = (cinfo.output_components == 1? 2 : 3);
  if(info.nd == 2)
  {
    info.shape[0] = cinfo.output_height;
    info.shape[1] = cinfo.output_width;
  }
  else
  {
    info.shape[0] = 3;
    info.shape[1] = cinfo.output_height;
    info.shape[2] = cinfo.output_width;
  }
  info.update_strides();

  // 6. clean up
  jpeg_destroy_decompress(&cinfo);
}

template <typename T> static
void im_load_gray(struct jpeg_decompress_struct *cinfo, bob::io::base::array::interface& b) {
  const bob::io::base::array::typeinfo& info = b.type();

  T *element = static_cast<T*>(b.ptr());
  const int row_stride = info.shape[1];
  JSAMPROW buffer_pptr[1];
  while (cinfo->output_scanline < cinfo->image_height) {
    buffer_pptr[0] = element;
    jpeg_read_scanlines(cinfo, buffer_pptr, 1);
    element += row_stride;
  }
}

template <typename T> static
void imbuffer_to_rgb(size_t size, const T* im, T* r, T* g, T* b) {
  for (size_t k=0; k<size; ++k) {
    r[k] = im[3*k];
    g[k] = im[3*k +1];
    b[k] = im[3*k +2];
  }
}

template <typename T> static
void im_load_color(struct jpeg_decompress_struct *cinfo, bob::io::base::array::interface& b) {
  const bob::io::base::array::typeinfo& info = b.type();

  long unsigned int frame_size = info.shape[1] * info.shape[2];
  T *element_r = static_cast<T*>(b.ptr());
  T *element_g = element_r+frame_size;
  T *element_b = element_g+frame_size;

  const int row_stride = cinfo->output_width * cinfo->output_components;
  JSAMPROW buffer_pptr[1];
  boost::shared_array<JSAMPLE> buffer(new JSAMPLE[row_stride]);
  buffer_pptr[0] = buffer.get();
  while (cinfo->output_scanline < cinfo->output_height) {
    jpeg_read_scanlines(cinfo, buffer_pptr, 1);
    imbuffer_to_rgb<T>(info.shape[2], reinterpret_cast<T*>(buffer_pptr[0]), element_r, element_g, element_b);
    element_r += cinfo->output_width;
    element_g += cinfo->output_width;
    element_b += cinfo->output_width;
  }
}

static void im_load(const std::string& filename, bob::io::base::array::interface& b) {
  // 1. JPEG structures
  struct jpeg_decompress_struct cinfo;
  struct jpeg_error_mgr jerr;
  cinfo.err = jpeg_std_error(&jerr);
  jerr.error_exit = my_error_exit;
  jpeg_create_decompress(&cinfo);

  // 2. JPEG file opening
  boost::shared_ptr<std::FILE> in_file = make_cfile(filename.c_str(), "rb");
  jpeg_stdio_src(&cinfo, in_file.get());

  // 3. Read header
  jpeg_read_header(&cinfo, TRUE);

  // 4. Set parameters for decompression

  // 5. Start decompression and get information
  jpeg_start_decompress(&cinfo);

  // 6. Read content
  const bob::io::base::array::typeinfo& info = b.type();
  if(info.dtype == bob::io::base::array::t_uint8) {
    if(info.nd == 2) im_load_gray<uint8_t>(&cinfo, b);
    else if( info.nd == 3) im_load_color<uint8_t>(&cinfo, b);
    else {
      boost::format m("the image in file `%s' has a number of dimensions this jpeg codec has no support for: %s");
      m % filename % info.str();
      throw std::runtime_error(m.str());
    }
  }
  else {
    boost::format m("the image in file `%s' has a data type this jpeg codec has no support for: %s");
    m % filename % info.str();
    throw std::runtime_error(m.str());
  }

  // 7. Finish decompression
  jpeg_finish_decompress(&cinfo);

  // 8. Release JPEG decompression object
  jpeg_destroy_decompress(&cinfo);
}

/**
 * SAVING
 */
template <typename T>
static void im_save_gray(const bob::io::base::array::interface& b, struct jpeg_compress_struct *cinfo) {
  const bob::io::base::array::typeinfo& info = b.type();

  const T* element = static_cast<const T*>(b.ptr());

  // pointer to a single row  (JSAMPLE is a typedef to unsigned char or char)
  JSAMPROW row_pointer[1];
  int row_stride = info.shape[1]; // JSAMPLEs per row in image_buffer
  while(cinfo->next_scanline < cinfo->image_height) {
    row_pointer[0] = const_cast<T*>(element);
    jpeg_write_scanlines(cinfo, row_pointer, 1);
    element += row_stride;
  }
}

template <typename T> static
void rgb_to_imbuffer(size_t size, const T* r, const T* g, const T* b, T* im) {
  for (size_t k=0; k<size; ++k) {
    im[3*k]   = r[k];
    im[3*k+1] = g[k];
    im[3*k+2] = b[k];
  }
}

template <typename T>
static void im_save_color(const bob::io::base::array::interface& b, struct jpeg_compress_struct *cinfo) {
  const bob::io::base::array::typeinfo& info = b.type();

  long unsigned int frame_size = info.shape[1] * info.shape[2];

  const T *element_r = static_cast<const T*>(b.ptr());
  const T *element_g = element_r + frame_size;
  const T *element_b = element_g + frame_size;

  // pointer to a single row  (JSAMPLE is a typedef to unsigned char or char)
  boost::shared_array<JSAMPLE> row(new JSAMPLE[3*info.shape[2]]);
  JSAMPROW array_ptr[1];
  array_ptr[0] = row.get();
  int row_color_stride = info.shape[2]; // JSAMPLEs per row in image_buffer
  while(cinfo->next_scanline < cinfo->image_height) {
    rgb_to_imbuffer(row_color_stride, element_r, element_g, element_b, reinterpret_cast<T*>(array_ptr[0]));
    jpeg_write_scanlines(cinfo, array_ptr, 1);
    element_r += row_color_stride;
    element_g += row_color_stride;
    element_b += row_color_stride;
  }
}

static void im_save (const std::string& filename, const bob::io::base::array::interface& array) {
  const bob::io::base::array::typeinfo& info = array.type();

  // 1. JPEG structures
  struct jpeg_compress_struct cinfo;
  struct jpeg_error_mgr jerr;
  cinfo.err = jpeg_std_error(&jerr);
  jerr.error_exit = my_error_exit;
  jpeg_create_compress(&cinfo);

  // 2. JPEG opening
  boost::shared_ptr<std::FILE> out_file = make_cfile(filename.c_str(), "wb");
  jpeg_stdio_dest(&cinfo, out_file.get());

  // 3. Set compression parameters
  cinfo.image_height = (info.nd == 2 ? info.shape[0] : info.shape[1]);
  cinfo.image_width = (info.nd == 2 ? info.shape[1] : info.shape[2]);
  cinfo.input_components = (info.nd == 2 ? 1 : 3);
  cinfo.in_color_space = (info.nd == 2 ? JCS_GRAYSCALE : JCS_RGB); // colorspace of input image
  jpeg_set_defaults(&cinfo);
  jpeg_set_quality(&cinfo, s_jpeg_quality, TRUE);

  // 4.
  jpeg_start_compress(&cinfo, true);

  // Writes content
  if(info.dtype == bob::io::base::array::t_uint8) {

    if(info.nd == 2) im_save_gray<uint8_t>(array, &cinfo);
    else if(info.nd == 3) {
      if(info.shape[0] != 3) throw std::runtime_error("color image does not have 3 planes on 1st. dimension");
      im_save_color<uint8_t>(array, &cinfo);
    }
    else {
      boost::format m("the image array to be written at file `%s' has a number of dimensions this jpeg codec has no support for: %s");
      m % filename % info.str();
      throw std::runtime_error(m.str());
    }
  }
  else {
    boost::format m("the image array to be written at file `%s' has a data type this jpeg codec has no support for: %s");
    m % filename % info.str();
    throw std::runtime_error(m.str());
  }

  // 6.
  jpeg_finish_compress(&cinfo);

  // 7.
  jpeg_destroy_compress(&cinfo);
}


class ImageJpegFile: public bob::io::base::File {

  public: //api

    ImageJpegFile(const char* path, char mode):
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

    virtual ~ImageJpegFile() { }

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

std::string ImageJpegFile::s_codecname = "bob.image_jpeg";

boost::shared_ptr<bob::io::base::File> make_jpeg_file (const char* path, char mode) {
  return boost::make_shared<ImageJpegFile>(path, mode);
}
