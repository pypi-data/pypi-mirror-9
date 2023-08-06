/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 17 May 2013 16:02:05 CEST
 *
 * @brief Implementation of the activation registry
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.activation/Activation.h>
#include <boost/make_shared.hpp>
#include <bob.core/logging.h>

boost::shared_ptr<bob::learn::activation::ActivationRegistry> bob::learn::activation::ActivationRegistry::instance() {
  static boost::shared_ptr<bob::learn::activation::ActivationRegistry> s_instance(new ActivationRegistry());
  return s_instance;
}

boost::shared_ptr<bob::learn::activation::Activation> bob::learn::activation::load_activation(bob::io::base::HDF5File& f) {
  auto make = ActivationRegistry::instance()->find(f.read<std::string>("id"));
  return make(f);
}

boost::shared_ptr<bob::learn::activation::Activation> bob::learn::activation::make_deprecated_activation(uint32_t e) {
  switch(e) {
    case 0:
      return boost::make_shared<bob::learn::activation::IdentityActivation>();
      break;
    case 1:
      return boost::make_shared<bob::learn::activation::HyperbolicTangentActivation>();
      break;
    case 2:
      return boost::make_shared<bob::learn::activation::LogisticActivation>();
      break;
    default:
      throw std::runtime_error("unsupported (deprecated) activation read from HDF5 file - not any of 0 (linear), 1 (tanh) or 2 (logistic)");
  }
}


void bob::learn::activation::ActivationRegistry::deregisterFactory(const std::string& id) {
  s_id2factory.erase(id);
}

void bob::learn::activation::ActivationRegistry::registerActivation(const std::string& id,
    bob::learn::activation::activation_factory_t factory) {

  auto it = s_id2factory.find(id);

  if (it == s_id2factory.end()) {
    s_id2factory[id] = factory;
  }
  else {
    if (s_id2factory[id] != factory) {
      boost::format m("replacing factory for activation functor `%s' with a different one is not allowed at this point");
      m % id;
      throw std::runtime_error(m.str());
    }
    //replacing with the same factory may be the result of multiple python
    //modules being loaded.
  }
}

bool bob::learn::activation::ActivationRegistry::isRegistered(const std::string& id) {
  return (s_id2factory.find(id) != s_id2factory.end());
}

bob::learn::activation::activation_factory_t bob::learn::activation::ActivationRegistry::find
(const std::string& id) {

  auto it = s_id2factory.find(id);

  if (it == s_id2factory.end()) {
    // try to convert the old "machine" name into the new "learn.activation" name
    auto i = id.find("machine");
    if (i != std::string::npos){
      std::string tid = id;
      tid.replace(i, 7, "learn.activation");

      it = s_id2factory.find(tid);
      if (it != s_id2factory.end()) {
        bob::core::warn << "Using the old name of the activation function '" << id << "' is deprecated. Please use '" << tid << "' instead!";
      }
    }
  }

  if (it == s_id2factory.end()) {
    boost::format m("unregistered activation function: %s");
    m % id;
    throw std::runtime_error(m.str());
  }

  return it->second;

}

/**
 * A generalized registration mechanism for all classes above
 */
template <typename T> struct register_activation {

  static boost::shared_ptr<bob::learn::activation::Activation> factory (bob::io::base::HDF5File& f) {
    auto retval = boost::make_shared<T>();
    retval->load(f);
    return retval;
  }

  register_activation() {
    T obj;
    bob::learn::activation::ActivationRegistry::instance()->registerActivation(obj.unique_identifier(), register_activation<T>::factory);
  }

};

// register all extensions
static register_activation<bob::learn::activation::IdentityActivation> _identity_act_reg;
static register_activation<bob::learn::activation::LinearActivation> _linear_act_reg;
static register_activation<bob::learn::activation::HyperbolicTangentActivation> _tanh_act_reg;
static register_activation<bob::learn::activation::MultipliedHyperbolicTangentActivation> _multanh_act_reg;
static register_activation<bob::learn::activation::LogisticActivation> _logistic_act_reg;


