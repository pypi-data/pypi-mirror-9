/**
 * @file io/cxx/ImageTiffFile.cc
 * @date Fri Oct 12 12:08:00 2012 +0200
 * @author Laurent El Shafey <laurent.el-shafey@idiap.ch>
 *
 * @brief Implements an image format reader/writer using libtiff.
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

extern "C" {
#include <tiffio.h>
}

static boost::shared_ptr<TIFF> make_cfile(const char *filename, const char *flags)
{
  TIFF* fp = TIFFOpen(filename, flags);
  if(fp == 0) {
    boost::format m("TIFFOpen(): cannot open file `%s' with flags `%s'");
    m % filename % flags;
    throw std::runtime_error(m.str());
  }
  return boost::shared_ptr<TIFF>(fp, TIFFClose);
}

/**
 * LOADING
 */
static void im_peek(const std::string& path, bob::io::base::array::typeinfo& info)
{
  // 1. TIFF file opening
  boost::shared_ptr<TIFF> in_file = make_cfile(path.c_str(), "r");

  // 2. Get file information
  uint32 w, h;
  TIFFGetField(in_file.get(), TIFFTAG_IMAGEWIDTH, &w);
  TIFFGetField(in_file.get(), TIFFTAG_IMAGELENGTH, &h);
  size_t width = (size_t)w;
  size_t height = (size_t)h;

  uint16 bps, spp;
  TIFFGetField(in_file.get(), TIFFTAG_BITSPERSAMPLE, &bps);
  TIFFGetField(in_file.get(), TIFFTAG_SAMPLESPERPIXEL, &spp);

  // 3. Set typeinfo variables
  info.dtype = (bps <= 8 ? bob::io::base::array::t_uint8 : bob::io::base::array::t_uint16);
  if(spp == 1)
    info.nd = 2;
  else if (spp == 3)
    info.nd = 3;
  else { // Unsupported color type
    boost::format m("TIFF: found unsupported object of type `%s' at file `%s': unsupported color type");
    m % info.str() % path;
    throw std::runtime_error(m.str());
  }
  if(info.nd == 2)
  {
    info.shape[0] = height;
    info.shape[1] = width;
  }
  else
  {
    info.shape[0] = 3;
    info.shape[1] = height;
    info.shape[2] = width;
  }
  info.update_strides();
}

template <typename T> static
void im_load_gray(boost::shared_ptr<TIFF> in_file, bob::io::base::array::interface& b)
{
  const bob::io::base::array::typeinfo& info = b.type();
  const size_t height = info.shape[0];
  const size_t width = info.shape[1];

  // Read in the possibly multiple strips
  tsize_t strip_size = TIFFStripSize(in_file.get());
  tstrip_t n_strips = TIFFNumberOfStrips(in_file.get());

  unsigned long buffer_size = n_strips * strip_size;
  boost::shared_array<unsigned char> buffer_(new unsigned char[buffer_size]);
  unsigned char* buffer = buffer_.get();
  if(buffer == 0) throw std::runtime_error("TIFF: error while getting the color buffer");

  tsize_t result;
  tsize_t image_offset = 0;
  for(tstrip_t strip_count=0; strip_count<n_strips; ++strip_count)
  {
    if((result = TIFFReadEncodedStrip(in_file.get(), strip_count, buffer+image_offset, strip_size)) == -1)
      throw std::runtime_error("TIFF: error in function TIFFReadEncodedStrip()");
    image_offset += result;
  }

  // Deal with photometric interpretations
  uint16 photo = PHOTOMETRIC_MINISBLACK;
  if(TIFFGetField(in_file.get(), TIFFTAG_PHOTOMETRIC, &photo) == 0 || (photo != PHOTOMETRIC_MINISBLACK && photo != PHOTOMETRIC_MINISWHITE))
    throw std::runtime_error("TIFF: error in function TIFFGetField()");

  if(photo != PHOTOMETRIC_MINISBLACK)
  {
    // Flip bits
    for(unsigned long count=0; count<buffer_size; ++count)
      buffer[count] = ~buffer[count];
  }

  // Deal with fillorder
  uint16 fillorder = FILLORDER_MSB2LSB;
  TIFFGetField(in_file.get(), TIFFTAG_FILLORDER, &fillorder);

  if(fillorder != FILLORDER_MSB2LSB) {
    // We need to swap bits -- ABCDEFGH becomes HGFEDCBA
    for(unsigned long count=0; count<buffer_size; ++count)
    {
      unsigned char tempbyte = 0;
      if(buffer[count] & 128) tempbyte += 1;
      if(buffer[count] & 64) tempbyte += 2;
      if(buffer[count] & 32) tempbyte += 4;
      if(buffer[count] & 16) tempbyte += 8;
      if(buffer[count] & 8) tempbyte += 16;
      if(buffer[count] & 4) tempbyte += 32;
      if(buffer[count] & 2) tempbyte += 64;
      if(buffer[count] & 1) tempbyte += 128;
      buffer[count] = tempbyte;
    }
  }

  // Copy to output array
  T *element = reinterpret_cast<T*>(b.ptr());
  T *b_in = reinterpret_cast<T*>(buffer);
  memcpy(element, b_in, height*width*sizeof(T));
}

template <typename T> static
void imbuffer_to_rgb(const size_t size, const T* im, T* r, T* g, T* b)
{
  for(size_t k=0; k<size; ++k)
  {
    r[k] = im[3*k];
    g[k] = im[3*k +1];
    b[k] = im[3*k +2];
  }
}

template <typename T> static
void im_load_color(boost::shared_ptr<TIFF> in_file, bob::io::base::array::interface& b)
{
  const bob::io::base::array::typeinfo& info = b.type();
  const size_t height = info.shape[1];
  const size_t width = info.shape[2];
  const size_t frame_size = height*width;
  const size_t row_stride = width;
  const size_t row_color_stride = 3*width;

  // Read in the possibly multiple strips
  tsize_t strip_size = TIFFStripSize(in_file.get());
  tstrip_t n_strips = TIFFNumberOfStrips(in_file.get());

  unsigned long buffer_size = n_strips * strip_size;
  boost::shared_array<unsigned char> buffer_(new unsigned char[buffer_size]);
  unsigned char* buffer = buffer_.get();
  if(buffer == 0) throw std::runtime_error("TIFF: error while getting the color buffer");

  tsize_t result;
  tsize_t image_offset = 0;
  for(tstrip_t strip_count=0; strip_count<n_strips; ++strip_count)
  {
    if((result = TIFFReadEncodedStrip(in_file.get(), strip_count, buffer+image_offset, strip_size)) == -1)
      throw std::runtime_error("TIFF: error in function TIFFReadEncodedStrip()");

    image_offset += result;
  }

  // Deal with photometric interpretations
  uint16 photo = PHOTOMETRIC_RGB;
  if(TIFFGetField(in_file.get(), TIFFTAG_PHOTOMETRIC, &photo) == 0 || photo != PHOTOMETRIC_RGB)
    throw std::runtime_error("TIFF: error in function TIFFGetField()");

  // Deal with fillorder
  uint16 fillorder = FILLORDER_MSB2LSB;
  TIFFGetField(in_file.get(), TIFFTAG_FILLORDER, &fillorder);

  if(fillorder != FILLORDER_MSB2LSB) {
    // We need to swap bits -- ABCDEFGH becomes HGFEDCBA
    for(unsigned long count=0; count<(unsigned long)image_offset; ++count)
    {
      unsigned char tempbyte = 0;
      if(buffer[count] & 128) tempbyte += 1;
      if(buffer[count] & 64) tempbyte += 2;
      if(buffer[count] & 32) tempbyte += 4;
      if(buffer[count] & 16) tempbyte += 8;
      if(buffer[count] & 8) tempbyte += 16;
      if(buffer[count] & 4) tempbyte += 32;
      if(buffer[count] & 2) tempbyte += 64;
      if(buffer[count] & 1) tempbyte += 128;
      buffer[count] = tempbyte;
    }
  }

  // Read the image (one row at a time)
  // This can deal with interlacing
  T *element_r = reinterpret_cast<T*>(b.ptr());
  T *element_g = element_r + frame_size;
  T *element_b = element_g + frame_size;
  unsigned char *row_pointer = buffer;
  // Loop over the rows
  for(size_t y=0; y<height; ++y)
  {
    imbuffer_to_rgb(row_stride, reinterpret_cast<T*>(row_pointer), element_r, element_g, element_b);
    element_r += row_stride;
    element_g += row_stride;
    element_b += row_stride;
    row_pointer += row_color_stride * sizeof(T);
  }
}

static void im_load(const std::string& filename, bob::io::base::array::interface& b)
{
  // 1. TIFF file opening
  boost::shared_ptr<TIFF> in_file = make_cfile(filename.c_str(), "r");

  // 2. Read content
  const bob::io::base::array::typeinfo& info = b.type();
  if(info.dtype == bob::io::base::array::t_uint8) {
    if(info.nd == 2) im_load_gray<uint8_t>(in_file, b);
    else if( info.nd == 3) im_load_color<uint8_t>(in_file, b);
    else {
      boost::format m("TIFF: cannot read object of type `%s' from file `%s'");
      m % info.str() % filename;
      throw std::runtime_error(m.str());
    }
  }
  else if(info.dtype == bob::io::base::array::t_uint16) {
    if(info.nd == 2) im_load_gray<uint16_t>(in_file, b);
    else if( info.nd == 3) im_load_color<uint16_t>(in_file, b);
    else {
      boost::format m("TIFF: cannot read object of type `%s' from file `%s'");
      m % info.str() % filename;
      throw std::runtime_error(m.str());
    }
  }
  else {
    boost::format m("TIFF: cannot read object of type `%s' from file `%s'");
    m % info.str() % filename;
    throw std::runtime_error(m.str());
  }
}


/**
 * SAVING
 */
template <typename T>
static void im_save_gray(const bob::io::base::array::interface& b, boost::shared_ptr<TIFF> out_file)
{
  const bob::io::base::array::typeinfo& info = b.type();
  const size_t height = info.shape[0];
  const size_t width = info.shape[1];

  unsigned char* row_pointer = const_cast<unsigned char*>(reinterpret_cast<const unsigned char*>(b.ptr()));
  const size_t data_size = height * width * sizeof(T);

  // Write the information to the file
  TIFFWriteEncodedStrip(out_file.get(), 0, row_pointer, data_size);
}

template <typename T> static
void rgb_to_imbuffer(const size_t size, const T* r, const T* g, const T* b, T* im)
{
  for (size_t k=0; k<size; ++k)
  {
    im[3*k]   = r[k];
    im[3*k+1] = g[k];
    im[3*k+2] = b[k];
  }
}

template <typename T>
static void im_save_color(const bob::io::base::array::interface& b, boost::shared_ptr<TIFF> out_file)
{
  const bob::io::base::array::typeinfo& info = b.type();
  const size_t height = info.shape[1];
  const size_t width = info.shape[2];
  const size_t frame_size = height * width;

  // Allocate array for a row as an RGB-like array
  boost::shared_array<T> row(new T[3*width*height]);
  unsigned char* row_pointer = reinterpret_cast<unsigned char*>(row.get());

  // pointer to a single row (tiff_bytep is a typedef to unsigned char or char)
  const T *element_r = static_cast<const T*>(b.ptr());
  const T *element_g = element_r + frame_size;
  const T *element_b = element_g + frame_size;
  rgb_to_imbuffer(frame_size, element_r, element_g, element_b, row.get());

  // Write the information to the file
  const size_t data_size = 3 * height * width * sizeof(T);
  TIFFWriteEncodedStrip(out_file.get(), 0, row_pointer, data_size);
}

static void im_save(const std::string& filename, const bob::io::base::array::interface& array)
{
  // 1. Open the file
  boost::shared_ptr<TIFF> out_file = make_cfile(filename.c_str(), "w");

  // 2. Set the image information here:
  const bob::io::base::array::typeinfo& info = array.type();
  const int height = (info.nd == 2 ? info.shape[0] : info.shape[1]);
  const int width = (info.nd == 2 ? info.shape[1] : info.shape[2]);
  TIFFSetField(out_file.get(), TIFFTAG_IMAGELENGTH, height);
  TIFFSetField(out_file.get(), TIFFTAG_IMAGEWIDTH, width);
  TIFFSetField(out_file.get(), TIFFTAG_BITSPERSAMPLE, (info.dtype == bob::io::base::array::t_uint8 ? 8 : 16));
  TIFFSetField(out_file.get(), TIFFTAG_SAMPLESPERPIXEL, (info.nd == 2 ? 1 : 3));

  TIFFSetField(out_file.get(), TIFFTAG_COMPRESSION, COMPRESSION_NONE);
  TIFFSetField(out_file.get(), TIFFTAG_FILLORDER, FILLORDER_MSB2LSB);
  if(info.nd == 3)
    TIFFSetField(out_file.get(), TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);
  TIFFSetField(out_file.get(), TIFFTAG_PHOTOMETRIC, (info.nd == 2 ? PHOTOMETRIC_MINISBLACK : PHOTOMETRIC_RGB));

  // 3. Writes content
  if(info.dtype == bob::io::base::array::t_uint8) {
    if(info.nd == 2) im_save_gray<uint8_t>(array, out_file);
    else if(info.nd == 3) {
      if(info.shape[0] != 3)
        throw std::runtime_error("color image does not have 3 planes on 1st. dimension");
      im_save_color<uint8_t>(array, out_file);
    }
    else {
      boost::format m("TIFF: cannot write object of type `%s' to file `%s'");
      m % info.str() % filename;
      throw std::runtime_error(m.str());
    }
  }
  else if(info.dtype == bob::io::base::array::t_uint16) {
    if(info.nd == 2) im_save_gray<uint16_t>(array, out_file);
    else if(info.nd == 3) {
      if(info.shape[0] != 3)
        throw std::runtime_error("color image does not have 3 planes on 1st. dimension");
      im_save_color<uint16_t>(array, out_file);
    }
    else {
      boost::format m("TIFF: cannot write object of type `%s' to file `%s'");
      m % info.str() % filename;
      throw std::runtime_error(m.str());
    }
  }
  else {
    boost::format m("TIFF: cannot write object of type `%s' to file `%s'");
    m % info.str() % filename;
    throw std::runtime_error(m.str());
  }
}

class ImageTiffFile: public bob::io::base::File {

  public: //api

    ImageTiffFile(const char* path, char mode):
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

    virtual ~ImageTiffFile() { }

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

std::string ImageTiffFile::s_codecname = "bob.image_tiff";

boost::shared_ptr<bob::io::base::File> make_tiff_file (const char* path, char mode) {
  return boost::make_shared<ImageTiffFile>(path, mode);
}
