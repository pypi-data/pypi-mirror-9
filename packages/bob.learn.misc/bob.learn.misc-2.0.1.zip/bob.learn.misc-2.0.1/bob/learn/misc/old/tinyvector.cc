/**
 * @author André Anjos <andre.anjos@idiap.ch>
 * @date Tue Jan 18 17:07:26 2011 +0100
 *
 * @brief Automatic converters to-from python for blitz::TinyVectors
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <boost/python.hpp>
#include <boost/format.hpp>
#include <blitz/tinyvec2.h>

/**
 * Objects of this type create a binding between blitz::TinyVector<T,N> and
 * python iterables. You can specify a python iterable as a parameter to a
 * bound method that would normally receive a TinyVector<T,N> or a const
 * TinyVector<T,N>& and the conversion will just magically happen.
 */
template <typename T, int N>
struct tinyvec_from_sequence {
  typedef typename blitz::TinyVector<T,N> container_type;

  /**
   * Registers converter from any python sequence into a blitz::TinyVector<T,N>
   */
  tinyvec_from_sequence() {
    boost::python::converter::registry::push_back(&convertible, &construct,
        boost::python::type_id<container_type>());
  }

  /**
   * This method will determine if the input python object is convertible into
   * a TinyVector<T,N>
   *
   * Conditions:
   * - The input object has to have N elements.
   * - The input object has to be iterable.
   * - All elements in the input object have to be convertible to T objects
   */
  static void* convertible(PyObject* obj_ptr) {

    /**
     * this bit will check if the input obj is one of the expected input types
     * It will return 0 if the element in question is neither:
     * - a list
     * - a tuple
     * - an iterable
     * - a range
     * - is not a string _and_ is not an unicode string _and_
     *   (is a valid object pointer _or_ (too long to continue... ;-)
     */
    if (!(PyList_Check(obj_ptr)
          || PyTuple_Check(obj_ptr)
          || PyIter_Check(obj_ptr)
          || PyRange_Check(obj_ptr)
          || (
#if PY_VERSION_HEX < 0x03000000
               !PyString_Check(obj_ptr)
#else
               !PyBytes_Check(obj_ptr)
#endif
            && !PyUnicode_Check(obj_ptr)
            && ( Py_TYPE(obj_ptr) == 0
              || Py_TYPE(Py_TYPE(obj_ptr)) == 0
              || Py_TYPE(Py_TYPE(obj_ptr))->tp_name == 0
              || std::strcmp(
                 Py_TYPE(Py_TYPE(obj_ptr))->tp_name, "Boost.Python.class") != 0)
            && PyObject_HasAttrString(obj_ptr, "__len__")
            && PyObject_HasAttrString(obj_ptr, "__getitem__")))) return 0;

    //this bit will check if we have exactly N
    if(PyObject_Length(obj_ptr) != N) {
      PyErr_Clear();
      return 0;
    }

    //this bit will make sure we can extract an interator from the object
    boost::python::handle<> obj_iter(
        boost::python::allow_null(PyObject_GetIter(obj_ptr)));
    if (!obj_iter.get()) { // must be convertible to an iterator
      PyErr_Clear();
      return 0;
    }

    //this bit will check every element for convertibility into "T"
    bool is_range = PyRange_Check(obj_ptr);
    std::size_t i=0;
    for(;;++i) { //if everything ok, should leave for loop with i == N
      boost::python::handle<> py_elem_hdl(
          boost::python::allow_null(PyIter_Next(obj_iter.get())));
      if (PyErr_Occurred()) {
        PyErr_Clear();
        return 0;
      }
      if (!py_elem_hdl.get()) break; // end of iteration
      boost::python::object py_elem_obj(py_elem_hdl);
      boost::python::extract<T> elem_proxy(py_elem_obj);
      if (!elem_proxy.check()) return 0;
      if (is_range) break; // in a range all elements are of the same type
    }
    if (!is_range) assert(i == N);

    return obj_ptr;
  }

  /**
   * This method will finally construct the C++ element out of the python
   * object that was input. Please note that when boost::python reaches this
   * method, the object has already been checked for convertibility.
   */
  static void construct(PyObject* obj_ptr,
      boost::python::converter::rvalue_from_python_stage1_data* data) {
    boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
    void* storage = ((boost::python::converter::rvalue_from_python_storage<container_type>*)data)->storage.bytes;
    new (storage) container_type();
    data->convertible = storage;
    container_type& result = *((container_type*)storage);
    std::size_t i=0;
    for(;;++i) {
      boost::python::handle<> py_elem_hdl(
          boost::python::allow_null(PyIter_Next(obj_iter.get())));
      if (PyErr_Occurred()) boost::python::throw_error_already_set();
      if (!py_elem_hdl.get()) break; // end of iteration
      boost::python::object py_elem_obj(py_elem_hdl);
      typename boost::python::extract<T> elem_proxy(py_elem_obj);
      result[i] = elem_proxy();
    }
    if (i != N) {
      boost::format s("expected %d elements for TinyVector<T,%d>, got %d");
      s % N % N % i;
      PyErr_SetString(PyExc_RuntimeError, s.str().c_str());
      boost::python::throw_error_already_set();
    }
  }

};

/**
 * Objects of this type bind TinyVector<T,N> to python tuples. Your method
 * generates as output an object of this type and the object will be
 * automatically converted into a python tuple.
 */
template <typename T, int N>
struct tinyvec_to_tuple {
  typedef typename blitz::TinyVector<T,N> container_type;

  static PyObject* convert(const container_type& tv) {
    boost::python::list result;
    typedef typename container_type::const_iterator const_iter;
    for(const_iter p=tv.begin();p!=tv.end();++p) {
      result.append(boost::python::object(*p));
    }
    return boost::python::incref(boost::python::tuple(result).ptr());
  }

  static const PyTypeObject* get_pytype() { return &PyTuple_Type; }

};

template <typename T, int N>
void register_tinyvec_to_tuple() {
  boost::python::to_python_converter<typename blitz::TinyVector<T,N>,
                          tinyvec_to_tuple<T,N>
#if defined BOOST_PYTHON_SUPPORTS_PY_SIGNATURES
                          ,true
#endif
              >();
}

void bind_core_tinyvector () {

  /**
   * The following struct constructors will make sure we can input
   * blitz::TinyVector<T,N> in our bound C++ routines w/o needing to specify
   * special converters each time. The rvalue converters allow boost::python to
   * automatically map the following inputs:
   *
   * a) const blitz::TinyVector<T,N>& (pass by const reference)
   * b) blitz::TinyVector<T,N> (pass by value)
   *
   * Please note that the last case:
   *
   * c) blitz::TinyVector<T,N>& (pass by non-const reference)
   *
   * is NOT covered by these converters. The reason being that because the
   * object may be changed, there is no way for boost::python to update the
   * original python object, in a sensible manner, at the return of the method.
   *
   * Avoid passing by non-const reference in your methods.
   */
  tinyvec_from_sequence<int,1>();
  tinyvec_from_sequence<int,2>();
  tinyvec_from_sequence<int,3>();
  tinyvec_from_sequence<int,4>();
  tinyvec_from_sequence<int,5>();
  tinyvec_from_sequence<int,6>();
  tinyvec_from_sequence<int,7>();
  tinyvec_from_sequence<int,8>();
  tinyvec_from_sequence<int,9>();
  tinyvec_from_sequence<int,10>();
  tinyvec_from_sequence<int,11>();
  tinyvec_from_sequence<uint64_t,1>();
  tinyvec_from_sequence<uint64_t,2>();
  tinyvec_from_sequence<uint64_t,3>();
  tinyvec_from_sequence<uint64_t,4>();
  tinyvec_from_sequence<uint64_t,5>();
  tinyvec_from_sequence<uint64_t,6>();
  tinyvec_from_sequence<uint64_t,7>();
  tinyvec_from_sequence<uint64_t,8>();
  tinyvec_from_sequence<uint64_t,9>();
  tinyvec_from_sequence<uint64_t,10>();
  tinyvec_from_sequence<uint64_t,11>();
  tinyvec_from_sequence<double,1>();
  tinyvec_from_sequence<double,2>();
  tinyvec_from_sequence<double,3>();
  tinyvec_from_sequence<double,4>();
  tinyvec_from_sequence<double,5>();
  tinyvec_from_sequence<double,6>();
  tinyvec_from_sequence<double,7>();
  tinyvec_from_sequence<double,8>();
  tinyvec_from_sequence<double,9>();
  tinyvec_from_sequence<double,10>();
  tinyvec_from_sequence<double,11>();
  if (typeid(int) != typeid(blitz::diffType)) {
    tinyvec_from_sequence<blitz::diffType,1>();
    tinyvec_from_sequence<blitz::diffType,2>();
    tinyvec_from_sequence<blitz::diffType,3>();
    tinyvec_from_sequence<blitz::diffType,4>();
    tinyvec_from_sequence<blitz::diffType,5>();
    tinyvec_from_sequence<blitz::diffType,6>();
    tinyvec_from_sequence<blitz::diffType,7>();
    tinyvec_from_sequence<blitz::diffType,8>();
    tinyvec_from_sequence<blitz::diffType,9>();
    tinyvec_from_sequence<blitz::diffType,10>();
    tinyvec_from_sequence<blitz::diffType,11>();
  }

  /**
   * The following struct constructors will make C++ return values of type
   * blitz::TinyVector<T,N> to show up in the python side as tuples.
   */
  register_tinyvec_to_tuple<int,1>();
  register_tinyvec_to_tuple<int,2>();
  register_tinyvec_to_tuple<int,3>();
  register_tinyvec_to_tuple<int,4>();
  register_tinyvec_to_tuple<int,5>();
  register_tinyvec_to_tuple<int,6>();
  register_tinyvec_to_tuple<int,7>();
  register_tinyvec_to_tuple<int,8>();
  register_tinyvec_to_tuple<int,9>();
  register_tinyvec_to_tuple<int,10>();
  register_tinyvec_to_tuple<int,11>();
  register_tinyvec_to_tuple<uint64_t,1>();
  register_tinyvec_to_tuple<uint64_t,2>();
  register_tinyvec_to_tuple<uint64_t,3>();
  register_tinyvec_to_tuple<uint64_t,4>();
  register_tinyvec_to_tuple<uint64_t,5>();
  register_tinyvec_to_tuple<uint64_t,6>();
  register_tinyvec_to_tuple<uint64_t,7>();
  register_tinyvec_to_tuple<uint64_t,8>();
  register_tinyvec_to_tuple<uint64_t,9>();
  register_tinyvec_to_tuple<uint64_t,10>();
  register_tinyvec_to_tuple<uint64_t,11>();
  register_tinyvec_to_tuple<double,1>();
  register_tinyvec_to_tuple<double,2>();
  register_tinyvec_to_tuple<double,3>();
  register_tinyvec_to_tuple<double,4>();
  register_tinyvec_to_tuple<double,5>();
  register_tinyvec_to_tuple<double,6>();
  register_tinyvec_to_tuple<double,7>();
  register_tinyvec_to_tuple<double,8>();
  register_tinyvec_to_tuple<double,9>();
  register_tinyvec_to_tuple<double,10>();
  register_tinyvec_to_tuple<double,11>();
  if (typeid(int) != typeid(blitz::diffType)) {
    register_tinyvec_to_tuple<blitz::diffType,1>();
    register_tinyvec_to_tuple<blitz::diffType,2>();
    register_tinyvec_to_tuple<blitz::diffType,3>();
    register_tinyvec_to_tuple<blitz::diffType,4>();
    register_tinyvec_to_tuple<blitz::diffType,5>();
    register_tinyvec_to_tuple<blitz::diffType,6>();
    register_tinyvec_to_tuple<blitz::diffType,7>();
    register_tinyvec_to_tuple<blitz::diffType,8>();
    register_tinyvec_to_tuple<blitz::diffType,9>();
    register_tinyvec_to_tuple<blitz::diffType,10>();
    register_tinyvec_to_tuple<blitz::diffType,11>();
  }

}
