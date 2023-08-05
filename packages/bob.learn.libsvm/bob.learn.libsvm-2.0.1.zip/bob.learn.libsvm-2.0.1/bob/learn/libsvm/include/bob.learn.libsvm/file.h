/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 25 Mar 2014 14:00:05 CET
 *
 * @brief C++ bindings to libsvm
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_LIBSVM_FILE_H
#define BOB_LEARN_LIBSVM_FILE_H

#include <blitz/array.h>
#include <fstream>

namespace bob { namespace learn { namespace libsvm {

  /**
   * Loads a given libsvm data file. The data file format, as defined on the
   * library README is like this:
   *
   * [label] [index1]:[value1] [index2]:[value2] ...
   *
   * The labels are integer values, so are the indexes, starting from "1" (and
   * not from zero as a C-programmer would expect. The values are floating
   * point.
   *
   * Zero values are suppressed - this is a sparse format.
   */
  class File {

    public: //api

      /**
       * Constructor, initializes the file readout.
       */
      File (const std::string& filename);

      /**
       * Destructor virtualization
       */
      virtual ~File();

      /**
       * Returns the size of each entry in the file, in number of floats
       */
      inline size_t shape() const { return m_shape; }

      /**
       * Returns the number of samples in the file.
       */
      inline size_t samples() const { return m_n_samples; }

      /**
       * Resets the file, going back to the beginning.
       */
      void reset();

      /**
       * Reads the next entry. Values are organized according to the indexed
       * labels at the file. Returns 'false' if the file is over or something
       * goes wrong.
       */
      bool read(int& label, blitz::Array<double,1>& values);

      /**
       * Reads the next entry on the file, but without checking. Returns
       * 'false' if the file is over or something goes wrong reading the file.
       */
      bool read_(int& label, blitz::Array<double,1>& values);

      /**
       * Returns the name of the file being read.
       */
      inline const std::string& filename() const { return m_filename; }

      /**
       * Tests if the file is still good to go.
       */
      inline bool good() const { return m_file.good(); }
      inline bool eof() const { return m_file.eof(); }
      inline bool fail() const { return m_file.fail(); }

    private: //representation

      std::string m_filename; ///< The path to the file being read
      std::ifstream m_file; ///< The file I'm reading.
      size_t m_shape; ///< Number of floats in samples
      size_t m_n_samples; ///< total number of samples at input file

  };

}}}

#endif /* BOB_LEARN_LIBSVM_FILE_H */
