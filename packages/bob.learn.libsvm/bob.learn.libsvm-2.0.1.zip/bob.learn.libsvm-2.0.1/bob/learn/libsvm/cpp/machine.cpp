/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Sat Dec 17 14:41:56 2011 +0100
 *
 * @brief Implementation of the SVM machine using libsvm
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.libsvm/machine.h>

#include <sys/stat.h>
#include <boost/format.hpp>
#include <boost/filesystem.hpp>
#include <bob.core/check.h>
#include <bob.core/logging.h>


std::string bob::learn::libsvm::_tmpdir() {
  const char* value = getenv("TMPDIR");
  if (value)
    return value;
  else
    return "/tmp";
}

std::string bob::learn::libsvm::_tmpfile(const std::string& extension) {
  boost::filesystem::path tpl = bob::learn::libsvm::_tmpdir();
  tpl /= std::string("bob_tmpfile_XXXXXX");
  boost::shared_array<char> char_tpl(new char[tpl.string().size()+1]);
  strcpy(char_tpl.get(), tpl.string().c_str());
#ifdef _WIN32
  mktemp(char_tpl.get());
#else
  int fd = mkstemp(char_tpl.get());
  close(fd);
  boost::filesystem::remove(char_tpl.get());
#endif
  std::string res = char_tpl.get();
  res += extension;
  return res;
}


/**
 * A wrapper, to standardize this function.
 */
static void svm_model_free(svm_model*& m) {
#if LIBSVM_VERSION >= 300
  svm_free_and_destroy_model(&m);
#else
  svm_destroy_model(m);
#endif
}

blitz::Array<uint8_t,1> bob::learn::libsvm::svm_pickle
(const boost::shared_ptr<svm_model> model)
{
  std::string tmp_filename = bob::learn::libsvm::_tmpfile(".svm");

  //save it to a temporary file
  if (svm_save_model(tmp_filename.c_str(), model.get())) {
    boost::format s("cannot save SVM to file `%s' while copying model");
    s % tmp_filename;
    throw std::runtime_error(s.str());
  }

  //gets total size of file
  struct stat filestatus;
  stat(tmp_filename.c_str(), &filestatus);

  //reload the data from the file in binary format
  std::ifstream binfile(tmp_filename.c_str(), std::ios::binary);
  blitz::Array<uint8_t,1> buffer(filestatus.st_size);
  binfile.read(reinterpret_cast<char*>(buffer.data()), filestatus.st_size);

  //unlink the temporary file
  boost::filesystem::remove(tmp_filename);

  //finally, return the pickled data
  return buffer;
}

static boost::shared_ptr<svm_model> make_model(const char* filename) {
  boost::shared_ptr<svm_model> retval(svm_load_model(filename),
      std::ptr_fun(svm_model_free));
#if LIBSVM_VERSION > 315
  if (retval) retval->sv_indices = 0; ///< force initialization: see ticket #109
#endif
  return retval;
}

/**
 * Reverts the pickling process, returns the model
 */
boost::shared_ptr<svm_model> bob::learn::libsvm::svm_unpickle
(const blitz::Array<uint8_t,1>& buffer) {

  std::string tmp_filename = bob::learn::libsvm::_tmpfile(".svm");

  std::ofstream binfile(tmp_filename.c_str(), std::ios::binary);
  binfile.write(reinterpret_cast<const char*>(buffer.data()), buffer.size());
  binfile.close();

  //reload the file using the appropriate libsvm loading method
  boost::shared_ptr<svm_model> retval = make_model(tmp_filename.c_str());

  if (!retval) {
    boost::format s("cannot open model file '%s'");
    s % tmp_filename;
    throw std::runtime_error(s.str());
  }

  //unlinks the temporary file
  boost::filesystem::remove(tmp_filename);

  //finally, return the pickled data
  return retval;
}

void bob::learn::libsvm::Machine::reset() {
  //gets the expected size for the input from the SVM
  m_input_size = 0;
  for (int k=0; k<m_model->l; ++k) {
    svm_node* end = m_model->SV[k];
    while (end->index != -1) {
      if (end->index > (int)m_input_size) m_input_size = end->index;
      ++end;
    }
  }

  //create and reset cache
  m_input_cache.reset(new svm_node[1 + m_input_size]);

  m_input_sub.resize(inputSize());
  m_input_sub = 0.0;
  m_input_div.resize(inputSize());
  m_input_div = 1.0;
}

bob::learn::libsvm::Machine::Machine(const std::string& model_file):
  m_model(make_model(model_file.c_str()))
{
  if (!m_model) {
    boost::format s("cannot open model file '%s'");
    s % model_file;
    throw std::runtime_error(s.str());
  }
  reset();
}

bob::learn::libsvm::Machine::Machine(bob::io::base::HDF5File& config):
  m_model()
{
  uint64_t version = 0;
  config.getAttribute(".", "version", version);
  if ( (LIBSVM_VERSION/100) > (version/100) ) {
    //if the major version changes... be aware!
    boost::format m("SVM being loaded from `%s:%s' (created with libsvm-%d) with libsvm-%d. You may want to read the libsvm FAQ at http://www.csie.ntu.edu.tw/~cjlin/libsvm/log to check if there were format changes between these versions. If not, you can safely ignore this warning and even tell us to remove it via our bug tracker: https://github.com/idiap/bob/issues");
    m % config.filename() % config.cwd() % version % LIBSVM_VERSION;
    bob::core::warn << m.str() << std::endl;
  }
  m_model = bob::learn::libsvm::svm_unpickle(config.readArray<uint8_t,1>("svm_model"));
  reset(); ///< note: has to be done before reading scaling parameters
  config.readArray("input_subtract", m_input_sub);
  config.readArray("input_divide", m_input_div);
}

bob::learn::libsvm::Machine::Machine(boost::shared_ptr<svm_model> model)
  : m_model(model)
{
  if (!m_model) {
    throw std::runtime_error("null SVM model cannot be processed");
  }
  reset();
}

bob::learn::libsvm::Machine::~Machine() { }

bool bob::learn::libsvm::Machine::supportsProbability() const {
  return svm_check_probability_model(m_model.get());
}

size_t bob::learn::libsvm::Machine::inputSize() const {
  return m_input_size;
}

size_t bob::learn::libsvm::Machine::outputSize() const {
  size_t retval = svm_get_nr_class(m_model.get());
  return (retval == 2)? 1 : retval;
}

size_t bob::learn::libsvm::Machine::numberOfClasses() const {
  return svm_get_nr_class(m_model.get());
}

int bob::learn::libsvm::Machine::classLabel(size_t i) const {

  if (i >= (size_t)svm_get_nr_class(m_model.get())) {
    boost::format s("request for label of class %d in SVM with %d classes is not legal");
    s % (int)i % svm_get_nr_class(m_model.get());
    throw std::runtime_error(s.str());
  }
  return m_model->label[i];

}

bob::learn::libsvm::machine_t bob::learn::libsvm::Machine::machineType() const {
  return (machine_t)svm_get_svm_type(m_model.get());
}

bob::learn::libsvm::kernel_t bob::learn::libsvm::Machine::kernelType() const {
  return (kernel_t)m_model->param.kernel_type;
}

int bob::learn::libsvm::Machine::polynomialDegree() const {
  return m_model->param.degree;
}

double bob::learn::libsvm::Machine::gamma() const {
  return m_model->param.gamma;
}

double bob::learn::libsvm::Machine::coefficient0() const {
  return m_model->param.coef0;
}

void bob::learn::libsvm::Machine::setInputSubtraction(const blitz::Array<double,1>& v) {
  if (inputSize() > (size_t)v.extent(0)) {
    boost::format m("mismatch on the input subtraction dimension: expected a vector with **at least** %d positions, but you input %d");
    m % inputSize() % v.extent(0);
    throw std::runtime_error(m.str());
  }
  m_input_sub.reference(bob::core::array::ccopy(v));
}

void bob::learn::libsvm::Machine::setInputDivision(const blitz::Array<double,1>& v) {
  if (inputSize() > (size_t)v.extent(0)) {
    boost::format m("mismatch on the input division dimension: expected a vector with **at least** %d positions, but you input %d");
    m % inputSize() % v.extent(0);
    throw std::runtime_error(m.str());
  }
  m_input_div.reference(bob::core::array::ccopy(v));
}

/**
 * Copies the user input to a locally pre-allocated cache. Apply normalization
 * at the same occasion.
 */
static inline void copy(const blitz::Array<double,1>& input,
    size_t cache_size, boost::shared_array<svm_node>& cache,
    const blitz::Array<double,1>& sub, const blitz::Array<double,1>& div) {

  size_t cur = 0; ///< currently used index

  for (size_t k=0; k<cache_size; ++k) {
    double tmp = (input(k) - sub(k))/div(k);
    if (!tmp) continue;
    cache[cur].index = k+1;
    cache[cur].value = tmp;
    ++cur;
  }

  cache[cur].index = -1; //libsvm detects end of input if index==-1
}

int bob::learn::libsvm::Machine::predictClass_
(const blitz::Array<double,1>& input) const {
  copy(input, m_input_size, m_input_cache, m_input_sub, m_input_div);
  int retval = round(svm_predict(m_model.get(), m_input_cache.get()));
  return retval;
}

int bob::learn::libsvm::Machine::predictClass
(const blitz::Array<double,1>& input) const {

  if ((size_t)input.extent(0) < inputSize()) {
    boost::format s("input for this SVM should have **at least** %d components, but you provided an array with %d elements instead");
    s % inputSize() % input.extent(0);
    throw std::runtime_error(s.str());
  }

  return predictClass_(input);
}

int bob::learn::libsvm::Machine::predictClassAndScores_
(const blitz::Array<double,1>& input,
 blitz::Array<double,1>& scores) const {
  copy(input, m_input_size, m_input_cache, m_input_sub, m_input_div);
#if LIBSVM_VERSION > 290
  int retval = round(svm_predict_values(m_model.get(), m_input_cache.get(), scores.data()));
#else
  svm_predict_values(m_model.get(), m_input_cache.get(), scores.data());
  int retval = round(svm_predict(m_model.get(), m_input_cache.get()));
#endif
  return retval;
}

int bob::learn::libsvm::Machine::predictClassAndScores
(const blitz::Array<double,1>& input,
 blitz::Array<double,1>& scores) const {

  if ((size_t)input.extent(0) < inputSize()) {
    boost::format s("input for this SVM should have **at least** %d components, but you provided an array with %d elements instead");
    s % inputSize() % input.extent(0);
    throw std::runtime_error(s.str());
  }

  if (!bob::core::array::isCContiguous(scores)) {
    throw std::runtime_error("scores output array should be C-style contiguous and what you provided is not");
  }

  size_t N = outputSize();
  size_t size = N < 2 ? 1 : (N*(N-1))/2;
  if ((size_t)scores.extent(0) != size) {
    boost::format s("output scores for this SVM (%d classes) should have %d components, but you provided an array with %d elements instead");
    s % svm_get_nr_class(m_model.get()) % size % scores.extent(0);
    throw std::runtime_error(s.str());
  }

  return predictClassAndScores_(input, scores);
}

int bob::learn::libsvm::Machine::predictClassAndProbabilities_
(const blitz::Array<double,1>& input,
 blitz::Array<double,1>& probabilities) const {
  copy(input, m_input_size, m_input_cache, m_input_sub, m_input_div);
  int retval = round(svm_predict_probability(m_model.get(), m_input_cache.get(), probabilities.data()));
  return retval;
}

int bob::learn::libsvm::Machine::predictClassAndProbabilities
(const blitz::Array<double,1>& input,
 blitz::Array<double,1>& probabilities) const {

  if ((size_t)input.extent(0) < inputSize()) {
    boost::format s("input for this SVM should have **at least** %d components, but you provided an array with %d elements instead");
    s % inputSize() % input.extent(0);
    throw std::runtime_error(s.str());
  }

  if (!supportsProbability()) {
    throw std::runtime_error("this SVM does not support probabilities");
  }

  if (!bob::core::array::isCContiguous(probabilities)) {
    throw std::runtime_error("probabilities output array should be C-style contiguous and what you provided is not");
  }

  if ((size_t)probabilities.extent(0) != outputSize()) {
    boost::format s("output probabilities for this SVM should have %d components, but you provided an array with %d elements instead");
    s % outputSize() % probabilities.extent(0);
    throw std::runtime_error(s.str());
  }

  return predictClassAndProbabilities_(input, probabilities);
}

void bob::learn::libsvm::Machine::save(const std::string& filename) const {
  if (svm_save_model(filename.c_str(), m_model.get())) {
    boost::format s("cannot save SVM model to file '%s'");
    s % filename;
    throw std::runtime_error(s.str());
  }
}

void bob::learn::libsvm::Machine::save(bob::io::base::HDF5File& config) const {
  config.setArray("svm_model", bob::learn::libsvm::svm_pickle(m_model));
  config.setArray("input_subtract", m_input_sub);
  config.setArray("input_divide", m_input_div);
  uint64_t version = LIBSVM_VERSION;
  config.setAttribute(".", "version", version);
}
