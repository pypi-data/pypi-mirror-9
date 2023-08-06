#include <Python.h>
#include <cstdint>
#include <new>
#include <sstream>
#include <type_traits>


// typedef for the cast "virtual" function
struct base_cinc_int;
typedef uint64_t(*castfunc)(base_cinc_int*);

/*
 * Base type for all cinc types.
 * This type exists so that the cinc types can be cast to another cinc type.
 */
struct base_cinc_int
{
    PyObject_HEAD
    /*
     * This simulates a virtual function.
     * virtual functions can't be used because it will break the ABI.
     */
    castfunc cast;
};

static PyTypeObject base_cinc_int_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cinc.BaseCincInt", // type name
    sizeof(base_cinc_int_type), // basic size
    0, // item size
    0, // deallocator
    0, // print
    0, // getattr (deprecated)
    0, // setattr (deprecated)
    0, // reserved
    0, // repr
    0, // number methods
    0, // sequence methods
    0, // mapping methods
    0, // hash
    0, // call
    0, // str
    0, // getattro
    0, // setattro
    0, // buffer functions
    Py_TPFLAGS_DEFAULT, // flags
    "Base type for all cinc types.\n"
    "This type cannot be constructed.",
};


/*
 * cinc integer type template.
 */
template<typename T>
struct cinc_integer : public base_cinc_int
{
    T value;
    PyObject* int_cache;

    cinc_integer(T initvalue);
    ~cinc_integer();

    static PyObject* create_object(PyTypeObject* type, T initvalue);
    static PyObject* new_object(PyTypeObject* type, PyObject* args, PyObject* kwds);

    static void dealloc(cinc_integer<T>* self);

    static uint64_t cast_value(base_cinc_int* self);

    static PyObject* str(cinc_integer<T>* self);
    static PyObject* repr(cinc_integer<T>* self);
    static Py_hash_t hash(cinc_integer<T>* self);

    static PyObject* compare(cinc_integer<T>* self, PyObject* other, int op);

    // Number protocol
    static PyObject* as_int(cinc_integer<T>* self);
    static int as_bool(cinc_integer<T>* self);
    static PyObject* as_float(cinc_integer<T>* self);

    static PyObject* add(PyObject* op1, PyObject* op2);
    static PyObject* subtract(PyObject* op1, PyObject* op2);

    static PyObject* multiply(PyObject* op1, PyObject* op2);
    static PyObject* divide(PyObject* op1, PyObject* op2);
    static PyObject* remainder(PyObject* op1, PyObject* op2);
    static PyObject* divmod(PyObject* op1, PyObject* op2);
    static PyObject* power(PyObject* op1, PyObject* op2, PyObject* mod);

    static PyObject* negative(cinc_integer<T>* self);
    static PyObject* positive(cinc_integer<T>* self);
    static PyObject* abs(cinc_integer<T>* self);

    static PyObject* invert(cinc_integer<T>* self);

    static PyObject* lshift(PyObject* op1, PyObject* op2);
    static PyObject* rshift(PyObject* op1, PyObject* op2);

    static PyObject* bitwise_and(PyObject* op1, PyObject* op2);
    static PyObject* bitwise_or(PyObject* op1, PyObject* op2);
    static PyObject* bitwise_xor(PyObject* op1, PyObject* op2);

    // Methods
    static PyObject* getnewargs(cinc_integer<T>* self, PyObject*);

    static PyObject* extract(cinc_integer<T>* self, PyObject* args, PyObject* kw);
    static PyObject* insert(cinc_integer<T>* self, PyObject* args, PyObject* kw);

    static PyObject* lrotate(cinc_integer<T>* self, PyObject* object);
    static PyObject* rrotate(cinc_integer<T>* self, PyObject* object);
};


/*
 * Constructor and destructor.
 */
template<typename T>
cinc_integer<T>::cinc_integer(T initvalue)
{
    this->cast = cinc_integer<T>::cast_value;
    this->value = initvalue;
    this->int_cache = NULL;
}

template<typename T>
cinc_integer<T>::~cinc_integer()
{
    Py_XDECREF(this->int_cache);
}


/*
 * create_object
 * Construct a cinc_integer object.
 * If the type is not a derived class, the object is created directly.
 */
template<typename T>
PyObject* cinc_integer<T>::create_object(PyTypeObject* type, T initvalue)
{
    cinc_integer<T>* newobject;
    if(type->tp_base == &base_cinc_int_type)
    {
        newobject = (cinc_integer<T>*)(type->tp_alloc(type, 0));
        if(newobject == NULL)
            return NULL;
        new(newobject) cinc_integer<T>(initvalue);
    }
    else
    {
        PyObject* args;
        if(std::is_unsigned<T>::value)
            args = Py_BuildValue("(K)", static_cast<uint64_t>(initvalue));
        else
            args = Py_BuildValue("(L)", static_cast<int64_t>(initvalue));
        newobject = (cinc_integer<T>*)PyObject_Call((PyObject*)type, args, NULL);
        Py_DECREF(args);
    }
    return (PyObject*)newobject;
}


/*
 * If the object is a cinc type or python int, convert it to a uint64_t.
 */
static int convert_cinc_pyint(PyObject* object, uint64_t* result)
{
    if(PyLong_Check(object))
        *result = PyLong_AsUnsignedLongLongMask(object);
    else if(PyObject_TypeCheck(object, &base_cinc_int_type))
        *result = ((base_cinc_int*)object)->cast((base_cinc_int*)object);
    else
    {
        PyErr_Format(PyExc_TypeError,
                     "argument must be an int or cinc type, not %s",
                     Py_TYPE(object)->tp_name);
        return 0;
    }
    return 1;
}

/*
 * new method.
 * Takes a single argument. Which can be a python int or a cinc type.
 */
static const char* new_keywords[] = {"x", NULL};
template<typename T>
PyObject* cinc_integer<T>::new_object(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    uint64_t x = 0;
    if(!PyArg_ParseTupleAndKeywords(args, kwds, "|O&",
            const_cast<char**>(new_keywords),
            convert_cinc_pyint, &x))
        return NULL;
    cinc_integer<T>* newobject = (cinc_integer<T>*)type->tp_alloc(type, 0);
    if(newobject != NULL)
        new(newobject) cinc_integer<T>(x);
    return (PyObject*)newobject;
}


/*
 * Deallocator for cinc types.
 */
template<typename T>
void cinc_integer<T>::dealloc(cinc_integer<T>* self)
{
    self->~cinc_integer<T>();
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject*>(self));
}


/*
 * cast_value()
 * Cast the value to a uint64_t, which can then be cast to the appropriate
 * type.
 */
template<typename T>
uint64_t cinc_integer<T>::cast_value(base_cinc_int* self)
{
    return static_cast<uint64_t>(static_cast<cinc_integer*>(self)->value);
}


/*
 * str and repr methods.
 */
template<typename T>
PyObject* cinc_integer<T>::str(cinc_integer<T>* self)
{
    try
    {
        std::stringstream stream;
        if(std::is_same<T, signed char>::value || std::is_same<T, unsigned char>::value)
            stream << static_cast<int_fast16_t>(self->value);
        else
            stream << self->value;

        PyObject* result = Py_BuildValue("s", stream.str().c_str());
        return result;
    }
    catch(std::bad_alloc&)
    {
        return PyErr_NoMemory();
    }
}

template<typename T>
PyObject* cinc_integer<T>::repr(cinc_integer<T>* self)
{
    try
    {
        std::stringstream stream;
        stream << Py_TYPE(self)->tp_name << '(';
        if(std::is_same<T, signed char>::value || std::is_same<T, unsigned char>::value)
            stream << static_cast<int_fast16_t>(self->value);
        else
            stream << self->value;
        stream << ')';

        PyObject* result = Py_BuildValue("s", stream.str().c_str());
        return result;
    }
    catch(std::bad_alloc&)
    {
        return PyErr_NoMemory();
    }
}

/*
 * hash method.
 * If the result is -1, returns -2 instead.
 */
template<typename T>
Py_hash_t cinc_integer<T>::hash(cinc_integer<T>* self)
{
    Py_hash_t hashvalue;
    if(sizeof(T) <= sizeof(Py_hash_t))
        hashvalue = self->value;
    else
    {
        // Handling for 64-bit types.
        // The two haves are XOR'd together.
        const unsigned char bits = sizeof(Py_hash_t) * CHAR_BIT;
        hashvalue = static_cast<Py_hash_t>(self->value) ^ (self->value >> bits);
    }

    if(hashvalue == static_cast<T>(-1))
        return static_cast<T>(-2);
    else
        return hashvalue;
}


/*
 * Argument converter for operators.
 */
#define cast_cinc(object, objectvalue) \
    if(PyObject_TypeCheck(object, &base_cinc_int_type)) \
        objectvalue = ((base_cinc_int*)object)->cast((base_cinc_int*)object); \
    else \
    { \
        Py_RETURN_NOTIMPLEMENTED; \
    }

/*
 * Comparison for cinc objects.
 * cinc types can only be compared with other cinc types.
 */
template<typename T>
PyObject* cinc_integer<T>::compare(cinc_integer<T>* self, PyObject* other, int op)
{
    T othervalue;
    assert((PyObject_TypeCheck(self, &base_cinc_int_type)));
    cast_cinc(other, othervalue);

    bool result = false;
    switch(op)
    {
        case Py_LT:
            result = self->value < othervalue;
            break;
        case Py_LE:
            result = self->value <= othervalue;
            break;
        case Py_EQ:
            result = self->value == othervalue;
            break;
        case Py_NE:
            result = self->value != othervalue;
            break;
        case Py_GT:
            result = self->value > othervalue;
            break;
        case Py_GE:
            result = self->value >= othervalue;
            break;
    }
    PyObject* resultobject = result ? Py_True : Py_False;
    Py_INCREF(resultobject);
    return resultobject;
}


/*
 * Number protocol methods
 */

template<typename T>
PyObject* cinc_integer<T>::as_int(cinc_integer<T>* self)
{
    if(self->int_cache == NULL)
    {
        if(std::is_unsigned<T>::value)
            self->int_cache = PyLong_FromUnsignedLongLong(self->value);
        else
            self->int_cache = PyLong_FromLongLong(self->value);
        if(self->int_cache == NULL)
            return NULL;
    }
    Py_INCREF(self->int_cache);
    return self->int_cache;
}

template<typename T>
int cinc_integer<T>::as_bool(cinc_integer<T>* self)
{
    return static_cast<bool>(self->value);
}

template<typename T>
PyObject* cinc_integer<T>::as_float(cinc_integer<T>* self)
{
    return PyFloat_FromDouble(self->value);
}


/*
 * Addition and subtraction.
 */
template<typename T>
PyObject* cinc_integer<T>::add(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value + op2value);
}

template<typename T>
PyObject* cinc_integer<T>::subtract(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value - op2value);
}

/*
 * Multiply, divide, remainder and divmod.
 */
template<typename T>
PyObject* cinc_integer<T>::multiply(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value * op2value);
}

template<typename T>
PyObject* cinc_integer<T>::divide(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    if(op2value == 0)
    {
        PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
        return NULL;
    }
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value / op2value);
}

template<typename T>
PyObject* cinc_integer<T>::remainder(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    if(op2value == 0)
    {
        PyErr_SetString(PyExc_ZeroDivisionError,
            "integer division or modulo by zero");
        return NULL;
    }
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value % op2value);
}

template<typename T>
PyObject* cinc_integer<T>::divmod(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    if(op2value == 0)
    {
        PyErr_SetString(PyExc_ZeroDivisionError,
            "integer division or modulo by zero");
        return NULL;
    }

    T quot = op1value / op2value;
    T remain = op1value % op2value;

    PyObject* pyquot = cinc_integer<T>::create_object(Py_TYPE(op1), quot);
    if(pyquot == NULL)
        return NULL;
    PyObject* pyremain = cinc_integer<T>::create_object(Py_TYPE(op1), remain);
    if(pyremain == NULL)
    {
        Py_DECREF(pyquot);
        return NULL;
    }

    PyObject* result = Py_BuildValue("NN", pyquot, pyremain);
    if(result == NULL)
    {
        Py_DECREF(pyquot);
        Py_DECREF(pyremain);
    }
    return result;
}


/*
 * power
 */
template<typename T>
PyObject* cinc_integer<T>::power(PyObject* op1, PyObject* op2, PyObject* mod)
{
    T op1value, op2value, modvalue = 0;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    if(mod != Py_None)
    {
        if(op2value < 0)
        {
            PyErr_SetString(PyExc_TypeError,
                "pow() 2nd argument cannot be negative when 3rd argument specified");
            return NULL;
        }
        cast_cinc(mod, modvalue)
        if(modvalue == 0)
        {
            PyErr_SetString(PyExc_ValueError,
                "pow() 3rd argument cannot be 0");
            return NULL;
        }
    }

    T result = 1;
    for(T i = 0; i < op2value; ++i)
        result *= op1value;
    if(mod != Py_None)
        result %= modvalue;
    return cinc_integer<T>::create_object(Py_TYPE(op1), result);
}


/*
 * negative, positive and abs.
 */
template<typename T>
PyObject* cinc_integer<T>::negative(cinc_integer<T>* self)
{
    if(self->value == 0)
    {
        Py_INCREF(self);
        return (PyObject*)self;
    }
    else
        return cinc_integer<T>::create_object(Py_TYPE(self), -self->value);
}

template<typename T>
PyObject* cinc_integer<T>::positive(cinc_integer<T>* self)
{
    Py_INCREF(self);
    return (PyObject*)self;
}

template<typename T>
PyObject* cinc_integer<T>::abs(cinc_integer<T>* self)
{
    if(self->value < 0)
        return cinc_integer<T>::create_object(Py_TYPE(self), -self->value);
    else
    {
        Py_INCREF(self);
        return (PyObject*)self;
    }
}


/*
 * invert
 */
template<typename T>
PyObject* cinc_integer<T>::invert(cinc_integer<T>* self)
{
    return cinc_integer<T>::create_object(Py_TYPE(self), ~self->value);
}


/*
 * Converter for shift operators.
 * The converter will convert python ints in addition to cinc types.
 */
#define cast_cinc_pyint(object, objectvalue) \
    if(PyLong_Check(object)) \
        objectvalue = PyLong_AsUnsignedLongMask(object); \
    else cast_cinc(object, objectvalue)

/*
 * left and right shift.
 * The methods accept python ints as their other operand.
 */
template<typename T>
PyObject* cinc_integer<T>::lshift(PyObject* op1, PyObject* op2)
{
    T op1value;
    unsigned char shift;
    cast_cinc_pyint(op1, op1value);
    cast_cinc_pyint(op2, shift);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value << shift);
}

template<typename T>
PyObject* cinc_integer<T>::rshift(PyObject* op1, PyObject* op2)
{
    T op1value;
    unsigned char shift;
    cast_cinc_pyint(op1, op1value);
    cast_cinc_pyint(op2, shift);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value >> shift);
}


/*
 * bitwise and, or and xor.
 */
template<typename T>
PyObject* cinc_integer<T>::bitwise_and(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value & op2value);
}

template<typename T>
PyObject* cinc_integer<T>::bitwise_or(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value | op2value);
}

template<typename T>
PyObject* cinc_integer<T>::bitwise_xor(PyObject* op1, PyObject* op2)
{
    T op1value, op2value;
    cast_cinc(op1, op1value);
    cast_cinc(op2, op2value);
    return cinc_integer<T>::create_object(Py_TYPE(op1),
                                          op1value ^ op2value);
}

/*
 * __getnewargs__()
 */
template<typename T>
PyObject* cinc_integer<T>::getnewargs(cinc_integer<T>* self, PyObject*)
{
    return Py_BuildValue("(N)", cinc_integer<T>::as_int(self));
}


/*
 * extract(pos, size)
 */
static const char* extract_keywords[] = {"pos", "size", NULL};
template<typename T>
PyObject* cinc_integer<T>::extract(cinc_integer<T>* self, PyObject* args, PyObject* kw)
{
    unsigned char pos, size;
    if(!PyArg_ParseTupleAndKeywords(args, kw, "BB",
            const_cast<char**>(extract_keywords), &pos, &size))
        return NULL;

    const uint64_t mask = (1 << size) -1;
    return cinc_integer<T>::create_object(Py_TYPE(self),
                                          (self->value >> pos) & mask);
}

/*
 * insert(value, pos, size)
 */
static const char* insert_keywords[] = {"value", "pos", "size", NULL};
template<typename T>
PyObject* cinc_integer<T>::insert(cinc_integer<T>* self, PyObject* args, PyObject* kw)
{
    base_cinc_int* value;
    unsigned char pos, size;
    if(!PyArg_ParseTupleAndKeywords(args, kw, "O!BB",
            const_cast<char**>(insert_keywords),
            &base_cinc_int_type, &value, &pos, &size))
        return NULL;

    const uint64_t mask = ((1 << size) -1) << pos;

    T otherbits = value->cast(value) << pos;
    T result = self->value ^ ((self->value ^ otherbits) & mask);
    return cinc_integer<T>::create_object(Py_TYPE(self), result);
}

/*
 * rotate methods
 */
template<typename T>
PyObject* cinc_integer<T>::lrotate(cinc_integer<T>* self, PyObject* object)
{
    uint64_t shift;
    if(!convert_cinc_pyint(object, &shift))
        return NULL;

    const unsigned char bits = sizeof(T) * CHAR_BIT;
    typename std::make_unsigned<T>::type value = self->value;
    return cinc_integer<T>::create_object(Py_TYPE(self),
        (value << shift) | (value >> (bits - shift)));
}

template<typename T>
PyObject* cinc_integer<T>::rrotate(cinc_integer<T>* self, PyObject* object)
{
    uint64_t shift;
    if(!convert_cinc_pyint(object, &shift))
        return NULL;

    const unsigned char bits = sizeof(T) * CHAR_BIT;
    typename std::make_unsigned<T>::type value = self->value;
    return cinc_integer<T>::create_object(Py_TYPE(self),
        (value >> shift) | (value << (bits - shift)));
}


#define DECLARE_TYPE(type) _DECLARE_TYPE(type, cinc_integer<type ## _t>)
#define _DECLARE_TYPE(type, integer) \
PyNumberMethods type ## _number_methods = { \
    integer::add, /* add */ \
    integer::subtract, /* subtract */ \
    integer::multiply, /* multiply */ \
    integer::remainder, /* remainder */ \
    integer::divmod, /* divmod */ \
    integer::power, /* power */ \
    (unaryfunc)integer::negative, /* negate */ \
    (unaryfunc)integer::positive, /* positive */ \
    (unaryfunc)integer::abs, /* absolute */ \
    (inquiry)integer::as_bool, /* bool */ \
    (unaryfunc)integer::invert, /* invert */ \
    integer::lshift, /* left shift */ \
    integer::rshift, /* right shift */ \
    integer::bitwise_and, /* and */ \
    integer::bitwise_xor, /* xor */ \
    integer::bitwise_or, /* or */ \
    (unaryfunc)integer::as_int, /* int */ \
    0, /* reserved */ \
    (unaryfunc)integer::as_float, /* float */ \
    0, /* in place add */ \
    0, /* in place subtract */ \
    0, /* in place multiply */ \
    0, /* in place remainder */ \
    0, /* in place power */ \
    0, /* in place left shift */ \
    0, /* in place right shift */ \
    0, /* in place and */ \
    0, /* in place xor */ \
    0, /* in place or */ \
    integer::divide, /* floor divide */ \
    0, /* true divide */ \
}; \
static PyMethodDef type ## _methods[] = { \
    {"__getnewargs__", \
        (PyCFunction)integer::getnewargs, \
        METH_NOARGS, \
        "__getnewargs__($self, /)\n--\n\n" \
        "Return (int(self),)\n" \
        "Used by the pickle module."}, \
\
    {"extract", \
        (PyCFunction)integer::extract, \
        METH_VARARGS | METH_KEYWORDS, \
        "extract($self, /, pos, size)\n--\n\n" \
        "Extracts size bits starting from pos.\n" \
        ">>> x = " #type "(0b10010).extract(1, 4)\n" \
        ">>> bin(int(x))\n" \
        "'0b1001'"}, \
\
    {"insert", \
        (PyCFunction)integer::insert, \
        METH_VARARGS | METH_KEYWORDS, \
        "insert($self, /, value, pos, size)\n--\n\n" \
        "Returns a " #type " with the right most size bits from value inserted at pos.\n" \
        ">>> x = " #type "(0b0101)\n" \
        ">>> y = " #type "(0b110100).insert(x, 1, 4)\n" \
        ">>> bin(int(y))\n" \
        "'0b101010'"}, \
\
    {"lrotate", \
        (PyCFunction)integer::lrotate, \
        METH_O, \
        "lrotate($self, value, /)\n--\n\n" \
        "Return self left-rotate value."}, \
\
    {"rrotate", \
        (PyCFunction)integer::rrotate, \
        METH_O, \
        "rrotate($self, value, /)\n--\n\n" \
        "Return self right-rotate value.\n" \
        "self is always treated as an unsigned type."}, \
\
    {NULL} \
}; \
PyTypeObject type ## _type = { \
    PyVarObject_HEAD_INIT(NULL, 0) \
    "cinc." #type, /* type name */ \
    sizeof(integer), /* basic size */ \
    0, /* item size */ \
    (destructor)integer::dealloc, /* deallocator */ \
    0, /* print */ \
    0, /* getattr (deprecated) */ \
    0, /* setattr (deprecated) */ \
    0, /* reserved */ \
    (reprfunc)integer::repr, /* repr */ \
    &type ## _number_methods, /* number methods */ \
    0, /* sequence methods */ \
    0, /* mapping methods */ \
    (hashfunc)integer::hash, /* hash */ \
    0, /* call */ \
    (reprfunc)integer::str, /* str */ \
    0, /* getattro */ \
    0, /* setattro */ \
    0, /* buffer functions */ \
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* flags */ \
    #type "(x=0)\n\n" \
    "cinc type for the " #type "_t C type.", /* doc */ \
    0, /* traverse */ \
    0, /* clear */ \
    (richcmpfunc)integer::compare, /* rich compare */ \
    0, /* weak list offset */ \
    0, /* iter */ \
    0, /* iter next */ \
    type ## _methods, /* methods */ \
    0, /* members */ \
    0, /* get set */ \
    &base_cinc_int_type, /* base type */ \
    0, /* dict */ \
    0, /* descriptor get */ \
    0, /* descriptor set */ \
    0, /* dict offset */ \
    0, /* init */ \
    0, /* alloc */ \
    integer::new_object /* new */ \
};
DECLARE_TYPE(int8)
DECLARE_TYPE(uint8)
DECLARE_TYPE(int16)
DECLARE_TYPE(uint16)
DECLARE_TYPE(int32)
DECLARE_TYPE(uint32)
DECLARE_TYPE(int64)
DECLARE_TYPE(uint64)


static PyModuleDef cincmodule = {
    PyModuleDef_HEAD_INIT,
    "cinc", // name
    "Fast fixed-sized C-like integer types.\n\n"
    "Signed types are named \"intN\" and unsigned types are named \"uintN\", where \"N\"\n"
    "is the number of bits. Types for 8, 16, 32 and 64 bits are provided.\n\n"
    "cinc integers can be constructed from a Python ints or cast from another cinc\ntype.\n\n"
    "They support all arithmetic operators and also have methods for bit rotate \n"
    "operations as well as bit extraction and insertion.",
    -1, // size
    NULL, // methods
    NULL, // reload
    NULL, // traverse
    NULL, // clear
    NULL // free
};

#define INIT_TYPE(type) \
    if(PyType_Ready(&type ## _type) < 0) \
        return NULL;
#define ADD_TYPE(type) \
    Py_INCREF(&type ## _type); \
    PyModule_AddObject(module, #type, reinterpret_cast<PyObject*>(&type ## _type));

PyMODINIT_FUNC PyInit_cinc()
{
    if(PyType_Ready(&base_cinc_int_type) < 0)
        return NULL;

    INIT_TYPE(int8)
    INIT_TYPE(uint8)
    INIT_TYPE(int16)
    INIT_TYPE(uint16)
    INIT_TYPE(int32)
    INIT_TYPE(uint32)
    INIT_TYPE(int64)
    INIT_TYPE(uint64)

    PyObject* module = PyModule_Create(&cincmodule);
    if(module == NULL)
        return NULL;

    ADD_TYPE(int8)
    ADD_TYPE(uint8)
    ADD_TYPE(int16)
    ADD_TYPE(uint16)
    ADD_TYPE(int32)
    ADD_TYPE(uint32)
    ADD_TYPE(int64)
    ADD_TYPE(uint64)

    return module;
}
