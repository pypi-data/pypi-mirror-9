// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

%module(package="gphoto2") gphoto2_port_info_list

%{
#include "gphoto2/gphoto2.h"
%}

%import "gphoto2_port.i"

%feature("autodoc", "2");

%ignore gp_port_info_get_library_filename;
%ignore gp_port_info_set_library_filename;

%include "typemaps.i"

%include "macros.i"

IMPORT_GPHOTO2_ERROR()

%rename(PortInfoList) _GPPortInfoList;
%typemap(doc) GPPortInfoList * "$1_name: PortInfoList *";

// gp_port_info_list_new() returns a pointer in an output parameter
PLAIN_ARGOUT(GPPortInfoList **)

// In libgphoto2 version 2.4 GPPortInfo is a structure, in version 2.5 it's a
// pointer to a structure.
#ifdef GPHOTO2_24
CALLOC_ARGOUT(GPPortInfo *)
#else
%typemap(in, numinputs=0) GPPortInfo * (GPPortInfo temp) {
  $1 = &temp;
}
%typemap(argout) GPPortInfo * {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__GPPortInfo, 0));
}
#endif

// several getter functions return string pointers in output params
STRING_ARGOUT()

// Add default constructor and destructor to _GPPortInfoList
struct _GPPortInfoList {};
DEFAULT_CTOR(_GPPortInfoList, gp_port_info_list_new)
DEFAULT_DTOR(_GPPortInfoList, gp_port_info_list_free)
%ignore _GPPortInfoList;

// Make GPPortInfoList more like a Python list
LEN_MEMBER_FUNCTION(_GPPortInfoList, PortInfoList, gp_port_info_list_count)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_item",   functype="ssizeargfunc") _GPPortInfoList::__getitem__;
#endif
%exception __getitem__ {
  $action
  if (PyErr_Occurred() != NULL) {
    goto fail;
  }
}
%extend _GPPortInfoList {
  void __getitem__(int idx, GPPortInfo *info) {
    if (idx < 0 || idx >= gp_port_info_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "GPPortInfoList index out of range");
      return;
    }
    {
      int error = gp_port_info_list_get_info($self, idx, info);
      if (error < GP_OK) {
        GPHOTO2_ERROR(error)
        return;
      }
    }
  }
};

// Add member methods to _GPPortInfoList
MEMBER_FUNCTION(_GPPortInfoList, PortInfoList,
    append, (GPPortInfo info),
    gp_port_info_list_append, ($self, info))
MEMBER_FUNCTION(_GPPortInfoList, PortInfoList,
    load, (),
    gp_port_info_list_load, ($self))
INT_MEMBER_FUNCTION(_GPPortInfoList, PortInfoList,
    count, (),
    gp_port_info_list_count, ($self))
INT_MEMBER_FUNCTION(_GPPortInfoList, PortInfoList,
    lookup_path, (const char *path),
    gp_port_info_list_lookup_path, ($self, path))
INT_MEMBER_FUNCTION(_GPPortInfoList, PortInfoList,
    lookup_name, (const char *name),
    gp_port_info_list_lookup_name, ($self, name))
MEMBER_FUNCTION(_GPPortInfoList, PortInfoList,
    get_info, (const int n, GPPortInfo *info),
    gp_port_info_list_get_info, ($self, n, info))

// Don't wrap internal functions
%ignore gp_port_info_new;
%ignore gp_port_info_set_name;
%ignore gp_port_info_set_path;
%ignore gp_port_info_set_type;

%include "gphoto2/gphoto2-port-info-list.h"
