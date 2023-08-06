/**
 * @date Tue Jun  5 16:54:27 CEST 2012
 * @author Manuel Guenther <Manuel.Guenther@idiap.ch>
 *
 * A machine that implements the liner projection of input to the output using
 * weights, biases and sums:
 * output = sum(inputs * weights) + bias
 * It is possible to setup the machine to previously normalize the input taking
 * into consideration some input bias and division factor. It is also possible
 * to set it up to have an activation function.
 * A linear classifier. See C. M. Bishop, "Pattern Recognition and Machine
 * Learning", chapter 4
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.linear/bic.h>
#include <bob.learn.linear/pca.h>
#include <bob.math/linear.h>
#include <bob.core/assert.h>
#include <bob.core/check.h>


/*************************************************************
************************ BIC Machine *************************
*************************************************************/

/**
 * Initializes an empty BIC Machine
 *
 * @param use_DFFS  Add the Distance From Feature Space during score computation?
 */
bob::learn::linear::BICMachine::BICMachine(bool use_DFFS)
:
  m_project_data(use_DFFS),
  m_use_DFFS(use_DFFS)
{}

/**
 * Assigns the other BICMachine to this, i.e., makes a deep copy of the given machine.
 *
 * @param  other  The other BICMachine to get a shallow copy of
 * @return a reference to *this
 */
bob::learn::linear::BICMachine::BICMachine(const BICMachine& other)
:
  m_project_data(other.m_project_data),
  m_use_DFFS(other.m_use_DFFS)
{
  if (m_project_data){
    setBIC(false, other.m_mu_I, other.m_lambda_I, other.m_Phi_I, other.m_rho_I, true);
    setBIC(true , other.m_mu_E, other.m_lambda_E, other.m_Phi_E, other.m_rho_E, true);
  } else {
    setIEC(false, other.m_mu_I, other.m_lambda_I, true);
    setIEC(true , other.m_mu_E, other.m_lambda_E, true);
  }
}

/**
 * Assigns the other BICMachine to this, i.e., makes a deep copy of the given machine.
 *
 * @param  other  The other BICMachine to get a shallow copy of
 * @return a reference to *this
 */
bob::learn::linear::BICMachine::BICMachine(bob::io::base::HDF5File& hdf5)
{
  load(hdf5);
}


/**
 * Assigns the other BICMachine to this, i.e., makes a deep copy of the given BICMachine
 *
 * @param  other  The other BICMachine to get a deep copy of
 * @return a reference to *this
 */
bob::learn::linear::BICMachine& bob::learn::linear::BICMachine::operator=(const BICMachine& other)
{
  if (this != &other)
  {
    if (other.m_project_data){
      m_use_DFFS = other.m_use_DFFS;
      setBIC(false, other.m_mu_I, other.m_lambda_I, other.m_Phi_I, other.m_rho_I, true);
      setBIC(true , other.m_mu_E, other.m_lambda_E, other.m_Phi_E, other.m_rho_E, true);
    } else {
      m_use_DFFS = false;
      setIEC(false, other.m_mu_I, other.m_lambda_I, true);
      setIEC(true , other.m_mu_E, other.m_lambda_E, true);
    }
  }
  return *this;
}

/**
 * Compares if this machine and the given one are identical
 *
 * @param  other  The BICMachine to compare with
 * @return true if both machines are identical, i.e., have exactly the same parameters, otherwise false
 */
bool bob::learn::linear::BICMachine::operator==(const BICMachine& other) const
{
  return (m_project_data == other.m_project_data &&
          (!m_project_data || m_use_DFFS == other.m_use_DFFS) &&
          bob::core::array::isEqual(m_mu_I, other.m_mu_I) &&
          bob::core::array::isEqual(m_mu_E, other.m_mu_E) &&
          bob::core::array::isEqual(m_lambda_I, other.m_lambda_I) &&
          bob::core::array::isEqual(m_lambda_E, other.m_lambda_E) &&
          (!m_project_data ||
              (bob::core::array::isEqual(m_Phi_I, other.m_Phi_I) &&
               bob::core::array::isEqual(m_Phi_E, other.m_Phi_E) &&
               (!m_use_DFFS || (m_rho_I == other.m_rho_I && m_rho_E == other.m_rho_E)))));
}

/**
 * Checks if this machine and the given one are different
 *
 * @param  other  The BICMachine to compare with
 * @return false if both machines are identical, i.e., have exactly the same parameters, otherwise true
 */
bool bob::learn::linear::BICMachine::operator!=(const BICMachine& other) const
{
  return !(this->operator==(other));
}

/**
 * Compares the given machine with this for similarity
 *
 * @param  other  The BICMachine to compare with
 * @param  r_epsilon  The largest value any parameter might relatively differ between the two machines
 * @param  a_epsilon  The largest value any parameter might absolutely differ between the two machines

 * @return true if both machines are approximately equal, otherwise false
 */
bool bob::learn::linear::BICMachine::is_similar_to(const BICMachine& other,
  const double r_epsilon, const double a_epsilon) const
{
  if (m_project_data){
    // compare data
    if (not bob::core::array::hasSameShape(m_Phi_I, other.m_Phi_I)) return false;
    if (not bob::core::array::hasSameShape(m_Phi_E, other.m_Phi_E)) return false;
    // check that the projection matrices are close,
    // but allow that eigen vectors might have opposite directions
    // (i.e., they are either identical -> difference is 0, or opposite -> sum is zero)
    for (int i = m_Phi_I.extent(1); i--;){
      const blitz::Array<double,1>& sub1 = m_Phi_I(blitz::Range::all(), i);
      const blitz::Array<double,1>& sub2 = other.m_Phi_I(blitz::Range::all(), i);
      blitz::Array<double,1> sub2_negative(-sub2);
      if (!bob::core::array::isClose(sub1, sub2, r_epsilon, a_epsilon) && !bob::core::array::isClose(sub1, sub2_negative, r_epsilon, a_epsilon)) return false;
    }
    for (int i = m_Phi_E.shape()[1]; i--;){
      const blitz::Array<double,1>& sub1 = m_Phi_E(blitz::Range::all(), i);
      const blitz::Array<double,1>& sub2 = other.m_Phi_E(blitz::Range::all(), i);
      blitz::Array<double,1> sub2_negative(-sub2);
      if (!bob::core::array::isClose(sub1, sub2, r_epsilon, a_epsilon) && !bob::core::array::isClose(sub1, sub2_negative, r_epsilon, a_epsilon)) return false;
    }
  }

  return (m_project_data == other.m_project_data &&
          (!m_project_data || m_use_DFFS == other.m_use_DFFS) &&
          bob::core::array::isClose(m_mu_I, other.m_mu_I, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_mu_E, other.m_mu_E, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_lambda_I, other.m_lambda_I, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_lambda_E, other.m_lambda_E, r_epsilon, a_epsilon) &&
          (!m_project_data ||
               (!m_use_DFFS || (bob::core::isClose(m_rho_I, other.m_rho_I, r_epsilon, a_epsilon) &&
                                bob::core::isClose(m_rho_E, other.m_rho_E, r_epsilon, a_epsilon)))));
}



void bob::learn::linear::BICMachine::initialize(bool clazz, int input_length, int projected_length){
  blitz::Array<double,1>& diff = clazz ? m_diff_E : m_diff_I;
  blitz::Array<double,1>& proj = clazz ? m_proj_E : m_proj_I;
  diff.resize(input_length);
  proj.resize(projected_length);
}

/**
 * Sets the parameters of the given class that are required for computing the IEC scores (Guenther, Wuertz)
 *
 * @param  clazz   false for the intrapersonal class, true for the extrapersonal one.
 * @param  mean    The mean vector of the training data
 * @param  variances  The variances of the training data
 * @param  copy_data  If true, makes a deep copy of the matrices, otherwise it just references it (the default)
 */
void bob::learn::linear::BICMachine::setIEC(
    bool clazz,
    const blitz::Array<double,1>& mean,
    const blitz::Array<double,1>& variances,
    bool copy_data
){
  m_project_data = false;
  // select the right matrices to write
  blitz::Array<double,1>& mu = clazz ? m_mu_E : m_mu_I;
  blitz::Array<double,1>& lambda = clazz ? m_lambda_E : m_lambda_I;

  // copy mean and variances
  if (copy_data){
    mu.resize(mean.shape());
    mu = mean;
    lambda.resize(variances.shape());
    lambda = variances;
  } else {
    mu.reference(mean);
    lambda.reference(variances);
  }
}

/**
 * Sets the parameters of the given class that are required for computing the BIC scores (Teixeira)
 *
 * @param  clazz   false for the intrapersonal class, true for the extrapersonal one.
 * @param  mean    The mean vector of the training data
 * @param  variances  The eigenvalues of the training data
 * @param  projection  The PCA projection matrix
 * @param  rho     The residual eigenvalues, used for DFFS calculation
 * @param  copy_data  If true, makes a deep copy of the matrices, otherwise it just references it (the default)
 */
void bob::learn::linear::BICMachine::setBIC(
    bool clazz,
    const blitz::Array<double,1>& mean,
    const blitz::Array<double,1>& variances,
    const blitz::Array<double,2>& projection,
    const double rho,
    bool copy_data
){
  m_project_data = true;
  // select the right matrices to write
  blitz::Array<double,1>& mu = clazz ? m_mu_E : m_mu_I;
  blitz::Array<double,1>& lambda = clazz ? m_lambda_E : m_lambda_I;
  blitz::Array<double,2>& Phi = clazz ? m_Phi_E : m_Phi_I;
  double& rho_ = clazz ? m_rho_E : m_rho_I;

  // copy information
  if (copy_data){
    mu.resize(mean.shape());
    mu = mean;
    lambda.resize(variances.shape());
    lambda = variances;
    Phi.resize(projection.shape());
    Phi = projection;
  } else {
    mu.reference(mean);
    lambda.reference(variances);
    Phi.reference(projection);
  }
  rho_ = rho;

  // check that rho has a reasonable value (if it is used)
  if (m_use_DFFS && rho_ < 1e-12) throw std::runtime_error("The given average eigenvalue (rho) is too close to zero");

  // initialize temporaries
  initialize(clazz, Phi.shape()[0], Phi.shape()[1]);
}

/**
 * Set or unset the usage of the Distance From Feature Space
 *
 * @param use_DFFS The new value of use_DFFS
 */
void bob::learn::linear::BICMachine::use_DFFS(bool use_DFFS){
  m_use_DFFS = use_DFFS;
  if (m_project_data && m_use_DFFS && (m_rho_E < 1e-12 || m_rho_I < 1e-12)) std::runtime_error("The average eigenvalue (rho) is too close to zero, so using DFFS will not work");
}

/**
 * Loads the BICMachine from the given hdf5 file.
 *
 * @param  config  The hdf5 file containing the required information.
 */
void bob::learn::linear::BICMachine::load(bob::io::base::HDF5File& config){
  //reads all data directly into the member variables
  m_project_data = config.read<bool>("project_data");
  m_mu_I.reference(config.readArray<double,1>("intra_mean"));
  m_lambda_I.reference(config.readArray<double,1>("intra_variance"));
  if (m_project_data){
    m_use_DFFS = config.read<bool>("use_DFFS");
    m_Phi_I.reference(config.readArray<double,2>("intra_subspace"));
    initialize(false, m_Phi_I.shape()[0], m_Phi_I.shape()[1]);
    m_rho_I = config.read<double>("intra_rho");
  }

  m_mu_E.reference(config.readArray<double,1>("extra_mean"));
  m_lambda_E.reference(config.readArray<double,1>("extra_variance"));
  if (m_project_data){
    m_Phi_E.reference(config.readArray<double,2>("extra_subspace"));
    initialize(true, m_Phi_E.shape()[0], m_Phi_E.shape()[1]);
    m_rho_E = config.read<double>("extra_rho");
  }
  // check that rho has reasonable values
  if (m_project_data && m_use_DFFS && (m_rho_E < 1e-12 || m_rho_I < 1e-12)) throw std::runtime_error("The loaded average eigenvalue (rho) is too close to zero");

}

/**
 * Saves the parameters of the BICMachine to the given hdf5 file.
 *
 * @param  config  The hdf5 file to write the configuration into.
 */
void bob::learn::linear::BICMachine::save(bob::io::base::HDF5File& config) const{
  config.set("project_data", m_project_data);
  config.setArray("intra_mean", m_mu_I);
  config.setArray("intra_variance", m_lambda_I);
  if (m_project_data){
    config.set("use_DFFS", m_use_DFFS);
    config.setArray("intra_subspace", m_Phi_I);
    config.set("intra_rho", m_rho_I);
  }

  config.setArray("extra_mean", m_mu_E);
  config.setArray("extra_variance", m_lambda_E);
  if (m_project_data){
    config.setArray("extra_subspace", m_Phi_E);
    config.set("extra_rho", m_rho_E);
  }
}

/**
 * Computes the BIC or IEC score for the given input vector.
 * The score itself is the log-likelihood score of the given input vector belonging to the intrapersonal class.
 * No sanity checks of input and output are performed.
 *
 * @param  input  A vector (of difference values) to compute the BIC or IEC score for.
 * @return  The score.
 */
double bob::learn::linear::BICMachine::forward_(const blitz::Array<double,1>& input) const{
  double output;
  if (m_project_data){
    // subtract mean
    m_diff_I = input - m_mu_I;
    m_diff_E = input - m_mu_E;
    // project data to intrapersonal and extrapersonal subspace
    bob::math::prod(m_diff_I, m_Phi_I, m_proj_I);
    bob::math::prod(m_diff_E, m_Phi_E, m_proj_E);

    // compute Mahalanobis distance
    output = blitz::sum(blitz::pow2(m_proj_E) / m_lambda_E) - blitz::sum(blitz::pow2(m_proj_I) / m_lambda_I);

    // add the DFFS?
    if (m_use_DFFS){
      output += blitz::sum(blitz::pow2(m_diff_E) - blitz::pow2(m_proj_E)) / m_rho_E;
      output -= blitz::sum(blitz::pow2(m_diff_I) - blitz::pow2(m_proj_I)) / m_rho_I;
    }
    output /= (m_proj_E.extent(0) + m_proj_I.extent(0));
  } else {
    // forward without projection
    output = blitz::mean( blitz::pow2(input - m_mu_E) / m_lambda_E
                        - blitz::pow2(input - m_mu_I) / m_lambda_I);
  }
  return output;
}

/**
 * Computes the BIC or IEC score for the given input vector.
 * The score itself is the log-likelihood score of the given input vector belonging to the intrapersonal class.
 * Sanity checks of input and output shape are performed.
 *
 * @param  input  A vector (of difference values) to compute the BIC or IEC score for.
 * @return  The score.
 */
double bob::learn::linear::BICMachine::forward(const blitz::Array<double,1>& input) const{
  // perform some checks
  bob::core::array::assertSameShape(input, m_mu_E);

  // call the actual method
  return forward_(input);
}


/*************************************************************
************************ BIC Trainer *************************
*************************************************************/


static double sqr(const double& x){
  return x*x;
}

/**
 * This function trains one of the classes of the given machine with the given data.
 * It computes either BIC projection matrices, or IEC mean and variance.
 *
 * @param  clazz    false for the intrapersonal class, true for the extrapersonal one.
 * @param  machine  The machine to be trained.
 * @param  differences  A set of (intra/extra)-personal difference vectors that should be trained.
 */
void bob::learn::linear::BICTrainer::train_single(bool clazz, bob::learn::linear::BICMachine& machine, const blitz::Array<double,2>& differences) const {
  int subspace_dim = clazz ? m_M_E : m_M_I;
  int input_dim = differences.extent(1);
  int data_count = differences.extent(0);
  blitz::Range a = blitz::Range::all();

  if (subspace_dim){
    // train the class using BIC

    // Compute PCA on the given dataset
    bob::learn::linear::PCATrainer trainer;
    const int n_eigs = trainer.output_size(differences);
    bob::learn::linear::Machine pca(input_dim, n_eigs);
    blitz::Array<double,1> variances(n_eigs);
    trainer.train(pca, variances, differences);

    // compute rho
    double rho = 0.;
    int non_zero_eigenvalues = std::min(input_dim, data_count-1);
    // assert that the number of kept eigenvalues is not chosen to big
    if (subspace_dim >= non_zero_eigenvalues)
      throw std::runtime_error((boost::format("The chosen subspace dimension %d is larger than the theoretical number of nonzero eigenvalues %d")%subspace_dim%non_zero_eigenvalues).str());
    // compute the average of the reminding eigenvalues
    for (int i = subspace_dim; i < non_zero_eigenvalues; ++i){
      rho += variances(i);
    }
    rho /= non_zero_eigenvalues - subspace_dim;

    // limit dimensionalities
    pca.resize(input_dim, subspace_dim);
    variances.resizeAndPreserve(subspace_dim);

    // check that all variances are meaningful
    for (int i = 0; i < subspace_dim; ++i){
      if (variances(i) < 1e-12)
        throw std::runtime_error((boost::format("The chosen subspace dimension is %d, but the %dth eigenvalue is already to small")%subspace_dim%i).str());
    }

    // initialize the machine
    blitz::Array<double, 2> projection = pca.getWeights();
    blitz::Array<double, 1> mean = pca.getInputSubtraction();
    machine.setBIC(clazz, mean, variances, projection, rho);
  } else {
    // train the class using IEC
    // => compute mean and variance only
    blitz::Array<double,1> mean(input_dim), variance(input_dim);

    // compute mean and variance
    mean = 0.;
    variance = 0.;
    for (int n = data_count; n--;){
      const blitz::Array<double,1>& diff = differences(n,a);
      for (int i = input_dim; i--;){
        mean(i) += diff(i);
        variance(i) += sqr(diff(i));
      }
    }
    // normalize mean and variances
    for (int i = 0; i < input_dim; ++i){
      // intrapersonal
      variance(i) = (variance(i) - sqr(mean(i)) / data_count) / (data_count - 1.);
      mean(i) /= data_count;
      if (variance(i) < 1e-12)
        throw std::runtime_error((boost::format("The variance of the %dth dimension is too small. Check your data!")%i).str());
    }

    // set the results to the machine
    machine.setIEC(clazz, mean, variance);
  }
}
