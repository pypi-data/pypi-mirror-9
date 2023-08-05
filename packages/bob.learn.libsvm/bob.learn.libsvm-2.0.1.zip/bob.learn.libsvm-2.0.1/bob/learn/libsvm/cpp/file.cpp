/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 25 Mar 2014 14:01:13 CET
 *
 * @brief Implementation of the SVM machine using libsvm
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.libsvm/file.h>
#include <boost/format.hpp>
#include <boost/algorithm/string.hpp>

static bool is_colon(char i) { return i == ':'; }

bob::learn::libsvm::File::File (const std::string& filename):
  m_filename(filename),
  m_file(m_filename.c_str()),
  m_shape(0),
  m_n_samples(0)
{
  if (!m_file) {
    boost::format s("cannot open file '%s'");
    s % filename;
    throw std::runtime_error(s.str());
  }

  //scan the whole file, gets the shape and total size
  while (m_file.good()) {
    //gets the next non-empty line
    std::string line;
    while (!line.size()) {
      if (!m_file.good()) break;
      std::getline(m_file, line);
      boost::trim(line);
    }

    if (!m_file.good()) break;

    int label;
    size_t pos;
    char separator;
    double value;
    size_t n_values = std::count_if(line.begin(), line.end(), is_colon);

    std::istringstream iss(line);
    iss >> label;

    for (size_t k=0; k<n_values; ++k) {
      iss >> pos >> separator >> value;
      if (m_shape < pos) m_shape = pos;
    }

    ++m_n_samples;
  }

  //reset the file to then begin to read it properly
  m_file.clear();
  m_file.seekg(0, std::ios_base::beg);
}

bob::learn::libsvm::File::~File() {
}

void bob::learn::libsvm::File::reset() {
  m_file.close();
  m_file.open(m_filename.c_str());
}

bool bob::learn::libsvm::File::read(int& label, blitz::Array<double,1>& values) {
  if ((size_t)values.extent(0) != m_shape) {
    boost::format s("file '%s' contains %d entries per sample, but you gave me an array with only %d positions");
    s % m_filename % m_shape % values.extent(0);
    throw std::runtime_error(s.str());
  }

  //read the data.
  return read_(label, values);
}

bool bob::learn::libsvm::File::read_(int& label, blitz::Array<double,1>& values) {

  //if the file is at the end, just raise, you should have checked
  if (!m_file.good()) return false;

  //gets the next non-empty line
  std::string line;
  while (!line.size()) {
    if (!m_file.good()) return false;
    std::getline(m_file, line);
    boost::trim(line);
  }

  std::istringstream iss(line);
  iss >> label;

  int pos;
  char separator;
  double value;

  values = 0; ///zero values all over as the data is sparse on the files

  for (size_t k=0; k<m_shape; ++k) {
    iss >> pos >> separator >> value;
    values(pos-1) = value;
  }

  return true;
}
