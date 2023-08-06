#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <Python.h>
#include "sass_context.h"

#if PY_MAJOR_VERSION >= 3
#define PySass_IF_PY3(three, two) (three)
#define PySass_Int_FromLong(v) PyLong_FromLong(v)
#define PySass_Bytes_Check(o) PyBytes_Check(o)
#define PySass_Bytes_GET_SIZE(o) PyBytes_GET_SIZE(o)
#define PySass_Bytes_AS_STRING(o) PyBytes_AS_STRING(o)
#define PySass_Object_Bytes(o) PyUnicode_AsUTF8String(PyObject_Str(o))
#else
#define PySass_IF_PY3(three, two) (two)
#define PySass_Int_FromLong(v) PyInt_FromLong(v)
#define PySass_Bytes_Check(o) PyString_Check(o)
#define PySass_Bytes_GET_SIZE(o) PyString_GET_SIZE(o)
#define PySass_Bytes_AS_STRING(o) PyString_AS_STRING(o)
#define PySass_Object_Bytes(o) PyObject_Str(o)
#endif

#ifdef __cplusplus
extern "C" {
#endif

static PyObject* _to_py_value(const union Sass_Value* value);
static union Sass_Value* _to_sass_value(PyObject* value);

static union Sass_Value* _color_to_sass_value(PyObject* value);
static union Sass_Value* _number_to_sass_value(PyObject* value);
static union Sass_Value* _list_to_sass_value(PyObject* value);
static union Sass_Value* _mapping_to_sass_value(PyObject* value);
static union Sass_Value* _unicode_to_sass_value(PyObject* value);
static union Sass_Value* _warning_to_sass_value(PyObject* value);
static union Sass_Value* _error_to_sass_value(PyObject* value);
static union Sass_Value* _unknown_type_to_sass_error(PyObject* value);
static union Sass_Value* _exception_to_sass_error();

struct PySass_Pair {
    char *label;
    int value;
};

static struct PySass_Pair PySass_output_style_enum[] = {
    {(char *) "nested", SASS_STYLE_NESTED},
    {(char *) "expanded", SASS_STYLE_EXPANDED},
    {(char *) "compact", SASS_STYLE_COMPACT},
    {(char *) "compressed", SASS_STYLE_COMPRESSED},
    {NULL}
};

static PyObject* _to_py_value(const union Sass_Value* value) {
    PyObject* retv = NULL;
    PyObject* types_mod = PyImport_ImportModule("sass");
    PyObject* sass_comma = PyObject_GetAttrString(types_mod, "SASS_SEPARATOR_COMMA");
    PyObject* sass_space = PyObject_GetAttrString(types_mod, "SASS_SEPARATOR_SPACE");

    switch (sass_value_get_tag(value)) {
        case SASS_NULL:
            retv = Py_None;
            Py_INCREF(retv);
            break;
        case SASS_BOOLEAN:
            retv = PyBool_FromLong(sass_boolean_get_value(value));
            break;
        case SASS_STRING:
            retv = PyUnicode_FromString(sass_string_get_value(value));
            break;
        case SASS_NUMBER:
            retv = PyObject_CallMethod(
                types_mod,
                "SassNumber",
                PySass_IF_PY3("dy", "ds"),
                sass_number_get_value(value),
                sass_number_get_unit(value)
            );
            break;
        case SASS_COLOR:
            retv = PyObject_CallMethod(
                types_mod,
                "SassColor",
                "dddd",
                sass_color_get_r(value),
                sass_color_get_g(value),
                sass_color_get_b(value),
                sass_color_get_a(value)
            );
            break;
        case SASS_LIST: {
            size_t i = 0;
            PyObject* items = PyTuple_New(sass_list_get_length(value));
            PyObject* separator = sass_comma;
            switch (sass_list_get_separator(value)) {
                case SASS_COMMA:
                    separator = sass_comma;
                    break;
                case SASS_SPACE:
                    separator = sass_space;
                    break;
            }
            for (i = 0; i < sass_list_get_length(value); i += 1) {
                PyTuple_SetItem(
                    items,
                    i,
                    _to_py_value(sass_list_get_value(value, i))
                );
            }
            retv = PyObject_CallMethod(
                types_mod, "SassList", "OO", items, separator
            );
            break;
        }
        case SASS_MAP: {
            size_t i = 0;
            PyObject* items = PyTuple_New(sass_map_get_length(value));
            for (i = 0; i < sass_map_get_length(value); i += 1) {
                PyObject* kvp = PyTuple_New(2);
                PyTuple_SetItem(
                    kvp, 0, _to_py_value(sass_map_get_key(value, i))
                );
                PyTuple_SetItem(
                    kvp, 1, _to_py_value(sass_map_get_value(value, i))
                );
                PyTuple_SetItem(items, i, kvp);
            }
            retv = PyObject_CallMethod(types_mod, "SassMap", "(O)", items);
            Py_DECREF(items);
            break;
        }
        case SASS_ERROR:
        case SASS_WARNING:
            /* @warning and @error cannot be passed */
            break;
    }

    if (retv == NULL) {
        PyErr_SetString(PyExc_TypeError, "Unexpected sass type");
    }

    Py_DECREF(types_mod);
    Py_DECREF(sass_comma);
    Py_DECREF(sass_space);
    return retv;
}

static union Sass_Value* _color_to_sass_value(PyObject* value) {
    union Sass_Value* retv = NULL;
    PyObject* r_value = PyObject_GetAttrString(value, "r");
    PyObject* g_value = PyObject_GetAttrString(value, "g");
    PyObject* b_value = PyObject_GetAttrString(value, "b");
    PyObject* a_value = PyObject_GetAttrString(value, "a");
    retv = sass_make_color(
        PyFloat_AsDouble(r_value),
        PyFloat_AsDouble(g_value),
        PyFloat_AsDouble(b_value),
        PyFloat_AsDouble(a_value)
    );
    Py_DECREF(r_value);
    Py_DECREF(g_value);
    Py_DECREF(b_value);
    Py_DECREF(a_value);
    return retv;
}

static union Sass_Value* _list_to_sass_value(PyObject* value) {
    PyObject* types_mod = PyImport_ImportModule("sass");
    PyObject* sass_comma = PyObject_GetAttrString(types_mod, "SASS_SEPARATOR_COMMA");
    PyObject* sass_space = PyObject_GetAttrString(types_mod, "SASS_SEPARATOR_SPACE");
    union Sass_Value* retv = NULL;
    Py_ssize_t i = 0;
    PyObject* items = PyObject_GetAttrString(value, "items");
    PyObject* separator = PyObject_GetAttrString(value, "separator");
    Sass_Separator sep = SASS_COMMA;
    if (separator == sass_comma) {
        sep = SASS_COMMA;
    } else if (separator == sass_space) {
        sep = SASS_SPACE;
    } else {
        assert(0);
    }
    retv = sass_make_list(PyTuple_Size(items), sep);
    for (i = 0; i < PyTuple_Size(items); i += 1) {
        sass_list_set_value(
            retv, i, _to_sass_value(PyTuple_GET_ITEM(items, i))
        );
    }
    Py_DECREF(types_mod);
    Py_DECREF(sass_comma);
    Py_DECREF(sass_space);
    Py_DECREF(items);
    Py_DECREF(separator);
    return retv;
}

static union Sass_Value* _mapping_to_sass_value(PyObject* value) {
    union Sass_Value* retv = NULL;
    size_t i = 0;
    Py_ssize_t pos = 0;
    PyObject* d_key = NULL;
    PyObject* d_value = NULL;
    PyObject* dct = PyDict_New();
    PyDict_Update(dct, value);
    retv = sass_make_map(PyDict_Size(dct));
    while (PyDict_Next(dct, &pos, &d_key, &d_value)) {
        sass_map_set_key(retv, i, _to_sass_value(d_key));
        sass_map_set_value(retv, i, _to_sass_value(d_value));
        i += 1;
    }
    Py_DECREF(dct);
    return retv;
}

static union Sass_Value* _number_to_sass_value(PyObject* value) {
    union Sass_Value* retv = NULL;
    PyObject* d_value = PyObject_GetAttrString(value, "value");
    PyObject* unit = PyObject_GetAttrString(value, "unit");
    PyObject* bytes = PyUnicode_AsEncodedString(unit, "UTF-8", "strict");
    retv = sass_make_number(
        PyFloat_AsDouble(d_value), PySass_Bytes_AS_STRING(bytes)
    );
    Py_DECREF(d_value);
    Py_DECREF(unit);
    Py_DECREF(bytes);
    return retv;
}

static union Sass_Value* _unicode_to_sass_value(PyObject* value) {
    union Sass_Value* retv = NULL;
    PyObject* bytes = PyUnicode_AsEncodedString(value, "UTF-8", "strict");
    retv = sass_make_string(PySass_Bytes_AS_STRING(bytes));
    Py_DECREF(bytes);
    return retv;
}

static union Sass_Value* _warning_to_sass_value(PyObject* value) {
    union Sass_Value* retv = NULL;
    PyObject* msg = PyObject_GetAttrString(value, "msg");
    PyObject* bytes = PyUnicode_AsEncodedString(msg, "UTF-8", "strict");
    retv = sass_make_warning(PySass_Bytes_AS_STRING(bytes));
    Py_DECREF(msg);
    Py_DECREF(bytes);
    return retv;
}

static union Sass_Value* _error_to_sass_value(PyObject* value) {
    union Sass_Value* retv = NULL;
    PyObject* msg = PyObject_GetAttrString(value, "msg");
    PyObject* bytes = PyUnicode_AsEncodedString(msg, "UTF-8", "strict");
    retv = sass_make_error(PySass_Bytes_AS_STRING(bytes));
    Py_DECREF(msg);
    Py_DECREF(bytes);
    return retv;
}

static union Sass_Value* _unknown_type_to_sass_error(PyObject* value) {
    union Sass_Value* retv = NULL;
    PyObject* type = PyObject_Type(value);
    PyObject* type_name = PyObject_GetAttrString(type, "__name__");
    PyObject* fmt = PyUnicode_FromString(
        "Unexpected type: `{0}`.\n"
        "Expected one of:\n"
        "- None\n"
        "- bool\n"
        "- str\n"
        "- SassNumber\n"
        "- SassColor\n"
        "- SassList\n"
        "- dict\n"
        "- SassMap\n"
        "- SassWarning\n"
        "- SassError\n"
    );
    PyObject* format_meth = PyObject_GetAttrString(fmt, "format");
    PyObject* result = PyObject_CallFunctionObjArgs(
        format_meth, type_name, NULL
    );
    PyObject* bytes = PyUnicode_AsEncodedString(result, "UTF-8", "strict");
    retv = sass_make_error(PySass_Bytes_AS_STRING(bytes));
    Py_DECREF(type);
    Py_DECREF(type_name);
    Py_DECREF(fmt);
    Py_DECREF(format_meth);
    Py_DECREF(result);
    Py_DECREF(bytes);
    return retv;
}

static union Sass_Value* _exception_to_sass_error() {
    union Sass_Value* retv = NULL;
    PyObject* etype = NULL;
    PyObject* evalue = NULL;
    PyObject* etb = NULL;
    PyErr_Fetch(&etype, &evalue, &etb);
    {
        PyObject* traceback_mod = PyImport_ImportModule("traceback");
        PyObject* traceback_parts = PyObject_CallMethod(
            traceback_mod, "format_exception", "OOO", etype, evalue, etb
        );
        PyList_Insert(traceback_parts, 0, PyUnicode_FromString("\n"));
        PyObject* joinstr = PyUnicode_FromString("");
        PyObject* result = PyUnicode_Join(joinstr, traceback_parts);
        PyObject* bytes = PyUnicode_AsEncodedString(
            result, "UTF-8", "strict"
        );
        retv = sass_make_error(PySass_Bytes_AS_STRING(bytes));
        Py_DECREF(traceback_mod);
        Py_DECREF(traceback_parts);
        Py_DECREF(joinstr);
        Py_DECREF(result);
        Py_DECREF(bytes);
    }
    return retv;
}

static union Sass_Value* _to_sass_value(PyObject* value) {
    union Sass_Value* retv = NULL;
    PyObject* types_mod = PyImport_ImportModule("sass");
    PyObject* sass_number_t = PyObject_GetAttrString(types_mod, "SassNumber");
    PyObject* sass_color_t = PyObject_GetAttrString(types_mod, "SassColor");
    PyObject* sass_list_t = PyObject_GetAttrString(types_mod, "SassList");
    PyObject* sass_warning_t = PyObject_GetAttrString(types_mod, "SassWarning");
    PyObject* sass_error_t = PyObject_GetAttrString(types_mod, "SassError");
    PyObject* collections_mod = PyImport_ImportModule("collections");
    PyObject* mapping_t = PyObject_GetAttrString(collections_mod, "Mapping");

    if (value == Py_None) {
        retv = sass_make_null();
    } else if (PyBool_Check(value)) {
        retv = sass_make_boolean(value == Py_True);
    } else if (PyUnicode_Check(value)) {
        retv = _unicode_to_sass_value(value);
    } else if (PySass_Bytes_Check(value)) {
        retv = sass_make_string(PySass_Bytes_AS_STRING(value));
    /* XXX: PyMapping_Check returns true for lists and tuples in python3 :( */
    /* XXX: pypy derps on dicts: https://bitbucket.org/pypy/pypy/issue/1970 */
    } else if (PyDict_Check(value) || PyObject_IsInstance(value, mapping_t)) {
        retv = _mapping_to_sass_value(value);
    } else if (PyObject_IsInstance(value, sass_number_t)) {
        retv = _number_to_sass_value(value);
    } else if (PyObject_IsInstance(value, sass_color_t)) {
        retv = _color_to_sass_value(value);
    } else if (PyObject_IsInstance(value, sass_list_t)) {
        retv = _list_to_sass_value(value);
    } else if (PyObject_IsInstance(value, sass_warning_t)) {
        retv = _warning_to_sass_value(value);
    } else if (PyObject_IsInstance(value, sass_error_t)) {
        retv = _error_to_sass_value(value);
    }

    if (retv == NULL) {
        retv = _unknown_type_to_sass_error(value);
    }

    Py_DECREF(types_mod);
    Py_DECREF(sass_number_t);
    Py_DECREF(sass_color_t);
    Py_DECREF(sass_list_t);
    Py_DECREF(sass_warning_t);
    Py_DECREF(sass_error_t);
    Py_DECREF(collections_mod);
    Py_DECREF(mapping_t);
    return retv;
}

static union Sass_Value* _call_py_f(
        const union Sass_Value* sass_args, void* cookie
) {
    size_t i;
    PyObject* pyfunc = (PyObject*)cookie;
    PyObject* py_args = PyTuple_New(sass_list_get_length(sass_args));
    PyObject* py_result = NULL;
    union Sass_Value* sass_result = NULL;

    for (i = 0; i < sass_list_get_length(sass_args); i += 1) {
        const union Sass_Value* sass_arg = sass_list_get_value(sass_args, i);
        PyObject* py_arg = NULL;
        if (!(py_arg = _to_py_value(sass_arg))) goto done;
        PyTuple_SetItem(py_args, i, py_arg);
    }

    if (!(py_result = PyObject_CallObject(pyfunc, py_args))) goto done;
    sass_result = _to_sass_value(py_result);

done:
    if (sass_result == NULL) {
        sass_result = _exception_to_sass_error();
    }
    Py_XDECREF(py_args);
    Py_XDECREF(py_result);
    return sass_result;
}


static void _add_custom_functions(
        struct Sass_Options* options, PyObject* custom_functions
) {
    Py_ssize_t i;
    Sass_C_Function_List fn_list = sass_make_function_list(
        PyList_Size(custom_functions)
    );
    for (i = 0; i < PyList_GET_SIZE(custom_functions); i += 1) {
        PyObject* sass_function = PyList_GET_ITEM(custom_functions, i);
        PyObject* signature = PySass_Object_Bytes(sass_function);
        Sass_C_Function_Callback fn = sass_make_function(
            PySass_Bytes_AS_STRING(signature),
            _call_py_f,
            sass_function
        );
        sass_function_set_list_entry(fn_list, i, fn);
    }
    sass_option_set_c_functions(options, fn_list);
}

static PyObject *
PySass_compile_string(PyObject *self, PyObject *args) {
    struct Sass_Context *ctx;
    struct Sass_Data_Context *context;
    struct Sass_Options *options;
    char *string, *include_paths, *image_path;
    const char *error_message, *output_string;
    Sass_Output_Style output_style;
    int source_comments, error_status, precision;
    PyObject *custom_functions;
    PyObject *result;

    if (!PyArg_ParseTuple(args,
                          PySass_IF_PY3("yiiyyiO", "siissiO"),
                          &string, &output_style, &source_comments,
                          &include_paths, &image_path, &precision,
                          &custom_functions)) {
        return NULL;
    }

    context = sass_make_data_context(string);
    options = sass_data_context_get_options(context);
    sass_option_set_output_style(options, output_style);
    sass_option_set_source_comments(options, source_comments);
    sass_option_set_include_path(options, include_paths);
    sass_option_set_image_path(options, image_path);
    sass_option_set_precision(options, precision);
    _add_custom_functions(options, custom_functions);

    sass_compile_data_context(context);

    ctx = sass_data_context_get_context(context);
    error_status = sass_context_get_error_status(ctx);
    error_message = sass_context_get_error_message(ctx);
    output_string = sass_context_get_output_string(ctx);
    result = Py_BuildValue(
        PySass_IF_PY3("hy", "hs"),
        (short int) !error_status,
        error_status ? error_message : output_string
    );
    sass_delete_data_context(context);
    return result;
}

static PyObject *
PySass_compile_filename(PyObject *self, PyObject *args) {
    struct Sass_Context *ctx;
    struct Sass_File_Context *context;
    struct Sass_Options *options;
    char *filename, *include_paths, *image_path;
    const char *error_message, *output_string, *source_map_string;
    Sass_Output_Style output_style;
    int source_comments, error_status, precision;
    PyObject *source_map_filename, *custom_functions, *result;

    if (!PyArg_ParseTuple(args,
                          PySass_IF_PY3("yiiyyiOO", "siissiOO"),
                          &filename, &output_style, &source_comments,
                          &include_paths, &image_path, &precision,
                          &source_map_filename, &custom_functions)) {
        return NULL;
    }

    context = sass_make_file_context(filename);
    options = sass_file_context_get_options(context);

    if (source_comments && PySass_Bytes_Check(source_map_filename)) {
        size_t source_map_file_len = PySass_Bytes_GET_SIZE(source_map_filename);
        if (source_map_file_len) {
            char *source_map_file = (char *) malloc(source_map_file_len + 1);
            strncpy(
                source_map_file,
                PySass_Bytes_AS_STRING(source_map_filename),
                source_map_file_len + 1
            );
            sass_option_set_source_map_file(options, source_map_file);
        }
    }
    sass_option_set_output_style(options, output_style);
    sass_option_set_source_comments(options, source_comments);
    sass_option_set_include_path(options, include_paths);
    sass_option_set_image_path(options, image_path);
    sass_option_set_precision(options, precision);
    _add_custom_functions(options, custom_functions);

    sass_compile_file_context(context);

    ctx = sass_file_context_get_context(context);
    error_status = sass_context_get_error_status(ctx);
    error_message = sass_context_get_error_message(ctx);
    output_string = sass_context_get_output_string(ctx);
    source_map_string = sass_context_get_source_map_string(ctx);
    result = Py_BuildValue(
        PySass_IF_PY3("hyy", "hss"),
        (short int) !error_status,
        error_status ? error_message : output_string,
        error_status || source_map_string == NULL ? "" : source_map_string
    );
    sass_delete_file_context(context);
    return result;
}

static PyMethodDef PySass_methods[] = {
    {"compile_string", PySass_compile_string, METH_VARARGS,
     "Compile a SASS string."},
    {"compile_filename", PySass_compile_filename, METH_VARARGS,
     "Compile a SASS file."},
    {NULL, NULL, 0, NULL}
};

static char PySass_doc[] = "The thin binding of libsass for Python.";

void PySass_make_enum_dict(PyObject *enum_dict, struct PySass_Pair *pairs) {
    size_t i;
    for (i = 0; pairs[i].label; ++i) {
        PyDict_SetItemString(
            enum_dict,
            pairs[i].label,
            PySass_Int_FromLong((long) pairs[i].value)
        );
    }
}

void PySass_init_module(PyObject *module) {
    PyObject *output_styles;
    output_styles = PyDict_New();
    PySass_make_enum_dict(output_styles, PySass_output_style_enum);
    PyModule_AddObject(module, "OUTPUT_STYLES", output_styles);
}

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef sassmodule = {
    PyModuleDef_HEAD_INIT,
    "_sass",
    PySass_doc,
    -1,
    PySass_methods
};

PyMODINIT_FUNC
PyInit__sass()
{
    PyObject *module = PyModule_Create(&sassmodule);
    if (module != NULL) {
        PySass_init_module(module);
    }
    return module;
}

#else

PyMODINIT_FUNC
init_sass()
{
    PyObject *module;
    module = Py_InitModule3("_sass", PySass_methods, PySass_doc);
    if (module != NULL) {
        PySass_init_module(module);
    }
}

#endif

#ifdef __cplusplus
}
#endif
