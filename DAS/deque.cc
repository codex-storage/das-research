
#include <deque>

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

using std::deque;

struct DequeInt {
  deque<int16_t> d;
  DequeInt() {}
  void push(int e) { d.push_back(e); }
  int pop() {
    auto ret = d.front();
    d.pop_front();
    return ret;
  }
  bool empty() {return d.empty();}
  bool notEmpty() {return not d.empty();}
};

PYBIND11_MODULE(deque, m) {
  // m.doc() = "STL based deque"; // optional module docstring
  py::class_<DequeInt>(m, "DequeInt")
    .def(py::init<>())
    .def("append", &DequeInt::push)
    .def("popleft", &DequeInt::pop)
    .def("empty", &DequeInt::empty)
    .def("__bool__", &DequeInt::notEmpty);
}
