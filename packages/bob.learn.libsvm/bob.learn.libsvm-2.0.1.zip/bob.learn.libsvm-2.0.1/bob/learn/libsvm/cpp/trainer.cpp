/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Sun  4 Mar 10:02:45 2012 CET
 *
 * @brief Implementation of the SVM training methods
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.libsvm/trainer.h>
#include <boost/format.hpp>
#include <boost/make_shared.hpp>
#include <bob.core/logging.h>

#ifdef BOB_DEBUG
//remove newline
#include <boost/algorithm/string/trim.hpp>
static std::string strip(const char* s) {
  std::string t(s);
  boost::algorithm::trim(t);
  return t;
}
#endif

static void debug_libsvm(const char* s) {
  TDEBUG1("[libsvm-" << LIBSVM_VERSION << "] " << strip(s));
}

bob::learn::libsvm::Trainer::Trainer(
    bob::learn::libsvm::machine_t machine_type,
    bob::learn::libsvm::kernel_t kernel_type,
    double cache_size,
    double eps,
    bool shrinking,
    bool probability
    )
{
  m_param.svm_type = machine_type;
  m_param.kernel_type = kernel_type;
  m_param.degree = 3;
  m_param.gamma = 0.;
  m_param.coef0 = 0.;
  m_param.cache_size = cache_size;
  m_param.eps = eps;
  m_param.C = 1;
  m_param.nu = 0.5;
  m_param.p = 0.1;
  m_param.shrinking = shrinking;
  m_param.probability = probability;

  //extracted from the data
  m_param.nr_weight = 0;
  m_param.weight_label = 0;
  m_param.weight = 0;
}

bob::learn::libsvm::Trainer::~Trainer() { }

/**
 * Erases an SVM problem:
 *
 * struct svm_problem {
 *   int l; //number of entries
 *   double* y; //labels
 *   svm_node** x; //each set terminated with a -1 index entry
 * };
 *
 * At svm-train the nodes for each entry are allocated globally, what is
 * probably more efficient from the allocation perspective. It still requires
 * libsvm to scan the data twice to understand how many nodes need to be
 * allocated globally.
 */
static void delete_problem(svm_problem* p) {
  delete[] p->y; //all labels
  delete[] p->x[0]; //all entries
  delete[] p->x; //entry pointers
  delete p;
}

/**
 * Allocates an svm_problem matrix
 */
static svm_problem* new_problem(size_t entries) {
  svm_problem* retval = new svm_problem;
  retval->l = (int)entries;
  retval->y = new double[entries];
  typedef svm_node* svm_node_ptr;
  retval->x = new svm_node_ptr[entries];
  for (size_t k=0; k<entries; ++k) retval->x[k] = 0;
  return retval;
}

/**
 * Converts the input arrayset data into an svm_problem matrix, used by libsvm
 * training routines. Updates "gamma" at the svm_parameter's.
 */
static boost::shared_ptr<svm_problem> data2problem
(const std::vector<blitz::Array<double, 2> >& data,
 const blitz::Array<double,1>& sub, const blitz::Array<double,1>& div,
 svm_parameter& param) {

  //counts the number of samples required
  size_t entries = 0;
  for (size_t k=0; k<data.size(); ++k)
    entries += data[k].extent(blitz::firstDim);

  //allocates the container that will represent the problem; at this stage, we
  //allocate entries for each vector, but not the space in which feature will
  //be put at. This will come next.
  boost::shared_ptr<svm_problem> problem(new_problem(entries),
      std::ptr_fun(delete_problem));

  //choose labels.
  if ((data.size() <= 1) | (data.size() > 16)) {
    boost::format m("Only supports SVMs for binary or multi-class classification problems (up to 16 classes). You passed me a list of %d arraysets.");
    m % data.size();
    throw std::runtime_error(m.str());
  }

  std::vector<double> labels;
  labels.reserve(data.size());
  if (data.size() == 2) {
    //keep libsvm ordering
    labels.push_back(+1.);
    labels.push_back(-1.);
  }
  else { //data.size() == 3, 4, ..., 16
    for (size_t k=0; k<data.size(); ++k) labels.push_back(k+1);
  }

  //just count how many nodes we need; unfortunately we have no other choice
  //than doing a 2-pass instantiation here as libsvm has a very weird way to
  //optimize data access in which it requires all nodes to be allocated in a
  //single shot.
  size_t nodes = 0; //total number of nodes to be allocated
  blitz::Range all=blitz::Range::all();
  int n_features = data[0].extent(blitz::secondDim);
  blitz::Array<double,1> d(n_features); //for temporary feature manipulation

  for (size_t k=0; k<data.size(); ++k) {
    for (int i=0; i<data[k].extent(blitz::firstDim); ++i) {
      d = (data[k](i,all)-sub)/div; //eval and copy in 1 instruction
      for (int p=0; p<d.extent(blitz::firstDim); ++p) {
        if (d(p)) {
          ++nodes;
        }
      }
      ++nodes; //one extra for the termination node "index == -1"
    }
  }

  //allocates all the nodes, set first entry, a la libsvm
  svm_node* all_nodes = new svm_node[nodes];

  //iterates over each class data and fills the svm_node's
  int max_index = 0; //data width
  size_t sample = 0; //sample counter
  size_t node = 0; //node counter

  for (size_t k=0; k<data.size(); ++k) {
    for (int i=0; i<data[k].extent(blitz::firstDim); ++i) {
      problem->x[sample] = &all_nodes[node]; //setup current sample base pointer
      d = (data[k](i,all)-sub)/div; //eval and copy in 1 instruction
      for (blitz::sizeType p=0; p<d.size(); ++p) {
        if (d(p)) {
          int index = p+1; //starts indexing at 1
          all_nodes[node].index = index;
          all_nodes[node].value = d(p);
          if ( index > max_index ) max_index = index;
          ++node; //index within the current sample
        }
      }
      //marks end of sequence
      all_nodes[node].index = -1;
      all_nodes[node].value = 0;
      problem->y[sample] = labels[k];
      ++node;
      ++sample;
    }
  }

  //extracted from svm-train.c
  if (param.gamma == 0. && max_index > 0) {
    param.gamma = 1.0/max_index;
  }

  //do not support pre-computed kernels...
  if (param.kernel_type == PRECOMPUTED) {
    throw std::runtime_error("We currently dod not support PRECOMPUTED kernels in these bindings to libsvm");
  }

  return problem;
}

/**
 * A wrapper, to standardize the freeing of the svm_model
 */
static void svm_model_free(svm_model*& m) {
#if LIBSVM_VERSION >= 300
  svm_free_and_destroy_model(&m);
#else
  svm_destroy_model(m);
#endif
}

bob::learn::libsvm::Machine* bob::learn::libsvm::Trainer::train
(const std::vector<blitz::Array<double, 2> >& data,
 const blitz::Array<double,1>& input_subtraction,
 const blitz::Array<double,1>& input_division) const {

  //sanity check of input arraysets
  int n_features = data[0].extent(blitz::secondDim);

  for (size_t cl=0; cl<data.size(); ++cl) {
    if (data[cl].extent(blitz::secondDim) != n_features) {
      boost::format m("number of features (columns) of array for class %u (%d) does not match that of array for class 0 (%d)");
      m % cl % data[cl].extent(blitz::secondDim) % n_features;
      throw std::runtime_error(m.str());
    }
  }

  //converts the input arraysets into something libsvm can digest
  double save_gamma = m_param.gamma; ///< the next method may update it!
  boost::shared_ptr<svm_problem> problem =
    data2problem(data, input_subtraction, input_division,
        const_cast<svm_parameter&>(m_param) ///< temporary cast
        );

  //checks parametrization to make sure all is alright.
  const char* error_msg = svm_check_parameter(problem.get(), &m_param);

  if (error_msg) {
    const_cast<double&>(m_param.gamma) = save_gamma;
    boost::format m("libsvm-%d reports: %s");
    m % libsvm_version % error_msg;
    std::runtime_error(m.str());
  }

  //do the training, returns the new machine
#if LIBSVM_VERSION >= 291
  svm_set_print_string_function(debug_libsvm);
#else
  boost::format m("libsvm-%d does not support debugging stream setting");
  m % libsvm_version;
  debug_libsvm(m.str().c_str());
#endif
  boost::shared_ptr<svm_model> model(svm_train(problem.get(), &m_param),
      std::ptr_fun(svm_model_free));

  const_cast<double&>(m_param.gamma) = save_gamma;

  //save newly created machine to file, reload from there to get rid of memory
  //dependencies due to the poorly implemented memory model in libsvm
  boost::shared_ptr<svm_model> new_model =
    bob::learn::libsvm::svm_unpickle(bob::learn::libsvm::svm_pickle(model));

  auto retval = new bob::learn::libsvm::Machine(new_model);

  //sets up the scaling parameters given as input
  retval->setInputSubtraction(input_subtraction);
  retval->setInputDivision(input_division);

  return retval;
}

bob::learn::libsvm::Machine* bob::learn::libsvm::Trainer::train
(const std::vector<blitz::Array<double,2> >& data) const {
  int n_features = data[0].extent(blitz::secondDim);
  blitz::Array<double,1> sub(n_features);
  sub = 0.;
  blitz::Array<double,1> div(n_features);
  div = 1.;
  return train(data, sub, div);
}
