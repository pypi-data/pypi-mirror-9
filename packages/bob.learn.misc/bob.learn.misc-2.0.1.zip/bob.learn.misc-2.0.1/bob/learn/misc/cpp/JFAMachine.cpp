/**
 * @date Sat Jul 23 21:41:15 2011 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */


#include <bob.learn.misc/JFAMachine.h>
#include <bob.core/array_copy.h>
#include <bob.math/linear.h>
#include <bob.math/inv.h>
#include <bob.learn.misc/LinearScoring.h>
#include <limits>


//////////////////// FABase ////////////////////
bob::learn::misc::FABase::FABase():
  m_ubm(boost::shared_ptr<bob::learn::misc::GMMMachine>()), m_ru(1), m_rv(1),
  m_U(0,1), m_V(0,1), m_d(0)
{
}

bob::learn::misc::FABase::FABase(const boost::shared_ptr<bob::learn::misc::GMMMachine> ubm,
    const size_t ru, const size_t rv):
  m_ubm(ubm), m_ru(ru), m_rv(rv),
  m_U(getDimCD(),ru), m_V(getDimCD(),rv), m_d(getDimCD())
{
  if (ru < 1) {
    boost::format m("value for parameter `ru' (%lu) cannot be smaller than 1");
    m % ru;
    throw std::runtime_error(m.str());
  }
  if (rv < 1) {
    boost::format m("value for parameter `rv' (%lu) cannot be smaller than 1");
    m % ru;
    throw std::runtime_error(m.str());
  }
  updateCache();
}

bob::learn::misc::FABase::FABase(const bob::learn::misc::FABase& other):
  m_ubm(other.m_ubm), m_ru(other.m_ru), m_rv(other.m_rv),
  m_U(bob::core::array::ccopy(other.m_U)),
  m_V(bob::core::array::ccopy(other.m_V)),
  m_d(bob::core::array::ccopy(other.m_d))
{
  updateCache();
}

bob::learn::misc::FABase::~FABase() {
}

bob::learn::misc::FABase& bob::learn::misc::FABase::operator=
(const bob::learn::misc::FABase& other)
{
  if (this != &other)
  {
    m_ubm = other.m_ubm;
    m_ru = other.m_ru;
    m_rv = other.m_rv;
    m_U.reference(bob::core::array::ccopy(other.m_U));
    m_V.reference(bob::core::array::ccopy(other.m_V));
    m_d.reference(bob::core::array::ccopy(other.m_d));

    updateCache();
  }
  return *this;
}

bool bob::learn::misc::FABase::operator==(const bob::learn::misc::FABase& b) const
{
  return ( (((m_ubm && b.m_ubm) && *m_ubm == *(b.m_ubm)) || (!m_ubm && !b.m_ubm)) &&
          m_ru == b.m_ru && m_rv == b.m_rv &&
          bob::core::array::isEqual(m_U, b.m_U) &&
          bob::core::array::isEqual(m_V, b.m_V) &&
          bob::core::array::isEqual(m_d, b.m_d));
}

bool bob::learn::misc::FABase::operator!=(const bob::learn::misc::FABase& b) const
{
  return !(this->operator==(b));
}

bool bob::learn::misc::FABase::is_similar_to(const bob::learn::misc::FABase& b,
    const double r_epsilon, const double a_epsilon) const
{
  // TODO: update is_similar_to of the GMMMachine with the 2 epsilon's
  return (( ((m_ubm && b.m_ubm) && m_ubm->is_similar_to(*(b.m_ubm), a_epsilon)) ||
            (!m_ubm && !b.m_ubm) ) &&
          m_ru == b.m_ru && m_rv == b.m_rv &&
          bob::core::array::isClose(m_U, b.m_U, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_V, b.m_V, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_d, b.m_d, r_epsilon, a_epsilon));
}

void bob::learn::misc::FABase::resize(const size_t ru, const size_t rv)
{
  if (ru < 1) {
    boost::format m("value for parameter `ru' (%lu) cannot be smaller than 1");
    m % ru;
    throw std::runtime_error(m.str());
  }
  if (rv < 1) {
    boost::format m("value for parameter `rv' (%lu) cannot be smaller than 1");
    m % ru;
    throw std::runtime_error(m.str());
  }

  m_ru = ru;
  m_rv = rv;
  m_U.resizeAndPreserve(m_U.extent(0), ru);
  m_V.resizeAndPreserve(m_V.extent(0), rv);

  updateCacheUbmUVD();
}

void bob::learn::misc::FABase::resize(const size_t ru, const size_t rv, const size_t cd)
{
  if (ru < 1) {
    boost::format m("value for parameter `ru' (%lu) cannot be smaller than 1");
    m % ru;
    throw std::runtime_error(m.str());
  }
  if (rv < 1) {
    boost::format m("value for parameter `rv' (%lu) cannot be smaller than 1");
    m % ru;
    throw std::runtime_error(m.str());
  }

  if (!m_ubm || (m_ubm && getDimCD() == cd))
  {
    m_ru = ru;
    m_rv = rv;
    m_U.resizeAndPreserve(cd, ru);
    m_V.resizeAndPreserve(cd, rv);
    m_d.resizeAndPreserve(cd);

    updateCacheUbmUVD();
  }
  else {
    boost::format m("value for parameter `cd' (%lu) is not set to %lu");
    m % cd % getDimCD();
    throw std::runtime_error(m.str());
  }
}

void bob::learn::misc::FABase::setUbm(const boost::shared_ptr<bob::learn::misc::GMMMachine> ubm)
{
  m_ubm = ubm;
  m_U.resizeAndPreserve(getDimCD(), m_ru);
  m_V.resizeAndPreserve(getDimCD(), m_rv);
  m_d.resizeAndPreserve(getDimCD());

  updateCache();
}

void bob::learn::misc::FABase::setU(const blitz::Array<double,2>& U)
{
  if(U.extent(0) != m_U.extent(0)) { //checks dimension
    boost::format m("number of rows in parameter `U' (%d) does not match the expected size (%d)");
    m % U.extent(0) % m_U.extent(0);
    throw std::runtime_error(m.str());
  }
  if(U.extent(1) != m_U.extent(1)) { //checks dimension
    boost::format m("number of columns in parameter `U' (%d) does not match the expected size (%d)");
    m % U.extent(1) % m_U.extent(1);
    throw std::runtime_error(m.str());
  }
  m_U.reference(bob::core::array::ccopy(U));

  // update cache
  updateCacheUbmUVD();
}

void bob::learn::misc::FABase::setV(const blitz::Array<double,2>& V)
{
  if(V.extent(0) != m_V.extent(0)) { //checks dimension
    boost::format m("number of rows in parameter `V' (%d) does not match the expected size (%d)");
    m % V.extent(0) % m_V.extent(0);
    throw std::runtime_error(m.str());
  }
  if(V.extent(1) != m_V.extent(1)) { //checks dimension
    boost::format m("number of columns in parameter `V' (%d) does not match the expected size (%d)");
    m % V.extent(1) % m_V.extent(1);
    throw std::runtime_error(m.str());
  }
  m_V.reference(bob::core::array::ccopy(V));
}

void bob::learn::misc::FABase::setD(const blitz::Array<double,1>& d)
{
  if(d.extent(0) != m_d.extent(0)) { //checks dimension
    boost::format m("size of input vector `d' (%d) does not match the expected size (%d)");
    m % d.extent(0) % m_d.extent(0);
    throw std::runtime_error(m.str());
  }
  m_d.reference(bob::core::array::ccopy(d));
}


void bob::learn::misc::FABase::updateCache()
{
  updateCacheUbm();
  updateCacheUbmUVD();
  resizeTmp();
}

void bob::learn::misc::FABase::resizeTmp()
{
  m_tmp_IdPlusUSProdInv.resize(getDimRu(),getDimRu());
  m_tmp_Fn_x.resize(getDimCD());
  m_tmp_ru.resize(getDimRu());
  m_tmp_ruD.resize(getDimRu(), getDimD());
  m_tmp_ruru.resize(getDimRu(), getDimRu());
}

void bob::learn::misc::FABase::updateCacheUbm()
{
  // Put supervectors in cache
  if (m_ubm)
  {
    m_cache_mean.resize(getDimCD());
    m_cache_sigma.resize(getDimCD());
    m_ubm->getMeanSupervector(m_cache_mean);
    m_ubm->getVarianceSupervector(m_cache_sigma);
  }
}

void bob::learn::misc::FABase::updateCacheUbmUVD()
{
  // Compute and put  U^{T}.diag(sigma)^{-1} in cache
  if (m_ubm)
  {
    blitz::firstIndex i;
    blitz::secondIndex j;
    m_cache_UtSigmaInv.resize(getDimRu(), getDimCD());
    m_cache_UtSigmaInv = m_U(j,i) / m_cache_sigma(j); // Ut * diag(sigma)^-1
  }
}

void bob::learn::misc::FABase::computeIdPlusUSProdInv(const bob::learn::misc::GMMStats& gmm_stats,
  blitz::Array<double,2>& output) const
{
  // Computes (Id + U^T.Sigma^-1.U.N_{i,h}.U)^-1 =
  // (Id + sum_{c=1..C} N_{i,h}.U_{c}^T.Sigma_{c}^-1.U_{c})^-1

  // Blitz compatibility: ugly fix (const_cast, as old blitz version does not
  // provide a non-const version of transpose())
  blitz::Array<double,2> Ut = const_cast<blitz::Array<double,2>&>(m_U).transpose(1,0);

  blitz::firstIndex i;
  blitz::secondIndex j;
  blitz::Range rall = blitz::Range::all();

  bob::math::eye(m_tmp_ruru); // m_tmp_ruru = Id
  // Loop and add N_{i,h}.U_{c}^T.Sigma_{c}^-1.U_{c} to m_tmp_ruru at each iteration
  const size_t dim_c = getDimC();
  const size_t dim_d = getDimD();
  for(size_t c=0; c<dim_c; ++c) {
    blitz::Range rc(c*dim_d,(c+1)*dim_d-1);
    blitz::Array<double,2> Ut_c = Ut(rall,rc);
    blitz::Array<double,1> sigma_c = m_cache_sigma(rc);
    m_tmp_ruD = Ut_c(i,j) / sigma_c(j); // U_{c}^T.Sigma_{c}^-1
    blitz::Array<double,2> U_c = m_U(rc,rall);
    // Use m_cache_IdPlusUSProdInv as an intermediate array
    bob::math::prod(m_tmp_ruD, U_c, output); // U_{c}^T.Sigma_{c}^-1.U_{c}
    // Finally, add N_{i,h}.U_{c}^T.Sigma_{c}^-1.U_{c} to m_tmp_ruru
    m_tmp_ruru += output * gmm_stats.n(c);
  }
  // Computes the inverse
  bob::math::inv(m_tmp_ruru, output);
}


void bob::learn::misc::FABase::computeFn_x(const bob::learn::misc::GMMStats& gmm_stats,
  blitz::Array<double,1>& output) const
{
  // Compute Fn_x = sum_{sessions h}(N*(o - m) (Normalised first order statistics)
  blitz::Range rall = blitz::Range::all();
  const size_t dim_c = getDimC();
  const size_t dim_d = getDimD();
  for(size_t c=0; c<dim_c; ++c) {
    blitz::Range rc(c*dim_d,(c+1)*dim_d-1);
    blitz::Array<double,1> Fn_x_c = output(rc);
    blitz::Array<double,1> mean_c = m_cache_mean(rc);
    Fn_x_c = gmm_stats.sumPx(c,rall) - mean_c*gmm_stats.n(c);
  }
}

void bob::learn::misc::FABase::estimateX(const blitz::Array<double,2>& IdPlusUSProdInv,
  const blitz::Array<double,1>& Fn_x, blitz::Array<double,1>& x) const
{
  // m_tmp_ru = UtSigmaInv * Fn_x = Ut*diag(sigma)^-1 * N*(o - m)
  bob::math::prod(m_cache_UtSigmaInv, Fn_x, m_tmp_ru);
  // x = IdPlusUSProdInv * m_cache_UtSigmaInv * Fn_x
  bob::math::prod(IdPlusUSProdInv, m_tmp_ru, x);
}


void bob::learn::misc::FABase::estimateX(const bob::learn::misc::GMMStats& gmm_stats, blitz::Array<double,1>& x) const
{
  if (!m_ubm) throw std::runtime_error("No UBM was set in the JFA machine.");
  computeIdPlusUSProdInv(gmm_stats, m_tmp_IdPlusUSProdInv); // Computes first term
  computeFn_x(gmm_stats, m_tmp_Fn_x); // Computes last term
  estimateX(m_tmp_IdPlusUSProdInv, m_tmp_Fn_x, x); // Estimates the value of x
}



//////////////////// JFABase ////////////////////
bob::learn::misc::JFABase::JFABase()
{
}

bob::learn::misc::JFABase::JFABase(const boost::shared_ptr<bob::learn::misc::GMMMachine> ubm,
    const size_t ru, const size_t rv):
  m_base(ubm, ru, rv)
{
}

bob::learn::misc::JFABase::JFABase(const bob::learn::misc::JFABase& other):
  m_base(other.m_base)
{
}


bob::learn::misc::JFABase::JFABase(bob::io::base::HDF5File& config)
{
  load(config);
}

bob::learn::misc::JFABase::~JFABase() {
}

void bob::learn::misc::JFABase::save(bob::io::base::HDF5File& config) const
{
  config.setArray("U", m_base.getU());
  config.setArray("V", m_base.getV());
  config.setArray("d", m_base.getD());
}

void bob::learn::misc::JFABase::load(bob::io::base::HDF5File& config)
{
  //reads all data directly into the member variables
  blitz::Array<double,2> U = config.readArray<double,2>("U");
  blitz::Array<double,2> V = config.readArray<double,2>("V");
  blitz::Array<double,1> d = config.readArray<double,1>("d");
  const int ru = U.extent(1);
  const int rv = V.extent(1);
  if (!m_base.getUbm())
    m_base.resize(ru, rv, U.extent(0));
  else
    m_base.resize(ru, rv);
  m_base.setU(U);
  m_base.setV(V);
  m_base.setD(d);
}

bob::learn::misc::JFABase&
bob::learn::misc::JFABase::operator=(const bob::learn::misc::JFABase& other)
{
  if (this != &other)
  {
    m_base = other.m_base;
  }
  return *this;
}


//////////////////// ISVBase ////////////////////
bob::learn::misc::ISVBase::ISVBase()
{
}

bob::learn::misc::ISVBase::ISVBase(const boost::shared_ptr<bob::learn::misc::GMMMachine> ubm,
    const size_t ru):
  m_base(ubm, ru, 1)
{
  blitz::Array<double,2>& V = m_base.updateV();
  V = 0;
}

bob::learn::misc::ISVBase::ISVBase(const bob::learn::misc::ISVBase& other):
  m_base(other.m_base)
{
}


bob::learn::misc::ISVBase::ISVBase(bob::io::base::HDF5File& config)
{
  load(config);
}

bob::learn::misc::ISVBase::~ISVBase() {
}

void bob::learn::misc::ISVBase::save(bob::io::base::HDF5File& config) const
{
  config.setArray("U", m_base.getU());
  config.setArray("d", m_base.getD());
}

void bob::learn::misc::ISVBase::load(bob::io::base::HDF5File& config)
{
  //reads all data directly into the member variables
  blitz::Array<double,2> U = config.readArray<double,2>("U");
  blitz::Array<double,1> d = config.readArray<double,1>("d");
  const int ru = U.extent(1);
  if (!m_base.getUbm())
    m_base.resize(ru, 1, U.extent(0));
  else
    m_base.resize(ru, 1);
  m_base.setU(U);
  m_base.setD(d);
  blitz::Array<double,2>& V = m_base.updateV();
  V = 0;
}

bob::learn::misc::ISVBase&
bob::learn::misc::ISVBase::operator=(const bob::learn::misc::ISVBase& other)
{
  if (this != &other)
  {
    m_base = other.m_base;
  }
  return *this;
}



//////////////////// JFAMachine ////////////////////
bob::learn::misc::JFAMachine::JFAMachine():
  m_y(1), m_z(1)
{
  resizeTmp();
}

bob::learn::misc::JFAMachine::JFAMachine(const boost::shared_ptr<bob::learn::misc::JFABase> jfa_base):
  m_jfa_base(jfa_base),
  m_y(jfa_base->getDimRv()), m_z(jfa_base->getDimCD())
{
  if (!m_jfa_base->getUbm()) throw std::runtime_error("No UBM was set in the JFA machine.");
  updateCache();
  resizeTmp();
}


bob::learn::misc::JFAMachine::JFAMachine(const bob::learn::misc::JFAMachine& other):
  m_jfa_base(other.m_jfa_base),
  m_y(bob::core::array::ccopy(other.m_y)),
  m_z(bob::core::array::ccopy(other.m_z))
{
  updateCache();
  resizeTmp();
}

bob::learn::misc::JFAMachine::JFAMachine(bob::io::base::HDF5File& config)
{
  load(config);
}

bob::learn::misc::JFAMachine::~JFAMachine() {
}

bob::learn::misc::JFAMachine&
bob::learn::misc::JFAMachine::operator=(const bob::learn::misc::JFAMachine& other)
{
  if (this != &other)
  {
    m_jfa_base = other.m_jfa_base;
    m_y.reference(bob::core::array::ccopy(other.m_y));
    m_z.reference(bob::core::array::ccopy(other.m_z));
  }
  return *this;
}

bool bob::learn::misc::JFAMachine::operator==(const bob::learn::misc::JFAMachine& other) const
{
  return (*m_jfa_base == *(other.m_jfa_base) &&
          bob::core::array::isEqual(m_y, other.m_y) &&
          bob::core::array::isEqual(m_z, other.m_z));
}

bool bob::learn::misc::JFAMachine::operator!=(const bob::learn::misc::JFAMachine& b) const
{
  return !(this->operator==(b));
}


bool bob::learn::misc::JFAMachine::is_similar_to(const bob::learn::misc::JFAMachine& b,
    const double r_epsilon, const double a_epsilon) const
{
  return (m_jfa_base->is_similar_to(*(b.m_jfa_base), r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_y, b.m_y, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_z, b.m_z, r_epsilon, a_epsilon));
}

void bob::learn::misc::JFAMachine::save(bob::io::base::HDF5File& config) const
{
  config.setArray("y", m_y);
  config.setArray("z", m_z);
}

void bob::learn::misc::JFAMachine::load(bob::io::base::HDF5File& config)
{
  //reads all data directly into the member variables
  blitz::Array<double,1> y = config.readArray<double,1>("y");
  blitz::Array<double,1> z = config.readArray<double,1>("z");
  if (!m_jfa_base)
  {
    m_y.resize(y.extent(0));
    m_z.resize(z.extent(0));
  }
  setY(y);
  setZ(z);
  // update cache
  updateCache();
  resizeTmp();
}


void bob::learn::misc::JFAMachine::setY(const blitz::Array<double,1>& y)
{
  if(y.extent(0) != m_y.extent(0)) { //checks dimension
    boost::format m("size of input vector `y' (%d) does not match the expected size (%d)");
    m % y.extent(0) % m_y.extent(0);
    throw std::runtime_error(m.str());
  }
  m_y.reference(bob::core::array::ccopy(y));
  // update cache
  updateCache();
}

void bob::learn::misc::JFAMachine::setZ(const blitz::Array<double,1>& z)
{
  if(z.extent(0) != m_z.extent(0)) { //checks dimension
    boost::format m("size of input vector `z' (%d) does not match the expected size (%d)");
    m % z.extent(0) % m_z.extent(0);
    throw std::runtime_error(m.str());
  }
  m_z.reference(bob::core::array::ccopy(z));
  // update cache
  updateCache();
}

void bob::learn::misc::JFAMachine::setJFABase(const boost::shared_ptr<bob::learn::misc::JFABase> jfa_base)
{
  if (!jfa_base->getUbm())
    throw std::runtime_error("No UBM was set in the JFA machine.");
  m_jfa_base = jfa_base;
  // Resize variables
  resize();
}

void bob::learn::misc::JFAMachine::resize()
{
  m_y.resizeAndPreserve(getDimRv());
  m_z.resizeAndPreserve(getDimCD());
  updateCache();
  resizeTmp();
}

void bob::learn::misc::JFAMachine::resizeTmp()
{
  if (m_jfa_base)
  {
    m_tmp_Ux.resize(getDimCD());
  }
}

void bob::learn::misc::JFAMachine::updateCache()
{
  if (m_jfa_base)
  {
    // m + Vy + Dz
    m_cache_mVyDz.resize(getDimCD());
    bob::math::prod(m_jfa_base->getV(), m_y, m_cache_mVyDz);
    m_cache_mVyDz += m_jfa_base->getD()*m_z + m_jfa_base->getUbm()->getMeanSupervector();
    m_cache_x.resize(getDimRu());
  }
}

void bob::learn::misc::JFAMachine::estimateUx(const bob::learn::misc::GMMStats& gmm_stats,
  blitz::Array<double,1>& Ux)
{
  estimateX(gmm_stats, m_cache_x);
  bob::math::prod(m_jfa_base->getU(), m_cache_x, Ux);
}

void bob::learn::misc::JFAMachine::forward(const bob::learn::misc::GMMStats& input,
  double& score) const
{
  forward_(input, score);
}

void bob::learn::misc::JFAMachine::forward(const bob::learn::misc::GMMStats& gmm_stats,
  const blitz::Array<double,1>& Ux, double& score) const
{
  // Checks that a Base machine has been set
  if (!m_jfa_base) throw std::runtime_error("No UBM was set in the JFA machine.");

  score = bob::learn::misc::linearScoring(m_cache_mVyDz,
            m_jfa_base->getUbm()->getMeanSupervector(), m_jfa_base->getUbm()->getVarianceSupervector(),
            gmm_stats, Ux, true);
}

void bob::learn::misc::JFAMachine::forward_(const bob::learn::misc::GMMStats& input,
  double& score) const
{
  // Checks that a Base machine has been set
  if (!m_jfa_base) throw std::runtime_error("No UBM was set in the JFA machine.");

  // Ux and GMMStats
  estimateX(input, m_cache_x);
  bob::math::prod(m_jfa_base->getU(), m_cache_x, m_tmp_Ux);

  score = bob::learn::misc::linearScoring(m_cache_mVyDz,
            m_jfa_base->getUbm()->getMeanSupervector(), m_jfa_base->getUbm()->getVarianceSupervector(),
            input, m_tmp_Ux, true);
}



//////////////////// ISVMachine ////////////////////
bob::learn::misc::ISVMachine::ISVMachine():
  m_z(1)
{
  resizeTmp();
}

bob::learn::misc::ISVMachine::ISVMachine(const boost::shared_ptr<bob::learn::misc::ISVBase> isv_base):
  m_isv_base(isv_base),
  m_z(isv_base->getDimCD())
{
  if (!m_isv_base->getUbm())
    throw std::runtime_error("No UBM was set in the JFA machine.");
  updateCache();
  resizeTmp();
}


bob::learn::misc::ISVMachine::ISVMachine(const bob::learn::misc::ISVMachine& other):
  m_isv_base(other.m_isv_base),
  m_z(bob::core::array::ccopy(other.m_z))
{
  updateCache();
  resizeTmp();
}

bob::learn::misc::ISVMachine::ISVMachine(bob::io::base::HDF5File& config)
{
  load(config);
}

bob::learn::misc::ISVMachine::~ISVMachine() {
}

bob::learn::misc::ISVMachine&
bob::learn::misc::ISVMachine::operator=(const bob::learn::misc::ISVMachine& other)
{
  if (this != &other)
  {
    m_isv_base = other.m_isv_base;
    m_z.reference(bob::core::array::ccopy(other.m_z));
  }
  return *this;
}

bool bob::learn::misc::ISVMachine::operator==(const bob::learn::misc::ISVMachine& other) const
{
  return (*m_isv_base == *(other.m_isv_base) &&
          bob::core::array::isEqual(m_z, other.m_z));
}

bool bob::learn::misc::ISVMachine::operator!=(const bob::learn::misc::ISVMachine& b) const
{
  return !(this->operator==(b));
}


bool bob::learn::misc::ISVMachine::is_similar_to(const bob::learn::misc::ISVMachine& b,
    const double r_epsilon, const double a_epsilon) const
{
  return (m_isv_base->is_similar_to(*(b.m_isv_base), r_epsilon, a_epsilon) &&
          bob::core::array::isClose(m_z, b.m_z, r_epsilon, a_epsilon));
}

void bob::learn::misc::ISVMachine::save(bob::io::base::HDF5File& config) const
{
  config.setArray("z", m_z);
}

void bob::learn::misc::ISVMachine::load(bob::io::base::HDF5File& config)
{
  //reads all data directly into the member variables
  blitz::Array<double,1> z = config.readArray<double,1>("z");
  if (!m_isv_base)
    m_z.resize(z.extent(0));
  setZ(z);
  // update cache
  updateCache();
  resizeTmp();
}

void bob::learn::misc::ISVMachine::setZ(const blitz::Array<double,1>& z)
{
  if(z.extent(0) != m_z.extent(0)) { //checks dimension
    boost::format m("size of input vector `z' (%d) does not match the expected size (%d)");
    m % z.extent(0) % m_z.extent(0);
    throw std::runtime_error(m.str());
  }
  m_z.reference(bob::core::array::ccopy(z));
  // update cache
  updateCache();
}

void bob::learn::misc::ISVMachine::setISVBase(const boost::shared_ptr<bob::learn::misc::ISVBase> isv_base)
{
  if (!isv_base->getUbm())
    throw std::runtime_error("No UBM was set in the JFA machine.");
  m_isv_base = isv_base;
  // Resize variables
  resize();
}

void bob::learn::misc::ISVMachine::resize()
{
  m_z.resizeAndPreserve(getDimCD());
  updateCache();
  resizeTmp();
}

void bob::learn::misc::ISVMachine::resizeTmp()
{
  if (m_isv_base)
  {
    m_tmp_Ux.resize(getDimCD());
  }
}

void bob::learn::misc::ISVMachine::updateCache()
{
  if (m_isv_base)
  {
    // m + Dz
    m_cache_mDz.resize(getDimCD());
    m_cache_mDz = m_isv_base->getD()*m_z + m_isv_base->getUbm()->getMeanSupervector();
    m_cache_x.resize(getDimRu());
  }
}

void bob::learn::misc::ISVMachine::estimateUx(const bob::learn::misc::GMMStats& gmm_stats,
  blitz::Array<double,1>& Ux)
{
  estimateX(gmm_stats, m_cache_x);
  bob::math::prod(m_isv_base->getU(), m_cache_x, Ux);
}

void bob::learn::misc::ISVMachine::forward(const bob::learn::misc::GMMStats& input,
  double& score) const
{
  forward_(input, score);
}

void bob::learn::misc::ISVMachine::forward(const bob::learn::misc::GMMStats& gmm_stats,
  const blitz::Array<double,1>& Ux, double& score) const
{
  // Checks that a Base machine has been set
  if (!m_isv_base) throw std::runtime_error("No UBM was set in the JFA machine.");

  score = bob::learn::misc::linearScoring(m_cache_mDz,
            m_isv_base->getUbm()->getMeanSupervector(), m_isv_base->getUbm()->getVarianceSupervector(),
            gmm_stats, Ux, true);
}

void bob::learn::misc::ISVMachine::forward_(const bob::learn::misc::GMMStats& input,
  double& score) const
{
  // Checks that a Base machine has been set
  if(!m_isv_base) throw std::runtime_error("No UBM was set in the JFA machine.");

  // Ux and GMMStats
  estimateX(input, m_cache_x);
  bob::math::prod(m_isv_base->getU(), m_cache_x, m_tmp_Ux);

  score = bob::learn::misc::linearScoring(m_cache_mDz,
            m_isv_base->getUbm()->getMeanSupervector(), m_isv_base->getUbm()->getVarianceSupervector(),
            input, m_tmp_Ux, true);
}

