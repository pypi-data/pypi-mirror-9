/**
 * @date Thu Jul 7 16:49:35 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Activation functions for linear and MLP machines.
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_ACTIVATION_ACTIVATION_H
#define BOB_LEARN_ACTIVATION_ACTIVATION_H

#include <string>
#include <boost/shared_ptr.hpp>
#include <bob.io.base/HDF5File.h>

namespace bob { namespace learn { namespace activation {
  /**
   * Base class for activation functions. All activation functions must derive
   * from this one.
   */
  class Activation {

    public: // api

      /**
       * Computes activated value, given an input.
       */
      virtual double f (double z) const =0;

      /**
       * Computes the derivative of the current activation - i.e., the same
       * input as for f().
       */
      virtual double f_prime (double z) const { return f_prime_from_f(f(z)); }

      /**
       * Computes the derivative of the activated value, given the activated
       * value - that is, the output of Activation::f() above.
       */
      virtual double f_prime_from_f (double a) const =0;

      /**
       * Saves itself to an HDF5File
       */
      virtual void save(bob::io::base::HDF5File& f) const { f.set("id", unique_identifier()); }

      /**
       * Loads itself from an HDF5File
       */
      virtual void load(bob::io::base::HDF5File& f) {}

      /**
       * Returns a unique identifier, used by this class in connection to the
       * Activation registry.
       */
      virtual std::string unique_identifier() const =0;

      /**
       * Returns a stringified representation for this Activation function
       */
      virtual std::string str() const =0;

  };

  /**
   * Generic interface for Activation object factories
   */
  typedef boost::shared_ptr<Activation> (*activation_factory_t) (bob::io::base::HDF5File& f);

  /**
   * Loads an activation function from file using the new API
   */
  boost::shared_ptr<Activation> load_activation(bob::io::base::HDF5File& f);

  /**
   * Loads an activation function using the old API
   *
   * @param e The old enumeration value for activation functions:
   *        (0) - linear; (1) - tanh; (2) - logistic
   */
  boost::shared_ptr<Activation> make_deprecated_activation(uint32_t e);

  /**
   * Implements the activation function f(z) = z
   */
  class IdentityActivation: public Activation {

    public: // api

      virtual ~IdentityActivation() {}
      virtual double f (double z) const { return z; }
      virtual double f_prime (double z) const { return 1.; }
      virtual double f_prime_from_f (double a) const { return 1.; }
      virtual std::string unique_identifier() const { return "bob.learn.activation.Activation.Identity"; }
      virtual std::string str() const { return "f(z) = z"; }

  };

  /**
   * Implements the activation function f(z) = C*z
   */
  class LinearActivation: public Activation {

    public: // api

      LinearActivation(double C=1.) : m_C(C) {}
      virtual ~LinearActivation() {}
      virtual double f (double z) const { return m_C * z; }
      virtual double f_prime (double z) const { return m_C; }
      virtual double f_prime_from_f (double a) const { return m_C; }
      double C() const { return m_C; }
      virtual void save(bob::io::base::HDF5File& f) const { Activation::save(f); f.set("C", m_C); }
      virtual void load(bob::io::base::HDF5File& f) { m_C = f.read<double>("C"); }
      virtual std::string unique_identifier() const { return "bob.learn.activation.Activation.Linear"; }
      virtual std::string str() const { return (boost::format("f(z) = %.5e * z") % m_C).str(); }

    private: // representation

      double m_C; ///< multiplication factor

  };

  /**
   * Implements the activation function f(z) = std::tanh(z)
   */
  class HyperbolicTangentActivation: public Activation {

    public: // api

      virtual ~HyperbolicTangentActivation() {}
      virtual double f (double z) const { return std::tanh(z); }
      virtual double f_prime_from_f (double a) const { return (1. - (a*a)); }
      virtual std::string unique_identifier() const { return "bob.learn.activation.Activation.HyperbolicTangent"; }
      virtual std::string str() const { return "f(z) = tanh(z)"; }

  };

  /**
   * Implements the activation function f(z) = C*tanh(M*z)
   */
  class MultipliedHyperbolicTangentActivation: public Activation {

    public: // api

      MultipliedHyperbolicTangentActivation(double C=1., double M=1.) : m_C(C), m_M(M) {}
      virtual ~MultipliedHyperbolicTangentActivation() {}
      virtual double f (double z) const { return m_C * std::tanh(m_M * z); }
      virtual double f_prime_from_f (double a) const { return m_C * m_M * (1. - std::pow(a/m_C,2)); }
      double C() const { return m_C; }
      double M() const { return m_M; }
      virtual void save(bob::io::base::HDF5File& f) const { Activation::save(f); f.set("C", m_C); f.set("M", m_C); }
      virtual void load(bob::io::base::HDF5File& f) {m_C = f.read<double>("C"); m_M = f.read<double>("M"); }
      virtual std::string unique_identifier() const { return "bob.learn.activation.Activation.MultipliedHyperbolicTangent"; }
      virtual std::string str() const { return (boost::format("f(z) = %.5e * tanh(%.5e * z)") % m_C % m_M).str(); }

    private: // representation

      double m_C; ///< multiplication factor
      double m_M; ///< internal multiplication factor

  };

  /**
   * Implements the activation function f(z) = 1. / ( 1. + e^(-z) )
   */
  class LogisticActivation: public Activation {

    public: // api

      virtual ~LogisticActivation() {}
      virtual double f (double z) const { return 1. / ( 1. + std::exp(-z) ); }
      virtual double f_prime_from_f (double a) const { return a * (1. - a); }
      virtual std::string unique_identifier() const { return "bob.learn.activation.Activation.Logistic"; }
      virtual std::string str() const { return "f(z) = 1./(1. + e^-z)"; }

  };


  /**
   * The ActivationRegistry holds registered loaders for different types of
   * Activation functions.
   */
  class ActivationRegistry {

    public: //static access

      /**
       * Returns the singleton
       */
      static boost::shared_ptr<ActivationRegistry> instance();

      static const std::map<std::string, activation_factory_t>& getFactories ()
      {
        boost::shared_ptr<ActivationRegistry> ptr = instance();
        return ptr->s_id2factory;
      }

    public: //object access

      void registerActivation(const std::string& unique_identifier,
          activation_factory_t factory);

      void deregisterFactory(const std::string& unique_identifier);

      activation_factory_t find(const std::string& unique_identifier);

      bool isRegistered(const std::string& unique_identifier);

    private:

      ActivationRegistry (): s_id2factory() {}

      // Not implemented
      ActivationRegistry (const ActivationRegistry&);

      std::map<std::string, activation_factory_t> s_id2factory;

  };

} } }

#endif /* BOB_LEARN_ACTIVATION_ACTIVATION_H */

