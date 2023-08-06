/**
 * @file ip/cxx/HornAndSchunckFlow.cc
 * @date Wed Mar 16 15:01:13 2011 +0100
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Defines the HornAndSchunckFlow methods
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.core/assert.h>
#include <bob.sp/conv.h>
#include <bob.sp/extrapolate.h>

#include "HornAndSchunckFlow.h"

static const double LAPLACIAN_014_KERNEL_DATA[] = {0,.25,0,.25,0,.25,0,.25,0};
static const blitz::Array<double,2> LAPLACIAN_014_KERNEL(const_cast<double*>(LAPLACIAN_014_KERNEL_DATA), blitz::shape(3,3), blitz::neverDeleteData);

void bob::ip::optflow::laplacian_avg_hs_opencv(const blitz::Array<double,2>& input,
    blitz::Array<double,2>& output) {
  blitz::Array<double,2> inputExtra(bob::sp::getConvOutputSize(input, LAPLACIAN_014_KERNEL, bob::sp::Conv::Full));
  bob::sp::extrapolateMirror(input, inputExtra);
  bob::sp::conv(input, LAPLACIAN_014_KERNEL, output,
      bob::sp::Conv::Valid);
}

static const double _12 = 1./12.;
static const double _6 = 1./6.;
static const double LAPLACIAN_12_KERNEL_DATA[] = {_12,_6,_12,_6,0,_6,_12,_6,_12};
static const blitz::Array<double,2> LAPLACIAN_12_KERNEL(const_cast<double*>(LAPLACIAN_12_KERNEL_DATA), blitz::shape(3,3), blitz::neverDeleteData);

void bob::ip::optflow::laplacian_avg_hs(const blitz::Array<double,2>& input,
    blitz::Array<double,2>& output) {
  blitz::Array<double,2> inputExtra(bob::sp::getConvOutputSize(input, LAPLACIAN_12_KERNEL, bob::sp::Conv::Full));
  bob::sp::extrapolateMirror(input, inputExtra);
  bob::sp::conv(input, LAPLACIAN_12_KERNEL, output,
      bob::sp::Conv::Valid);
}
bob::ip::optflow::VanillaHornAndSchunckFlow::VanillaHornAndSchunckFlow
(const blitz::TinyVector<int,2>& shape) :
  m_gradient(shape),
  m_ex(shape),
  m_ey(shape),
  m_et(shape),
  m_u(shape),
  m_v(shape),
  m_cterm(shape)
{
}

bob::ip::optflow::VanillaHornAndSchunckFlow::~VanillaHornAndSchunckFlow() { }

void bob::ip::optflow::VanillaHornAndSchunckFlow::setShape
(const blitz::TinyVector<int,2>& shape) {
  m_gradient.setShape(shape);
  m_ex.resize(shape);
  m_ey.resize(shape);
  m_et.resize(shape);
  m_u.resize(shape);
  m_v.resize(shape);
  m_cterm.resize(shape);
}

void bob::ip::optflow::VanillaHornAndSchunckFlow::operator() (double alpha,
    size_t iterations, const blitz::Array<double,2>& i1,
    const blitz::Array<double,2>& i2, blitz::Array<double,2>& u0,
    blitz::Array<double,2>& v0) const {

  bob::core::array::assertSameShape(i1, i2);
  bob::core::array::assertSameShape(i1, m_ex);
  bob::core::array::assertSameShape(u0, m_u);
  bob::core::array::assertSameShape(v0, m_v);

  m_gradient(i1, i2, m_ex, m_ey, m_et);
  double a2 = std::pow(alpha, 2);
  for (size_t i=0; i<iterations; ++i) {
    bob::ip::optflow::laplacian_avg_hs(u0, m_u);
    bob::ip::optflow::laplacian_avg_hs(v0, m_v);
    m_cterm = (m_ex*m_u + m_ey*m_v + m_et) /
      (blitz::pow2(m_ex) + blitz::pow2(m_ey) + a2);
    u0 = m_u - m_ex*m_cterm;
    v0 = m_v - m_ey*m_cterm;
  }
}

void bob::ip::optflow::VanillaHornAndSchunckFlow::evalEc2
(const blitz::Array<double,2>& u, const blitz::Array<double,2>& v,
 blitz::Array<double,2>& error) const {

  bob::core::array::assertSameShape(u, v);
  bob::core::array::assertSameShape(u, error);
  bob::core::array::assertSameShape(u, m_u);

  laplacian_avg_hs(u, m_u);
  laplacian_avg_hs(v, m_u);
  error = blitz::pow2(m_u - u) + blitz::pow2(m_v - v);

}

void bob::ip::optflow::VanillaHornAndSchunckFlow::evalEb
(const blitz::Array<double,2>& i1, const blitz::Array<double,2>& i2,
 const blitz::Array<double,2>& u, const blitz::Array<double,2>& v,
 blitz::Array<double,2>& error) const {

  bob::core::array::assertSameShape(i1, i2);
  bob::core::array::assertSameShape(u, v);
  bob::core::array::assertSameShape(u, error);
  bob::core::array::assertSameShape(error, m_u);
  m_gradient(i1, i2, m_ex, m_ey, m_et);
  error = m_ex*u + m_ey*v + m_et;

}

bob::ip::optflow::HornAndSchunckFlow::HornAndSchunckFlow
(const blitz::TinyVector<int,2>& shape) :
  m_gradient(shape),
  m_ex(shape),
  m_ey(shape),
  m_et(shape),
  m_u(shape),
  m_v(shape),
  m_cterm(shape)
{
}

bob::ip::optflow::HornAndSchunckFlow::~HornAndSchunckFlow() { }

void bob::ip::optflow::HornAndSchunckFlow::setShape
(const blitz::TinyVector<int,2>& shape) {
  m_gradient.setShape(shape);
  m_ex.resize(shape);
  m_ey.resize(shape);
  m_et.resize(shape);
  m_u.resize(shape);
  m_v.resize(shape);
  m_cterm.resize(shape);
}

void bob::ip::optflow::HornAndSchunckFlow::operator() (double alpha,
    size_t iterations, const blitz::Array<double,2>& i1,
    const blitz::Array<double,2>& i2, const blitz::Array<double,2>& i3,
    blitz::Array<double,2>& u0, blitz::Array<double,2>& v0) const {

  bob::core::array::assertSameShape(i1, i2);
  bob::core::array::assertSameShape(i2, i3);
  bob::core::array::assertSameShape(i1, m_ex);
  bob::core::array::assertSameShape(u0, m_u);
  bob::core::array::assertSameShape(v0, m_v);

  m_gradient(i1, i2, i3, m_ex, m_ey, m_et);
  double a2 = std::pow(alpha, 2);
  for (size_t i=0; i<iterations; ++i) {
    bob::ip::optflow::laplacian_avg_hs_opencv(u0, m_u);
    bob::ip::optflow::laplacian_avg_hs_opencv(v0, m_v);
    m_cterm = (m_ex*m_u + m_ey*m_v + m_et) /
      (blitz::pow2(m_ex) + blitz::pow2(m_ey) + a2);
    u0 = m_u - m_ex*m_cterm;
    v0 = m_v - m_ey*m_cterm;
  }
}

void bob::ip::optflow::HornAndSchunckFlow::evalEc2
(const blitz::Array<double,2>& u, const blitz::Array<double,2>& v,
 blitz::Array<double,2>& error) const {

  bob::core::array::assertSameShape(u, v);
  bob::core::array::assertSameShape(u, error);
  bob::core::array::assertSameShape(u, m_u);

  laplacian_avg_hs_opencv(u, m_u);
  laplacian_avg_hs_opencv(v, m_u);
  error = blitz::pow2(m_u - u) + blitz::pow2(m_v - v);

}

void bob::ip::optflow::HornAndSchunckFlow::evalEb
(const blitz::Array<double,2>& i1, const blitz::Array<double,2>& i2,
 const blitz::Array<double,2>& i3, const blitz::Array<double,2>& u,
 const blitz::Array<double,2>& v, blitz::Array<double,2>& error) const {

  bob::core::array::assertSameShape(i1, i2);
  bob::core::array::assertSameShape(i2, i3);
  bob::core::array::assertSameShape(u, v);
  bob::core::array::assertSameShape(u, error);
  bob::core::array::assertSameShape(error, m_u);

  m_gradient(i1, i2, i3, m_ex, m_ey, m_et);
  error = m_ex*u + m_ey*v + m_et;

}

void bob::ip::optflow::flowError (const blitz::Array<double,2>& i1,
    const blitz::Array<double,2>& i2, const blitz::Array<double,2>& u,
    const blitz::Array<double,2>& v, blitz::Array<double,2>& error) {
  bob::core::array::assertSameShape(i1, i2);
  bob::core::array::assertSameShape(u, v);
  bob::core::array::assertSameShape(i1, u);
  bob::core::array::assertSameShape(i1, error);
  error = 0;
  for (int i=0; i<i1.extent(1); ++i) {
    for (int j=0; j<i1.extent(0); ++j) {
      int i_ = i - u(j,i); //flow adjustment
      if (i_ >= i1.extent(1)) continue; //cannot project
      int j_ = j - v(j,i); //flow adjustment
      if (j_ >= i1.extent(0)) continue; //cannot project
      error(j,i) = i2(j_,i_) - i1(j,i);
    }
  }
}
