/**
 * @file ip/cxx/SpatioTemporalGradient.cc
 * @date Tue Sep 6 17:29:53 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implementation of Spatio-Temporal Gradients as indicated on the
 * equivalent header file.
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include <cmath>
#include <bob.sp/extrapolate.h>
#include <bob.sp/conv.h>
#include <bob.core/assert.h>

#include "SpatioTemporalGradient.h"

static inline void fastconv(const blitz::Array<double,2>& image,
    const blitz::Array<double,1>& kernel,
    blitz::Array<double,2>& result, int dimension) {
  blitz::Array<double,2> imageExtra(bob::sp::getConvSepOutputSize(image, kernel, dimension, bob::sp::Conv::Full));
  bob::sp::extrapolateMirror(image, imageExtra);
  bob::sp::convSep(imageExtra, kernel, result, dimension, bob::sp::Conv::Valid);
}

bob::ip::optflow::ForwardGradient::ForwardGradient(const blitz::Array<double,1>& diff_kernel,
    const blitz::Array<double,1>& avg_kernel,
    const blitz::TinyVector<int,2>& shape) :
  m_diff_kernel(diff_kernel.copy()),
  m_avg_kernel(avg_kernel.copy()),
  m_buffer1(shape),
  m_buffer2(shape)
{
  blitz::TinyVector<int,1> required_shape(2);
  bob::core::array::assertSameShape(m_diff_kernel, required_shape);
  bob::core::array::assertSameShape(m_avg_kernel, required_shape);
}

bob::ip::optflow::ForwardGradient::ForwardGradient(const bob::ip::optflow::ForwardGradient& other) :
  m_diff_kernel(other.m_diff_kernel.copy()),
  m_avg_kernel(other.m_avg_kernel.copy()),
  m_buffer1(other.m_buffer1.shape()),
  m_buffer2(other.m_buffer2.shape())
{
}

bob::ip::optflow::ForwardGradient::~ForwardGradient() { }

bob::ip::optflow::ForwardGradient& bob::ip::optflow::ForwardGradient::operator= (const bob::ip::optflow::ForwardGradient& other) {
  m_diff_kernel.reference(other.m_diff_kernel.copy());
  m_avg_kernel.reference(other.m_avg_kernel.copy());
  m_buffer1.resize(other.m_buffer1.shape());
  m_buffer2.resize(other.m_buffer2.shape());
  return *this;
}

void bob::ip::optflow::ForwardGradient::setShape(const blitz::TinyVector<int,2>& shape) {
  m_buffer1.resize(shape);
  m_buffer2.resize(shape);
}

void bob::ip::optflow::ForwardGradient::setDiffKernel(const blitz::Array<double,1>& k) {
  bob::core::array::assertSameDimensionLength(k.extent(0), 2);
  m_diff_kernel.reference(k.copy());
}

void bob::ip::optflow::ForwardGradient::setAvgKernel(const blitz::Array<double,1>& k) {
  bob::core::array::assertSameDimensionLength(k.extent(0), 2);
  m_avg_kernel.reference(k.copy());
}

void bob::ip::optflow::ForwardGradient::operator()(const blitz::Array<double,2>& i1,
    const blitz::Array<double,2>& i2, blitz::Array<double,2>& Ex,
    blitz::Array<double,2>& Ey, blitz::Array<double,2>& Et) const {

  // all arrays have to have the same shape
  bob::core::array::assertSameShape(i1, i2);
  bob::core::array::assertSameShape(Ex, Ey);
  bob::core::array::assertSameShape(Ey, Et);
  bob::core::array::assertSameShape(i1, Ex);
  bob::core::array::assertSameShape(m_buffer1, i1);

  // Notation:
  // DK - difference kernel
  // AK - averaging kernel
  // v^T - vector (v) transposed
  // A * B - A convolved with B (A is mirrored)

  // Differentiation along the X direction (extent 1) => Ex matrix
  fastconv(i1, m_diff_kernel, Ex, 1); // Ex =  DK * i1
  fastconv(Ex, m_avg_kernel, m_buffer1, 0); // Buffer1 = AK^T * Ex

  fastconv(i2, m_diff_kernel, Ex, 1); // Ex = DK * i2
  fastconv(Ex, m_avg_kernel, m_buffer2, 0); // Buffer2 = AK^T * Ex

  // The averaging operation along the t coordinate is performed by hand
  Ex = (m_avg_kernel(1) * m_buffer1) + (m_avg_kernel(0) * m_buffer2);

  // Differentiation along the Y direction (extent 0) => Ey matrix
  fastconv(i1, m_diff_kernel, Ey, 0); // Ey =  DK^T * i1
  fastconv(Ey, m_avg_kernel, m_buffer1, 1); // Buffer1 = AK * Ey

  fastconv(i2, m_diff_kernel, Ey, 0); // Ey =  DK^T * i2
  fastconv(Ey, m_avg_kernel, m_buffer2, 1); // Buffer2 = AK * Ey

  // The averaging operation along the t coordinate is performed by hand
  Ey = (m_avg_kernel(1) * m_buffer1) + (m_avg_kernel(0) * m_buffer2);

  // Differentiation along the T direction i1 -> i2 => Et matrix
  fastconv(i1, m_avg_kernel, Et, 1); // Et =  AK * i1
  fastconv(Et, m_avg_kernel, m_buffer1, 0); // Buffer1 = AK^T * Et

  fastconv(i2, m_avg_kernel, Et, 1); // Et =  AK * i2
  fastconv(Et, m_avg_kernel, m_buffer2, 0); // Buffer2 = AK^T * Et

  // The difference operation along the t coordinate is performed by hand
  Et = (m_diff_kernel(1) * m_buffer1) + (m_diff_kernel(0) * m_buffer2);
}

static const double HS_DIFF_KERNEL_DATA[] = {+1/4., -1/4.};
static const blitz::Array<double,1> HS_DIFF_KERNEL(const_cast<double*>(HS_DIFF_KERNEL_DATA), blitz::shape(2), blitz::neverDeleteData);
static const double HS_AVG_KERNEL_DATA[] = {+1., +1.};
static const blitz::Array<double,1> HS_AVG_KERNEL(const_cast<double*>(HS_AVG_KERNEL_DATA), blitz::shape(2), blitz::neverDeleteData);

bob::ip::optflow::HornAndSchunckGradient::HornAndSchunckGradient(const blitz::TinyVector<int,2>& shape):
  bob::ip::optflow::ForwardGradient(HS_DIFF_KERNEL, HS_AVG_KERNEL, shape)
{
}

bob::ip::optflow::HornAndSchunckGradient::~HornAndSchunckGradient() { }

bob::ip::optflow::CentralGradient::CentralGradient(const blitz::Array<double,1>& diff_kernel,
    const blitz::Array<double,1>& avg_kernel,
    const blitz::TinyVector<int,2>& shape) :
  m_diff_kernel(diff_kernel.copy()),
  m_avg_kernel(avg_kernel.copy()),
  m_buffer1(shape),
  m_buffer2(shape),
  m_buffer3(shape)
{
  blitz::TinyVector<int,1> required_shape(3);
  bob::core::array::assertSameShape(m_diff_kernel, required_shape);
  bob::core::array::assertSameShape(m_avg_kernel, required_shape);
}

bob::ip::optflow::CentralGradient::CentralGradient(const bob::ip::optflow::CentralGradient& other) :
  m_diff_kernel(other.m_diff_kernel.copy()),
  m_avg_kernel(other.m_avg_kernel.copy()),
  m_buffer1(other.m_buffer1.shape()),
  m_buffer2(other.m_buffer2.shape()),
  m_buffer3(other.m_buffer3.shape())
{
}

bob::ip::optflow::CentralGradient::~CentralGradient() { }

bob::ip::optflow::CentralGradient& bob::ip::optflow::CentralGradient::operator= (const bob::ip::optflow::CentralGradient& other) {
  m_diff_kernel.reference(other.m_diff_kernel.copy());
  m_avg_kernel.reference(other.m_avg_kernel.copy());
  m_buffer1.resize(other.m_buffer1.shape());
  m_buffer2.resize(other.m_buffer2.shape());
  m_buffer3.resize(other.m_buffer3.shape());
  return *this;
}

void bob::ip::optflow::CentralGradient::setShape(const blitz::TinyVector<int,2>& shape) {
  m_buffer1.resize(shape);
  m_buffer2.resize(shape);
  m_buffer3.resize(shape);
}

void bob::ip::optflow::CentralGradient::setDiffKernel(const blitz::Array<double,1>& k) {
  bob::core::array::assertSameDimensionLength(k.extent(0), 3);
  m_diff_kernel.reference(k.copy());
}

void bob::ip::optflow::CentralGradient::setAvgKernel(const blitz::Array<double,1>& k) {
  bob::core::array::assertSameDimensionLength(k.extent(0), 3);
  m_avg_kernel.reference(k.copy());
}

void bob::ip::optflow::CentralGradient::operator() (const blitz::Array<double,2>& i1,
    const blitz::Array<double,2>& i2, const blitz::Array<double,2>& i3,
    blitz::Array<double,2>& Ex, blitz::Array<double,2>& Ey,
    blitz::Array<double,2>& Et) const {

  // all arrays have to have the same shape
  bob::core::array::assertSameShape(i1, i2);
  bob::core::array::assertSameShape(i2, i3);
  bob::core::array::assertSameShape(Ex, Ey);
  bob::core::array::assertSameShape(Ey, Et);
  bob::core::array::assertSameShape(i1, Ex);
  bob::core::array::assertSameShape(m_buffer1, i1);

  // Notation:
  // DK - difference kernel
  // AK - averaging kernel
  // v^T - vector (v) transposed
  // A * B - A convolved with B (A is mirrored)

  // Differentiation along the X direction (extent 1) => Ex matrix
  fastconv(i1, m_diff_kernel, Ex, 1); // Ex =  DK * i1
  fastconv(Ex, m_avg_kernel, m_buffer1, 0); // Buffer1 = AK^T * Ex

  fastconv(i2, m_diff_kernel, Ex, 1); // Ex = DK * i2
  fastconv(Ex, m_avg_kernel, m_buffer2, 0); // Buffer2 = AK^T * Ex

  fastconv(i3, m_diff_kernel, Ex, 1); // Ex = DK * i3
  fastconv(Ex, m_avg_kernel, m_buffer3, 0); // Buffer3 = AK^T * Ex

  // The averaging operation along the t coordinate is performed by hand
  Ex = (m_avg_kernel(2) * m_buffer1) + (m_avg_kernel(1) * m_buffer2) +
    (m_avg_kernel(0) * m_buffer3);

  // Differentiation along the Y direction (extent 0) => Ey matrix
  fastconv(i1, m_diff_kernel, Ey, 0); // Ey =  DK^T * i1
  fastconv(Ey, m_avg_kernel, m_buffer1, 1); // Buffer1 = AK * Ey

  fastconv(i2, m_diff_kernel, Ey, 0); // Ey =  DK^T * i2
  fastconv(Ey, m_avg_kernel, m_buffer2, 1); // Buffer2 = AK * Ey

  fastconv(i3, m_diff_kernel, Ey, 0); // Ey =  DK^T * i3
  fastconv(Ey, m_avg_kernel, m_buffer3, 1); // Buffer3 = AK * Ey

  // The averaging operation along the t coordinate is performed by hand
  Ey = (m_avg_kernel(2) * m_buffer1) + (m_avg_kernel(1) * m_buffer2) +
    (m_avg_kernel(0) * m_buffer3);

  // Differentiation along the T direction i1 -> i2 => Et matrix
  fastconv(i1, m_avg_kernel, Et, 1); // Et =  AK * i1
  fastconv(Et, m_avg_kernel, m_buffer1, 0); // Buffer1 = AK^T * Et

  fastconv(i2, m_avg_kernel, Et, 1); // Et =  AK * i2
  fastconv(Et, m_avg_kernel, m_buffer2, 0); // Buffer2 = AK^T * Et

  fastconv(i3, m_avg_kernel, Et, 1); // Et =  AK * i3
  fastconv(Et, m_avg_kernel, m_buffer3, 0); // Buffer3 = AK^T * Et

  // The difference operation along the t coordinate is performed by hand
  Et = (m_diff_kernel(2) * m_buffer1) + (m_diff_kernel(1) * m_buffer2) +
    (m_diff_kernel(0) * m_buffer3);
}

static const double SOBEL_DIFF_KERNEL_DATA[] = {+1., 0., -1.};
static const blitz::Array<double,1> SOBEL_DIFF_KERNEL(const_cast<double*>(SOBEL_DIFF_KERNEL_DATA), blitz::shape(3), blitz::neverDeleteData);
static const double SOBEL_AVG_KERNEL_DATA[] = {+1., +2., +1};
static const blitz::Array<double,1> SOBEL_AVG_KERNEL(const_cast<double*>(SOBEL_AVG_KERNEL_DATA), blitz::shape(3), blitz::neverDeleteData);

bob::ip::optflow::SobelGradient::SobelGradient(const blitz::TinyVector<int,2>& shape):
  bob::ip::optflow::CentralGradient(SOBEL_DIFF_KERNEL, SOBEL_AVG_KERNEL, shape)
{
}

bob::ip::optflow::SobelGradient::~SobelGradient() { }

static const double PREWITT_DIFF_KERNEL_DATA[] = {+1., 0., -1.};
static const blitz::Array<double,1> PREWITT_DIFF_KERNEL(const_cast<double*>(PREWITT_DIFF_KERNEL_DATA), blitz::shape(3), blitz::neverDeleteData);
static const double PREWITT_AVG_KERNEL_DATA[] = {+1., +1., +1};
static const blitz::Array<double,1> PREWITT_AVG_KERNEL(const_cast<double*>(PREWITT_AVG_KERNEL_DATA), blitz::shape(3), blitz::neverDeleteData);

bob::ip::optflow::PrewittGradient::PrewittGradient(const blitz::TinyVector<int,2>& shape):
  bob::ip::optflow::CentralGradient(PREWITT_DIFF_KERNEL, PREWITT_AVG_KERNEL, shape)
{
}

bob::ip::optflow::PrewittGradient::~PrewittGradient() { }

static const double ISOTROPIC_DIFF_KERNEL_DATA[] = {+1., 0., -1.};
static const blitz::Array<double,1> ISOTROPIC_DIFF_KERNEL(const_cast<double*>(ISOTROPIC_DIFF_KERNEL_DATA), blitz::shape(3), blitz::neverDeleteData);
static const double ISOTROPIC_AVG_KERNEL_DATA[] = {+1., std::sqrt(2.), +1};
static const blitz::Array<double,1> ISOTROPIC_AVG_KERNEL(const_cast<double*>(ISOTROPIC_AVG_KERNEL_DATA), blitz::shape(3), blitz::neverDeleteData);

bob::ip::optflow::IsotropicGradient::IsotropicGradient(const blitz::TinyVector<int,2>& shape):
  bob::ip::optflow::CentralGradient(ISOTROPIC_DIFF_KERNEL, ISOTROPIC_AVG_KERNEL, shape)
{
}

bob::ip::optflow::IsotropicGradient::~IsotropicGradient() { }
