.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Sat 16 Nov 20:52:58 2013

=============
 Users Guide
=============

To estimate the classical Optical Flow using the original technique proposed by Horn & Schunck, use the functor :py:class:`bob.ip.optflow.hornschunck.VanillaFlow`.
In the following example, we assume you provide a pair of gray-scaled images ``i1`` and ``i2``, represented using a 2D :py:class:`numpy.ndarray` containing ``numpy.float64`` elements:

.. testsetup:: vanilla

   from bob.ip.optflow.hornschunck.test_gradient import make_image_pair_2
   i1, i2 = make_image_pair_2()

.. doctest:: vanilla
  :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

   >>> import bob.ip.optflow.hornschunck
   >>> flow = bob.ip.optflow.hornschunck.VanillaFlow(i1.shape)
   >>> u, v = flow.estimate(alpha=200, iterations=20, image1=i1, image2=i2)
   >>> print(u)
   [[...]]
   >>> print(v)
   [[...]]

If you'd like to estimate the flow for an image, given a triplet, then use the :py:class:`bob.ip.optflow.hornschunck.Flow` instead:

.. testsetup:: sobel

   from bob.ip.optflow.hornschunck.test_flow import make_image_tripplet
   i1, i2, i3 = make_image_tripplet()

.. doctest:: sobel
  :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

   >>> import bob.ip.optflow.hornschunck
   >>> flow  = bob.ip.optflow.hornschunck.Flow(i1.shape)
   >>> u, v = flow.estimate(200, 20, i1, i2, i3)
   >>> print(u)
   [[...]]
   >>> print(v)
   [[...]]

