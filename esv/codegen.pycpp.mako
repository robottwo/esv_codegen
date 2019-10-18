/*
 * This file was codegened from codegen.pycpp.mako.
 *
 */
#include "${name.lower()}.hpp"

#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
using namespace boost::python;

void export_${name.lower()}()
{
    class_<${name}>("${name}")
% for field, ctype in dtype:
        .def_readwrite("${field}", &${name}::${field})
% endfor
    ;

    // Convert from vector<${name}> to Python lists automatically.
    class_<std::vector<${name}> >("${name}List")
        .def(vector_indexing_suite<std::vector<${name}> >() );


    class_<${name}Collection>("${name}sCollection")
% for field, ctype in dtype:
% if field in keys:
        .def("get_by_${field}", &${name}Collection::get_by_${field}, (boost::python::arg("${field}")),"Retrieve a single ${name}.")
% else:
        .def("find_by_${field}", &${name}Collection::find_by_${field}, (boost::python::arg("${field}")), "Retrieve a list of ${name}s.")
% endif
% endfor
    ;
}
