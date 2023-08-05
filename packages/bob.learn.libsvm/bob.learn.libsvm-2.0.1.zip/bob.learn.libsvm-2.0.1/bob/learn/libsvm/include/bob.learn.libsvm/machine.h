/**
 * @file bob/machine/SVM.h
 * @date Sat Dec 17 14:41:56 2011 +0100
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief C++ bindings to libsvm
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_LIBSVM_MACHINE_H
#define BOB_LEARN_LIBSVM_MACHINE_H

#include <boost/shared_ptr.hpp>
#include <boost/shared_array.hpp>
#include <blitz/array.h>
#include <fstream>
#include <svm.h>
#include <bob.io.base/HDF5File.h>

// @cond SKIPDOXYGEN
// We need to declare the svm_model type for libsvm < 3.0.0. The next bit of
// code was cut and pasted from version 2.9.1 of libsvm, file svm.cpp.
#if LIBSVM_VERSION < 300
struct svm_model {
  struct svm_parameter param; /* parameter */
  int nr_class;         /* number of classes, = 2 in regression/one class svm */
  int l;                /* total #SV */
  struct svm_node **SV; /* SVs (SV[l]) */
  double **sv_coef;     /* coefficients for SVs in decision functions (sv_coef[k-1][l]) */
  double *rho;          /* constants in decision functions (rho[k*(k-1)/2]) */
  double *probA;        /* pariwise probability information */
  double *probB;

  /* for classification only */

  int *label;  /* label of each class (label[k]) */
  int *nSV;    /* number of SVs for each class (nSV[k]) */
               /* nSV[0] + nSV[1] + ... + nSV[k-1] = l */
  /* XXX */
  int free_sv; /* 1 if svm_model is created by svm_load_model*/
               /* 0 if svm_model is created by svm_train */
};
#endif
// @endcond

namespace bob { namespace learn { namespace libsvm {

  enum machine_t {
    C_SVC,
    NU_SVC,
    ONE_CLASS,
    EPSILON_SVR,
    NU_SVR
  }; /* the machine type */

  enum kernel_t {
    LINEAR,
    POLY,
    RBF,
    SIGMOID,
    PRECOMPUTED
  }; /* kernel type used on the machine */

    /**
     * @brief Chooses the correct temporary directory to use, like this:
     *
     * - The environment variable TMPDIR, if it is defined. For security reasons
     *   this only happens if the program is not SUID or SGID enabled.
     * - The directory /tmp.
     */
    std::string _tmpdir();

    /**
     * @brief Returns the full path of a temporary file in tmpdir().
     *
     * @param extension The desired extension for the file
     */
    std::string _tmpfile(const std::string& extension=".hdf5");


  /**
   * Here is the problem: libsvm does not provide a simple way to extract the
   * information from the SVM structure. There are lots of cases and allocation
   * and re-allocation is not exactly trivial. To overcome these problems and
   * still be able to save data in HDF5 format, we let libsvm pickle the data
   * into a text file and then re-read it in binary. We save the outcome of
   * this readout in a binary blob inside the HDF5 file.
   */
  blitz::Array<uint8_t,1> svm_pickle(const boost::shared_ptr<svm_model> model);

  /**
   * Reverts the pickling process, returns the model
   */
  boost::shared_ptr<svm_model> svm_unpickle(const blitz::Array<uint8_t,1>& buffer);

  /**
   * Interface to svm_model, from libsvm. Incorporates prediction.
   */
  class Machine {

    public: //api

      /**
       * Builds a new Support Vector Machine from a libsvm model file
       *
       * When you load using the libsvm model loader, note that the scaling
       * parameters will be set to defaults (subtraction of 0.0 and division by
       * 1.0). If you need scaling to be applied, set it individually using the
       * appropriate methods bellow.
       */
      Machine(const std::string& model_file);

      /**
       * Builds a new Support Vector Machine from an HDF5 file containing the
       * configuration for this machine. Scaling parameters are also loaded
       * from the file. Using this constructor assures a 100% state recovery
       * from previous sessions.
       */
      Machine(bob::io::base::HDF5File& config);

      /**
       * Builds a new SVM model from a trained model. Scaling parameters will
       * be neutral (subtraction := 0.0, division := 1.0).
       *
       * @note: This method is typically only used by the respective
       * bob::trainer::MachineTrainer as it requires the creation of the
       * object "svm_model". You can still make use of it if you decide to
       * implement the model instantiation yourself.
       */
      Machine(boost::shared_ptr<svm_model> model);

      /**
       * Virtual d'tor
       */
      virtual ~Machine();

      /**
       * Tells the input size this machine expects
       */
      size_t inputSize() const;

      /**
       * The number of outputs depends on the number of classes the machine has
       * to deal with. If the problem is a regression problem, the number of
       * outputs is fixed to 1. The same happens in a binary classification
       * problem. Otherwise, the output size is the same as the number of
       * classes being discriminated.
       */
      size_t outputSize() const;

      /**
       * Tells the number of classes the problem has.
       */
      size_t numberOfClasses() const;

      /**
       * Returns the class label (as stored inside the svm_model object) for a
       * given class 'i'.
       */
      int classLabel(size_t i) const;

      /**
       * SVM type
       */
      machine_t machineType() const;

      /**
       * Kernel type
       */
      kernel_t kernelType() const;

      /**
       * Polinomial degree, if kernel is POLY
       */
      int polynomialDegree() const;

      /**
       * Gamma factor, for POLY, RBF or SIGMOID kernels
       */
      double gamma() const;

      /**
       * Coefficient 0 for POLY and SIGMOID kernels
       */
      double coefficient0() const;

      /**
       * Tells if this model supports probability output.
       */
      bool supportsProbability() const;

      /**
       * Returns the input subtraction factor
       */
      inline const blitz::Array<double, 1>& getInputSubtraction() const
      { return m_input_sub; }

      /**
       * Sets the current input subtraction factor. We will check that the
       * number of inputs (first dimension of weights) matches the number of
       * values currently set and will raise an exception if that is not the
       * case.
       */
      void setInputSubtraction(const blitz::Array<double,1>& v);

      /**
       * Sets all input subtraction values to a specific value.
       */
      inline void setInputSubtraction(double v) { m_input_sub = v; }

      /**
       * Returns the input division factor
       */
      inline const blitz::Array<double, 1>& getInputDivision() const
      { return m_input_div; }

      /**
       * Sets the current input division factor. We will check that the number
       * of inputs (first dimension of weights) matches the number of values
       * currently set and will raise an exception if that is not the case.
       */
      void setInputDivision(const blitz::Array<double,1>& v);

      /**
       * Sets all input division values to a specific value.
       */
      inline void setInputDivision(double v) { m_input_div = v; }

      /**
       * Predict, output classes only. Note that the number of labels in the
       * output "labels" array should be the same as the number of input.
       */
      int predictClass(const blitz::Array<double,1>& input) const;

      /**
       * Predict, output classes only. Note that the number of labels in the
       * output "labels" array should be the same as the number of input.
       *
       * This does the same as predictClass(), but does not check the input.
       */
      int predictClass_(const blitz::Array<double,1>& input) const;

      /**
       * Predicts class and scores output for each class on this SVM,
       *
       * Note: The output array must be lying on contiguous memory. This is
       * also checked.
       */
      int predictClassAndScores
        (const blitz::Array<double,1>& input,
         blitz::Array<double,1>& scores) const;

      /**
       * Predicts output class and scores. Same as above, but does not check
       */
      int predictClassAndScores_
        (const blitz::Array<double,1>& input,
         blitz::Array<double,1>& scores) const;

      /**
       * Predict, output class and probabilities for each class on this SVM,
       * but only if the model supports it. Otherwise, throws a run-time
       * exception.
       *
       * Note: The output array must be lying on contiguous memory. This is
       * also checked.
       */
      int predictClassAndProbabilities
        (const blitz::Array<double,1>& input,
         blitz::Array<double,1>& probabilities) const;

      /**
       * Predict, output class and probability, but only if the model supports
       * it. Same as above, but does not check
       */
      int predictClassAndProbabilities_
        (const blitz::Array<double,1>& input,
         blitz::Array<double,1>& probabilities) const;

      /**
       * Saves the current model state to a file. With this variant, the model
       * is saved on simpler libsvm model file that does not include the
       * scaling parameters set on this machine.
       */
      void save(const std::string& filename) const;

      /**
       * Saves the whole machine into a configuration file. This allows for a
       * single instruction parameter loading, which includes both the model
       * and the scaling parameters.
       */
      void save(bob::io::base::HDF5File& config) const;

    private: //not implemented

      Machine(const Machine& other);

      Machine& operator= (const Machine& other);

    private: //methods

      /**
       * Resets the internal state of this machine. Normally called
       */
      void reset();

    private: //representation

      boost::shared_ptr<svm_model> m_model; ///< libsvm model pointer
      mutable boost::shared_array<svm_node> m_input_cache; ///< cache
      size_t m_input_size; ///< vector size expected as input for the SVM's
      blitz::Array<double,1> m_input_sub; ///< scaling: subtraction
      blitz::Array<double,1> m_input_div; ///< scaling: division

  };

}}}

#endif /* BOB_LEARN_LIBSVM_MACHINE_H */
