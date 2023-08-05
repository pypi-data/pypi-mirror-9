/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Sat Dec 17 14:41:56 2011 +0100
 *
 * @brief C++ bindings to libsvm (training bit)
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_LIBSVM_TRAINER_H
#define BOB_LEARN_LIBSVM_TRAINER_H

#include <vector>
#include <bob.learn.libsvm/machine.h>

namespace bob { namespace learn { namespace libsvm {

  /**
   * This class emulates the behavior of the command line utility called
   * svm-train, from libsvm. These bindings do not support:
   *
   * * Precomputed Kernels
   * * Regression Problems
   * * Different weights for every label (-wi option in svm-train)
   *
   * Fell free to implement those and remove these remarks.
   */
  class Trainer {

    public: //api

      /**
       * Builds a new trainer setting the default parameters as defined in the
       * command line application svm-train.
       */
      Trainer(
          machine_t machine_type=C_SVC,
          kernel_t kernel_type=RBF,
          double cache_size=100, //in MB
          double eps=1.e-3, //stopping criteria epsilon
          bool shrinking=true, //use the shrinking heuristics
          bool probability=false //do probability estimates
          );
      /** TODO: Support for weight cost in multi-class classification? **/

      /**
       * Destructor virtualisation
       */
      virtual ~Trainer();

      /**
       * Trains a new machine for multi-class classification. If the number of
       * classes in data is 2, then the assigned labels will be -1 and +1. If
       * the number of classes is greater than 2, labels are picked starting
       * from 1 (i.e., 1, 2, 3, 4, etc.). If what you want is regression, the
       * size of the input data array should be 1.
       *
       * Returns a new object you must deallocate yourself.
       */
      bob::learn::libsvm::Machine* train
        (const std::vector<blitz::Array<double,2> >& data) const;

      /**
       * This version accepts scaling parameters that will be applied
       * column-wise to the input data.
       */
      bob::learn::libsvm::Machine* train
        (const std::vector<blitz::Array<double,2> >& data,
         const blitz::Array<double,1>& input_subtract,
         const blitz::Array<double,1>& input_division) const;

      /**
       * Getters and setters for all parameters
       */
      machine_t getMachineType() const { return (machine_t)m_param.svm_type; }
      void setMachineType(machine_t v) { m_param.svm_type = v; }

      kernel_t getKernelType() const { return (kernel_t)m_param.kernel_type; }
      void setKernelType(kernel_t v) { m_param.kernel_type = v; }

      int getDegree() const { return m_param.degree; }
      void setDegree(int v) { m_param.degree = v; }

      double getGamma() const { return m_param.gamma; }
      void setGamma(double v) { m_param.gamma = v; }

      double getCoef0() const { return m_param.coef0; }
      void setCoef0(double v) { m_param.coef0 = v; }

      double getCacheSizeInMb() const { return m_param.cache_size; }
      void setCacheSizeInMb(double v) { m_param.cache_size = v; }

      double getStopEpsilon() const { return m_param.eps; }
      void setStopEpsilon(double v) { m_param.eps = v; }

      double getCost() const { return m_param.C; }
      void setCost(double v) { m_param.C = v; }

      double getNu() const { return m_param.nu; }
      void setNu(double v) { m_param.nu = v; }

      double getLossEpsilonSVR() const { return m_param.p; }
      void setLossEpsilonSVR(double v) { m_param.p = v; }

      bool getUseShrinking() const { return m_param.shrinking; }
      void setUseShrinking(bool v) { m_param.shrinking = v; }

      bool getProbabilityEstimates() const
      { return m_param.probability; }
      void setProbabilityEstimates(bool v)
      { m_param.probability = v; }

    private: //representation

      svm_parameter m_param; ///< training parametrization for libsvm

  };

}}}

#endif /* BOB_LEARN_LIBSVM_TRAINER_H */
