/**
 * @date Tue May 31 09:22:33 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implements a Machine
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <cmath>
#include <boost/make_shared.hpp>
#include <boost/format.hpp>

#include <bob.core/array_copy.h>
#include <bob.math/linear.h>

#include <bob.learn.linear/machine.h>

namespace bob { namespace learn { namespace linear {

  Machine::Machine(const blitz::Array<double,2>& weight)
    : m_input_sub(weight.extent(0)),
    m_input_div(weight.extent(0)),
    m_bias(weight.extent(1)),
    m_activation(boost::make_shared<bob::learn::activation::IdentityActivation>()),
    m_buffer(weight.extent(0))
  {
    m_input_sub = 0.0;
    m_input_div = 1.0;
    m_bias = 0.0;
    m_weight.reference(bob::core::array::ccopy(weight));
  }

  Machine::Machine():
    m_input_sub(0),
    m_input_div(0),
    m_weight(0, 0),
    m_bias(0),
    m_activation(boost::make_shared<bob::learn::activation::IdentityActivation>()),
    m_buffer(0)
  {
  }

  Machine::Machine(size_t n_input, size_t n_output):
    m_input_sub(n_input),
    m_input_div(n_input),
    m_weight(n_input, n_output),
    m_bias(n_output),
    m_activation(boost::make_shared<bob::learn::activation::IdentityActivation>()),
    m_buffer(n_input)
  {
    m_input_sub = 0.0;
    m_input_div = 1.0;
    m_weight = 0.0;
    m_bias = 0.0;
  }

  Machine::Machine(const Machine& other):
    m_input_sub(bob::core::array::ccopy(other.m_input_sub)),
    m_input_div(bob::core::array::ccopy(other.m_input_div)),
    m_weight(bob::core::array::ccopy(other.m_weight)),
    m_bias(bob::core::array::ccopy(other.m_bias)),
    m_activation(other.m_activation),
    m_buffer(m_input_sub.shape())
  {
  }

  Machine::Machine (bob::io::base::HDF5File& config) {
    load(config);
  }

  Machine::~Machine() {}

  Machine& Machine::operator=
    (const Machine& other) {
      if(this != &other)
      {
        m_input_sub.reference(bob::core::array::ccopy(other.m_input_sub));
        m_input_div.reference(bob::core::array::ccopy(other.m_input_div));
        m_weight.reference(bob::core::array::ccopy(other.m_weight));
        m_bias.reference(bob::core::array::ccopy(other.m_bias));
        m_activation = other.m_activation;
        m_buffer.resize(m_input_sub.shape());
      }
      return *this;
    }

  bool Machine::operator==(const Machine& b) const {
    return (bob::core::array::isEqual(m_input_sub, b.m_input_sub) &&
        bob::core::array::isEqual(m_input_div, b.m_input_div) &&
        bob::core::array::isEqual(m_weight, b.m_weight) &&
        bob::core::array::isEqual(m_bias, b.m_bias) &&
        m_activation->str() == b.m_activation->str());
  }

  bool Machine::operator!=(const Machine& b) const {
    return !(this->operator==(b));
  }

  bool Machine::is_similar_to(const Machine& b, const double r_epsilon, const double a_epsilon) const {

    return (bob::core::array::isClose(m_input_sub, b.m_input_sub, r_epsilon, a_epsilon) &&
        bob::core::array::isClose(m_input_div, b.m_input_div, r_epsilon, a_epsilon) &&
        bob::core::array::isClose(m_weight, b.m_weight, r_epsilon, a_epsilon) &&
        bob::core::array::isClose(m_bias, b.m_bias, r_epsilon, a_epsilon) &&
        m_activation->str() == b.m_activation->str());
  }

  void Machine::load (bob::io::base::HDF5File& config) {

    //reads all data directly into the member variables
    m_input_sub.reference(config.readArray<double,1>("input_sub"));
    m_input_div.reference(config.readArray<double,1>("input_div"));
    m_weight.reference(config.readArray<double,2>("weights"));
    m_bias.reference(config.readArray<double,1>("biases"));
    m_buffer.resize(m_input_sub.extent(0));

    //switch between different versions - support for version 1
    if (config.hasAttribute(".", "version")) { //new version
      config.cd("activation");
      m_activation = bob::learn::activation::load_activation(config);
      config.cd("..");
    }
    else { //old version
      uint32_t act = config.read<uint32_t>("activation");
      m_activation = bob::learn::activation::make_deprecated_activation(act);
    }

  }

  void Machine::resize (size_t input, size_t output) {

    m_input_sub.resizeAndPreserve(input);
    m_input_div.resizeAndPreserve(input);
    m_buffer.resizeAndPreserve(input);
    m_weight.resizeAndPreserve(input, output);
    m_bias.resizeAndPreserve(output);

  }

  void Machine::save (bob::io::base::HDF5File& config) const {

    config.setAttribute(".", "version", 1);
    config.setArray("input_sub", m_input_sub);
    config.setArray("input_div", m_input_div);
    config.setArray("weights", m_weight);
    config.setArray("biases", m_bias);
    config.createGroup("activation");
    config.cd("activation");
    m_activation->save(config);
    config.cd("..");

  }

  void Machine::forward_ (const blitz::Array<double,1>& input, blitz::Array<double,1>& output) const {

    m_buffer = (input - m_input_sub) / m_input_div;
    bob::math::prod_(m_buffer, m_weight, output);
    for (int i=0; i<m_weight.extent(1); ++i)
      output(i) = m_activation->f(output(i) + m_bias(i));

  }

  void Machine::forward (const blitz::Array<double,1>& input, blitz::Array<double,1>& output) const {

    if (m_weight.extent(0) != input.extent(0)) { //checks input dimension
      boost::format m("mismatch on the input dimension: expected a vector of size %d, but you input one with size = %d instead");
      m % m_weight.extent(0) % input.extent(0);
      throw std::runtime_error(m.str());
    }
    if (m_weight.extent(1) != output.extent(0)) { //checks output dimension
      boost::format m("mismatch on the output dimension: expected a vector of size %d, but you input one with size = %d instead");
      m % m_weight.extent(1) % output.extent(0);
      throw std::runtime_error(m.str());
    }
    forward_(input, output);

  }

  void Machine::setWeights (const blitz::Array<double,2>& weight) {

    if (weight.extent(0) != m_input_sub.extent(0)) { //checks 1st dimension
      boost::format m("mismatch on the weight shape (number of rows): expected a weight matrix with %d row(s), but you input one with %d row(s) instead");
      m % m_input_sub.extent(0) % weight.extent(0);
      throw std::runtime_error(m.str());
    }
    if (weight.extent(1) != m_bias.extent(0)) { //checks 2nd dimension
      boost::format m("mismatch on the weight shape (number of columns): expected a weight matrix with %d column(s), but you input one with %d column(s) instead");
      m % m_bias.extent(0) % weight.extent(1);
      throw std::runtime_error(m.str());
    }
    m_weight.reference(bob::core::array::ccopy(weight));

  }

  void Machine::setBiases (const blitz::Array<double,1>& bias) {

    if (m_weight.extent(1) != bias.extent(0)) {
      boost::format m("mismatch on the bias shape: expected a vector of size %d, but you input one with size = %d instead");
      m % m_weight.extent(1) % bias.extent(0);
      throw std::runtime_error(m.str());
    }
    m_bias.reference(bob::core::array::ccopy(bias));

  }

  void Machine::setInputSubtraction (const blitz::Array<double,1>& v) {

    if (m_weight.extent(0) != v.extent(0)) {
      boost::format m("mismatch on the input subtraction shape: expected a vector of size %d, but you input one with size = %d instead");
      m % m_weight.extent(0) % v.extent(0);
      throw std::runtime_error(m.str());
    }
    m_input_sub.reference(bob::core::array::ccopy(v));

  }

  void Machine::setInputDivision (const blitz::Array<double,1>& v) {

    if (m_weight.extent(0) != v.extent(0)) {
      boost::format m("mismatch on the input division shape: expected a vector of size %d, but you input one with size = %d instead");
      m % m_weight.extent(0) % v.extent(0);
      throw std::runtime_error(m.str());
    }
    m_input_div.reference(bob::core::array::ccopy(v));

  }

  void Machine::setActivation (boost::shared_ptr<bob::learn::activation::Activation> a) {
    m_activation = a;
  }

}}}
