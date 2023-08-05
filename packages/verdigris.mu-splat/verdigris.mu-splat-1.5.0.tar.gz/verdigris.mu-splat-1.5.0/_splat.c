/*
    Splat - _splat.c

    Copyright (C) 2012, 2013, 2014, 2015
    Guillaume Tucker <guillaume@mangoz.org>

    This program is free software; you can redistribute it and/or modify it
    under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your
    option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
    License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <Python.h>
#include <math.h>

/* Set to 1 to use 4xfloat vectors (SSE) */
#define USE_V4SF 0

#define BASE_TYPE_FLAGS (Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE)
#define MAX_CHANNELS 16

#define lin2dB(level) (20 * log10(level))
#define dB2lin(dB) (pow10((dB) / 20))

/* Use PP_NARG to get the number of arguments in __VA_ARGS__ */
#define PP_NARG(...) \
         PP_NARG_(__VA_ARGS__,PP_RSEQ_N())
#define PP_NARG_(...) \
         PP_ARG_N(__VA_ARGS__)
#define PP_ARG_N( \
          _1, _2, _3, _4, _5, _6, _7, _8, _9,_10, \
         _11,_12,_13,_14,_15,_16,_17,_18,_19,_20, \
         _21,_22,_23,_24,_25,_26,_27,_28,_29,_30, \
         _31,_32,_33,_34,_35,_36,_37,_38,_39,_40, \
         _41,_42,_43,_44,_45,_46,_47,_48,_49,_50, \
         _51,_52,_53,_54,_55,_56,_57,_58,_59,_60, \
         _61,_62,_63,N,...) N
#define PP_RSEQ_N() \
         63,62,61,60,                   \
         59,58,57,56,55,54,53,52,51,50, \
         49,48,47,46,45,44,43,42,41,40, \
         39,38,37,36,35,34,33,32,31,30, \
         29,28,27,26,25,24,23,22,21,20, \
         19,18,17,16,15,14,13,12,11,10, \
         9,8,7,6,5,4,3,2,1,0

#ifndef min
# define min(_a, _b) (((_a) < (_b)) ? (_a) : (_b))
#endif

#ifndef max
# define max(_a, _b) (((_a) > (_b)) ? (_a) : (_b))
#endif

#ifndef minmax
# define minmax(_val, _min, _max) \
	((_val) < (_min) ? (_min) : ((_val) > (_max) ? (_max) : (_val)))
#endif

#ifndef ARRAY_SIZE
# define ARRAY_SIZE(_array) (sizeof(_array) / sizeof(_array[0]))
#endif

static const char SPLAT_INT_8[] = "int8";
static const char SPLAT_INT_16[] = "int16";
static const char SPLAT_INT_24[] = "int24";
static const char SPLAT_FLOAT_32[] = "float32";
static const char SPLAT_FLOAT_64[] = "float64";

/* Internal sample type used in Fragment, sources, effects etc... */
#if USE_V4SF /* for speed and smaller memory footprint */
typedef float sample_t;
typedef float v4sf __attribute__ ((vector_size(16)));
#define SPLAT_NATIVE_SAMPLE_TYPE SPLAT_FLOAT_32
#else /* for precision */
typedef double sample_t;
#define SPLAT_NATIVE_SAMPLE_TYPE SPLAT_FLOAT_64
#endif

#define SPLAT_NATIVE_SAMPLE_WIDTH (sizeof(sample_t) * 8)

struct splat_raw_io {
	const char *sample_type;
	size_t sample_width;
	void (*import)(sample_t *out, const char *in, size_t n, size_t step);
	void (*export)(char *out, const sample_t **it, unsigned channels,
		       size_t n);
};

static const struct splat_raw_io *splat_get_raw_io(const char *sample_type);

/* Convert any number type to a double or return -1 */
static int splat_obj2double(PyObject *obj, double *out)
{
	double value;

	if (PyFloat_Check(obj))
		value = PyFloat_AsDouble(obj);
	else if (PyLong_Check(obj))
		value = PyLong_AsDouble(obj);
	else if (PyInt_Check(obj))
		value = (double)PyInt_AsLong(obj);
	else
		return -1;

	if (out != NULL)
		*out = value;

	return 0;
}

/* ----------------------------------------------------------------------------
 * Module constants
 */

/* Initial ratio for sound sources (square, triangle) */
static PyObject *splat_init_source_ratio;

/* A Python float with the value of 0.0 */
static PyObject *splat_zero;

/* A dictionary with sample type names as keys and size as values */
static PyObject *splat_sample_types;

/* ----------------------------------------------------------------------------
 * Fragment class interface
 */

struct Fragment_object {
	PyObject_HEAD;
	int init;
	unsigned n_channels;
	unsigned rate;
	size_t length;
	sample_t *data[MAX_CHANNELS];
	const char *name;
};
typedef struct Fragment_object Fragment;

static PyTypeObject splat_FragmentType;

/* ----------------------------------------------------------------------------
 * Spline class
 */

struct Spline_object {
	PyObject_HEAD;
	int init;
	PyObject *pols; /* List of tuples with (x0, x1, coeffs) */
	double k0;
	double start;
	double end;
};
typedef struct Spline_object Spline;

static PyTypeObject splat_SplineType;

static double splat_spline_tuple_value(PyObject *poly, double x);
static PyObject *splat_find_spline_poly(PyObject *spline, double x,
					double *end);

static void Spline_dealloc(Spline *self)
{
	if (self->init) {
		Py_DECREF(self->pols);
		self->init = 0;
	}
}

static int Spline_init(Spline *self, PyObject *args)
{
	PyObject *poly;

	if (!PyArg_ParseTuple(args, "O!d", &PyList_Type, &self->pols,
			      &self->k0))
		return -1;

	Py_INCREF(self->pols);

	poly = PyList_GET_ITEM(self->pols, 0);
	self->start = PyFloat_AS_DOUBLE(PyTuple_GET_ITEM(poly, 0));

	poly = PyList_GET_ITEM(self->pols, PyList_GET_SIZE(self->pols) - 1);
	self->end = PyFloat_AS_DOUBLE(PyTuple_GET_ITEM(poly, 1));

	self->init = 1;

	return 0;
}

static PyObject *Spline_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	Spline *self;

	self = (Spline *)type->tp_alloc(type, 0);

	if (self == NULL)
		return PyErr_NoMemory();

	self->init = 0;

	return (PyObject *)self;
}

static PyTypeObject splat_SplineType = {
	PyObject_HEAD_INIT(NULL)
	0,                                 /* ob_size */
	"_splat.Spline",                   /* tp_name */
	sizeof(Spline),                    /* tp_basicsize */
	0,                                 /* tp_itemsize */
	(destructor)Spline_dealloc,        /* tp_dealloc */
	0,                                 /* tp_print */
	0,                                 /* tp_getattr */
	0,                                 /* tp_setattr */
	0,                                 /* tp_compare */
	0,                                 /* tp_repr */
	0,                                 /* tp_as_number */
	0,                                 /* tp_as_sequence */
	0,                                 /* tp_as_mapping */
	0,                                 /* tp_hash  */
	0,                                 /* tp_call */
	0,                                 /* tp_str */
	0,                                 /* tp_getattro */
	0,                                 /* tp_setattro */
	0,                                 /* tp_as_buffer */
	BASE_TYPE_FLAGS,                   /* tp_flags */
	0,                                 /* tp_doc */
	0,                                 /* tp_traverse */
	0,                                 /* tp_clear */
	0,                                 /* tp_richcompare */
	0,                                 /* tp_weaklistoffset */
	0,                                 /* tp_iter */
	0,                                 /* tp_iternext */
	0,                                 /* tp_methods */
	0,                                 /* tp_members */
	0,                                 /* tp_getset */
	0,                                 /* tp_base */
	0,                                 /* tp_dict */
	0,                                 /* tp_descr_get */
	0,                                 /* tp_descr_set */
	0,                                 /* tp_dictoffset */
	(initproc)Spline_init,             /* tp_init */
	0,                                 /* tp_alloc */
	Spline_new,                        /* tp_new */
};

static double splat_spline_tuple_value(PyObject *poly, double x)
{
	Py_ssize_t i;
	double value = 0.0;
	double x_pow = 1.0;

	for (i = 0; i < PyTuple_GET_SIZE(poly); ++i) {
		PyObject *py_k = PyTuple_GET_ITEM(poly, i);
		const double k = PyFloat_AS_DOUBLE(py_k);

		value += k * x_pow;
		x_pow *= x;
	}

	return value;
}

static PyObject *splat_find_spline_poly(PyObject *spline, double x,
					double *end)
{
	Py_ssize_t i;

	if (!PyList_CheckExact(spline)) {
		PyErr_SetString(PyExc_TypeError, "spline must be a list");
		return NULL;
	}

	for (i = 0; i < PyList_GET_SIZE(spline); ++i) {
		PyObject *poly_params = PyList_GET_ITEM(spline, i);
		PyObject *param;
		double poly_start;
		double poly_end;

		if (!PyTuple_CheckExact(poly_params) ||
		    (PyTuple_GET_SIZE(poly_params) != 3)) {
			PyErr_SetString(PyExc_TypeError,
					"spline list item must be a 3-tuple");
			return NULL;
		}

		param = PyTuple_GET_ITEM(poly_params, 1);

		if (!PyFloat_CheckExact(param)) {
			PyErr_SetString(PyExc_TypeError,
				"spline list item start time must be a float");
			return NULL;
		}

		poly_end = PyFloat_AS_DOUBLE(param);

		if (x > poly_end)
			continue;

		param = PyTuple_GET_ITEM(poly_params, 0);

		if (!PyFloat_CheckExact(param)) {
			PyErr_SetString(PyExc_TypeError,
				"spline list item end time must be a float");
			return NULL;
		}

		poly_start = PyFloat_AS_DOUBLE(param);

		if (x < poly_start)
			continue;

		param = PyTuple_GET_ITEM(poly_params, 2);

		if (!PyTuple_CheckExact(param)) {
			PyErr_SetString(PyExc_TypeError,
				"spline list item coefs must be a tuple");
			return NULL;
		}

		if (end != NULL)
			*end = poly_end;

		return param;
	}

	return NULL;
}

/* ----------------------------------------------------------------------------
 * Signal vector interface
 */

#define SIGNAL_VECTOR_BITS 8
#define SIGNAL_VECTOR_LEN (1 << SIGNAL_VECTOR_BITS)

struct splat_signal;

struct signal_vector {
	sample_t data[SIGNAL_VECTOR_LEN];
	PyObject *obj;
	int (*signal)(struct splat_signal *s, struct signal_vector *v);
};

enum signal_ret {
	SIGNAL_VECTOR_CONTINUE = 0,
	SIGNAL_VECTOR_ERROR,
	SIGNAL_VECTOR_STOP,
};

struct splat_signal {
	enum signal_ret stat;
	size_t origin;
	size_t length;
	size_t n_vectors;
	struct signal_vector *vectors;
	unsigned rate;
	PyObject *py_float;
	PyObject *py_args;
	size_t cur;
	size_t end;
	size_t len;
};

static int splat_signal_init(struct splat_signal *s, size_t length,
			     size_t origin, PyObject **signals,
			     size_t n_signals, unsigned rate);
static void splat_signal_free(struct splat_signal *s);
static int splat_signal_next(struct splat_signal *s);
static ssize_t splat_signal_get(struct splat_signal *s, size_t n);
static PyObject *splat_signal_tuple(struct splat_signal *s, size_t offset);

/* -- Signal class -- */

struct Signal_object {
	PyObject_HEAD;
	int init;
	PyObject **signals;
	struct splat_signal sig;
	unsigned offset;
};
typedef struct Signal_object Signal;

static PyTypeObject splat_SignalType;

static void Signal_free_signals(Signal *self, size_t n)
{
	size_t i;

	for (i = 0; i < n; ++i)
		Py_DECREF(self->signals[i]);

	PyMem_Free(self->signals);
}

static void Signal_dealloc(Signal *self)
{
	if (self->init) {
		splat_signal_free(&self->sig);
		Signal_free_signals(self, self->sig.n_vectors);
		self->init = 0;
	}

	self->ob_type->tp_free((PyObject *)self);
}

static int Signal_init(Signal *self, PyObject *args)
{
	Fragment *frag;
	PyObject *sig_obj;
	double duration = 0.0;
	double origin = 0.0;

	size_t n_signals;
	size_t i;
	size_t length;

	if (!PyArg_ParseTuple(args, "O!O|dd", &splat_FragmentType, &frag,
			      &sig_obj, &duration, &origin))
		return -1;

	if (PyTuple_Check(sig_obj))
		n_signals = PyTuple_GET_SIZE(sig_obj);
	else
		n_signals = 1;

	if (duration != 0.0) {
		if (duration < 0.0) {
			PyErr_SetString(PyExc_ValueError, "negative duration");
			return -1;
		}

		length = duration * frag->rate;
	} else {
		length = frag->length;
	}

	if (origin < 0.0) {
		PyErr_SetString(PyExc_ValueError, "negative signal origin");
		return -1;
	}

	self->signals = PyMem_Malloc(sizeof(PyObject *) * n_signals);

	if (self->signals == NULL) {
		PyErr_NoMemory();
		return -1;
	}

	if (PyTuple_Check(sig_obj)) {
		for (i = 0; i < n_signals; ++i)
			self->signals[i] = PyTuple_GET_ITEM(sig_obj, i);
	} else {
		self->signals[0] = sig_obj;
	}

	for (i = 0; i < n_signals; ++i)
		Py_INCREF(self->signals[i]);

	if (splat_signal_init(&self->sig, length, (origin * frag->rate),
			      self->signals, n_signals, frag->rate)) {
		Signal_free_signals(self, n_signals);
		return -1;
	}

	self->offset = 0;
	self->init = 1;

	return 0;
}

static PyObject *Signal_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	Signal *self;

	self = (Signal *)type->tp_alloc(type, 0);

	if (self == NULL)
		return PyErr_NoMemory();

	self->init = 0;

	return (PyObject *)self;
}

/* Signal sequence interface */

static Py_ssize_t SignalObj_sq_length(Signal *self)
{
	return self->sig.length;
}

static PyObject *SignalObj_sq_item(Signal *self, Py_ssize_t i)
{
	ssize_t offset;

	offset = splat_signal_get(&self->sig, i);

	if (offset < 0) {
		PyErr_SetString(PyExc_IndexError, "out of signal range");
		return NULL;
	}

	return splat_signal_tuple(&self->sig, offset);
}

static PySequenceMethods Signal_as_sequence = {
	(lenfunc)SignalObj_sq_length, /* sq_length (lenfunc) */
	NULL, /* sq_concat (binaryfunc) */
	NULL, /* sq_repeat (ssizeargfunc) */
	(ssizeargfunc)SignalObj_sq_item, /* sq_item (ssizeargfunc) */
	NULL, /* sq_slice (ssizessizeargfunc) */
	NULL, /* sq_ass_item (ssizeobjargproc) */
	NULL, /* sq_ass_slice (ssizessizeobjargproc) */
	NULL, /* sq_contains (objobjproc) */
	NULL, /* sq_inplace_concat (binaryfunc) */
	NULL, /* sq_inplace_repeat (ssizeargfunc) */
};

static PyTypeObject splat_SignalType = {
	PyObject_HEAD_INIT(NULL)
	0,                                 /* ob_size */
	"_splat.Signal",                   /* tp_name */
	sizeof(Signal),                    /* tp_basicsize */
	0,                                 /* tp_itemsize */
	(destructor)Signal_dealloc,        /* tp_dealloc */
	0,                                 /* tp_print */
	0,                                 /* tp_getattr */
	0,                                 /* tp_setattr */
	0,                                 /* tp_compare */
	0,                                 /* tp_repr */
	0,                                 /* tp_as_number */
	&Signal_as_sequence,               /* tp_as_sequence */
	0,                                 /* tp_as_mapping */
	0,                                 /* tp_hash  */
	0,                                 /* tp_call */
	0,                                 /* tp_str */
	0,                                 /* tp_getattro */
	0,                                 /* tp_setattro */
	0,                                 /* tp_as_buffer */
	BASE_TYPE_FLAGS,                   /* tp_flags */
	0,                                 /* tp_doc */
	0,                                 /* tp_traverse */
	0,                                 /* tp_clear */
	0,                                 /* tp_richcompare */
	0,                                 /* tp_weaklistoffset */
	0,                                 /* tp_iter */
	0,                                 /* tp_iternext */
	0,                                 /* tp_methods */
	0,                                 /* tp_members */
	0,                                 /* tp_getset */
	0,                                 /* tp_base */
	0,                                 /* tp_dict */
	0,                                 /* tp_descr_get */
	0,                                 /* tp_descr_set */
	0,                                 /* tp_dictoffset */
	(initproc)Signal_init,             /* tp_init */
	0,                                 /* tp_alloc */
	Signal_new,                        /* tp_new */
};

/* -- Signal internal functions -- */

static int splat_signal_func(struct splat_signal *s, struct signal_vector *v)
{
	const double rate = s->rate;
	sample_t *out = v->data;
	size_t i = s->cur;
	size_t j = s->len;

	while (j--) {
		PyObject *ret;

		PyFloat_AS_DOUBLE(s->py_float) = i++ / rate;
		ret = PyObject_Call(v->obj, s->py_args, NULL);

		if (!PyFloat_Check(ret)) {
			PyErr_SetString(PyExc_TypeError,
					"Signal did not return a float");
			Py_DECREF(ret);
			return -1;
		}

		*out++ = PyFloat_AS_DOUBLE(ret);
		Py_DECREF(ret);
	}

	return 0;
}

static int splat_signal_frag(struct splat_signal *s, struct signal_vector *v)
{
	Fragment *frag = (Fragment *)v->obj;

	memcpy(v->data, &frag->data[0][s->cur], (s->len * sizeof(sample_t)));

	return 0;
}

static int splat_signal_spline(struct splat_signal *s, struct signal_vector *v)
{
	Spline *spline = (Spline *)v->obj;
	const double rate = s->rate;
	const double k0 = spline->k0;
	sample_t *out = v->data;
	size_t i = s->cur;
	size_t j = s->len;
	PyObject *poly = NULL;
	double end = 0.0;

	while (j--) {
		const double x = i++ / rate;

		if ((x > end) || (poly == NULL)) {
			poly = splat_find_spline_poly(spline->pols, x, &end);

			if (poly == NULL) {
				PyErr_SetString(PyExc_ValueError,
						"Spline polynomial not found");
				return -1;

			}
		}

		*out++ = splat_spline_tuple_value(poly, x) * k0;
	}

	return 0;
}

static int splat_signal_init(struct splat_signal *s, size_t length,
			     size_t origin, PyObject **signals,
			     size_t n_signals, unsigned rate)
{
	size_t i;

	s->origin = origin;
	s->length = length + s->origin;
	s->n_vectors = n_signals;
	s->vectors = PyMem_Malloc(n_signals * sizeof(struct signal_vector));
	s->rate = rate;

	if (s->vectors == NULL) {
		PyErr_NoMemory();
		return -1;
	}

	s->py_float = PyFloat_FromDouble(0);

	if (s->py_float == NULL) {
		PyErr_SetString(PyExc_AssertionError,
				"Failed to create float object");
		return -1;
	}

	s->py_args = PyTuple_New(1);

	if (s->py_args == NULL) {
		PyErr_NoMemory();
		return -1;
	}

	PyTuple_SET_ITEM(s->py_args, 0, s->py_float);

	for (i = 0; i < n_signals; ++i) {
		struct signal_vector *v = &s->vectors[i];
		PyObject *signal = signals[i];

		if (PyFloat_Check(signal)) {
			const sample_t value = PyFloat_AS_DOUBLE(signal);
			size_t j;

			for (j = 0; j < SIGNAL_VECTOR_LEN; ++j)
				v->data[j] = value;

			v->signal = NULL;
		} else if (PyCallable_Check(signal)) {
			v->signal = splat_signal_func;
		} else if (PyObject_TypeCheck(signal, &splat_FragmentType)) {
			Fragment *sig_frag = (Fragment *)signal;

			if (sig_frag->n_channels != 1) {
				PyErr_SetString(PyExc_ValueError,
				"Fragment signal must have only 1 channel");
				return -1;
			}

			if (s->length > sig_frag->length) {
				PyErr_SetString(PyExc_ValueError,
				"Fragment signal length too short");
				return -1;
			}

			v->signal = splat_signal_frag;
		} else if (PyObject_TypeCheck(signal, &splat_SplineType)) {
			Spline *spline = (Spline *)signal;
			size_t spline_length = spline->end * rate;

			if (s->length > spline_length) {
				PyErr_SetString(PyExc_ValueError,
				"Spline signal length too short");
				return -1;
			}

			v->signal = splat_signal_spline;
		} else {
			PyErr_SetString(PyExc_TypeError,
					"unsupported signal type");
			return -1;
		}

		v->obj = signal;
	}

	s->cur = s->origin;
	s->end = 0;
	s->len = 0;
	s->stat = SIGNAL_VECTOR_CONTINUE;

	return 0;
}

static void splat_signal_free(struct splat_signal *s)
{
	Py_DECREF(s->py_float);
	Py_DECREF(s->py_args);
	PyMem_Free(s->vectors);
}

static int splat_signal_cache(struct splat_signal *s, size_t cur)
{
	size_t i;

	if (cur >= s->length)
		return SIGNAL_VECTOR_STOP;

	if ((cur == s->cur) && s->len)
		return SIGNAL_VECTOR_CONTINUE;

	s->cur = cur;
	s->end = min((s->cur + SIGNAL_VECTOR_LEN), s->length);
	s->len = s->end - s->cur;

	for (i = 0; i < s->n_vectors; ++i) {
		struct signal_vector *v = &s->vectors[i];

		if ((v->signal != NULL) && (v->signal(s, v)))
			return SIGNAL_VECTOR_ERROR;
	}

	return SIGNAL_VECTOR_CONTINUE;
}

static int splat_signal_next(struct splat_signal *s)
{
	s->stat = splat_signal_cache(s, (s->cur + s->len));

	return s->stat;
}

static ssize_t splat_signal_get(struct splat_signal *s, size_t n)
{
	div_t co; /* cursor, offset */
	size_t cur;

	if (n >= s->length)
		return -1;

	co = div(n, SIGNAL_VECTOR_LEN);
	cur = co.quot * SIGNAL_VECTOR_LEN;
	s->stat = splat_signal_cache(s, cur);

	if (s->stat != SIGNAL_VECTOR_CONTINUE)
		return -1;

	return co.rem;
}

static PyObject *splat_signal_tuple(struct splat_signal *s, size_t offset)
{
	PyObject *sig_tuple;
	size_t i;

	sig_tuple = PyTuple_New(s->n_vectors);

	if (sig_tuple == NULL)
		return NULL;

	for (i = 0; i < s->n_vectors; ++i) {
		PyObject *val = PyFloat_FromDouble(s->vectors[i].data[offset]);

		if (val == NULL) {
			Py_DECREF(sig_tuple);
			return NULL;
		}

		PyTuple_SET_ITEM(sig_tuple, i, val);
	}

	return sig_tuple;
}

/* ----------------------------------------------------------------------------
 * Fragment class
 */

/* -- internal functions -- */

struct splat_levels {
	unsigned n;
	PyObject *obj[MAX_CHANNELS];
	double fl[MAX_CHANNELS]; /* levels converted to linear scale */
	int all_floats;
};

struct splat_peak {
	double avg;
	double pos;
	double neg;
	double peak;
};

static int frag_get_levels(Fragment *frag, struct splat_levels *levels,
			   PyObject *levels_obj);
static int frag_resize(Fragment *self, size_t length);
#define frag_grow(_frag, _length)					\
	(((_length) <= (_frag)->length) ? 0 : frag_resize((_frag), (_length)))
static int frag_get_sample_number(size_t *val, long min_val, long max_val,
				  PyObject *obj);
static void frag_get_peak(Fragment *frag, struct splat_peak *chan_peak,
			  struct splat_peak *frag_peak, int do_avg);
static PyObject *splat_peak_dict(const struct splat_peak *peak);

/* -- Fragment functions -- */

static void Fragment_dealloc(Fragment *self)
{
	if (self->init) {
		unsigned i;

		for (i = 0; i < self->n_channels; ++i)
			PyMem_Free(self->data[i]);

		if (self->name != NULL)
			free((void *)self->name);

		self->init = 0;
	}

	self->ob_type->tp_free((PyObject *)self);
}

static int Fragment_init(Fragment *self, PyObject *args, PyObject *kw)
{
	static char *kwlist[] = {
		"channels", "rate", "duration", "length", "name", NULL };
	unsigned n_channels = 2;
	unsigned rate = 48000;
	double duration = 0.0;
	unsigned long length = 0;
	const char *name = NULL;

	unsigned i;
	size_t data_size;

	if (!PyArg_ParseTupleAndKeywords(args, kw, "|IIdkz", kwlist,
					 &n_channels, &rate, &duration,
					 &length, &name))
		return -1;

	if (n_channels > MAX_CHANNELS) {
		PyErr_SetString(PyExc_ValueError,
				"exceeding maximum number of channels");
		return -1;
	}

	if (!rate) {
		PyErr_SetString(PyExc_ValueError, "rate cannot be 0Hz");
		return -1;
	}

	if (duration < 0.0) {
		PyErr_SetString(PyExc_ValueError, "negative duration");
		return -1;
	}

	if (!length) {
		length = duration * rate;
	} else if (duration != 0.0) {
		PyErr_SetString(PyExc_ValueError,
				"cannot specify both length and duration");
		return -1;
	}

	data_size = length * sizeof(sample_t);

	for (i = 0; i < n_channels; ++i) {
		if (!data_size) {
			self->data[i] = NULL;
		} else {
			self->data[i] = PyMem_Malloc(data_size);

			if (self->data[i] == NULL) {
				PyErr_NoMemory();
				return -1;
			}

			memset(self->data[i], 0, data_size);
		}
	}

	if (name == NULL)
		self->name = NULL;
	else
		self->name = strdup(name);


	self->n_channels = n_channels;
	self->rate = rate;
	self->length = length;
	self->init = 1;

	return 0;
}

static PyObject *Fragment_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	Fragment *self;

	self = (Fragment *)type->tp_alloc(type, 0);

	if (self == NULL)
		return PyErr_NoMemory();

	self->init = 0;

	return (PyObject *)self;
}

/* Fragment sequence interface */

static Py_ssize_t Fragment_sq_length(Fragment *self)
{
	return self->length;
}

static PyObject *Fragment_sq_item(Fragment *self, Py_ssize_t i)
{
	PyObject *sample;
	unsigned c;

	if ((i < 0) || (i >= self->length)) {
		PyErr_SetString(PyExc_IndexError, "index out of range");
		return NULL;
	}

	sample = PyTuple_New(self->n_channels);

	if (sample == NULL)
		return NULL;

	for (c = 0; c < self->n_channels; ++c) {
		const sample_t s = self->data[c][i];
		PyTuple_SET_ITEM(sample, c, PyFloat_FromDouble(s));
	}

	return sample;
}

static int Fragment_sq_ass_item(Fragment *self, Py_ssize_t i, PyObject *v)
{
	unsigned c;

	if (!PyTuple_CheckExact(v)) {
		PyErr_SetString(PyExc_TypeError, "item must be a tuple");
		return -1;
	}

	if (PyTuple_GET_SIZE(v) != self->n_channels) {
		PyErr_SetString(PyExc_ValueError, "channels number mismatch");
		return -1;
	}

	if ((i < 0) || (i >= self->length)) {
		PyErr_SetString(PyExc_IndexError, "set index error");
		return -1;
	}

	for (c = 0; c < self->n_channels; ++c) {
		PyObject *s = PyTuple_GET_ITEM(v, c);

		if (!PyFloat_CheckExact(s)) {
			PyErr_SetString(PyExc_TypeError,
					"item must contain floats");
			return -1;
		}

		self->data[c][i] = (sample_t)PyFloat_AS_DOUBLE(s);
	}

	return 0;
}

static PySequenceMethods Fragment_as_sequence = {
	(lenfunc)Fragment_sq_length, /* sq_length */
	(binaryfunc)0, /* sq_concat */
	(ssizeargfunc)0, /* sq_repeat */
	(ssizeargfunc)Fragment_sq_item, /* sq_item */
	(ssizessizeargfunc)0, /* sq_slice */
	(ssizeobjargproc)Fragment_sq_ass_item, /* sq_ass_item */
	(ssizessizeobjargproc)0, /* sq_ass_slice */
	(objobjproc)0, /* sq_contains */
	(binaryfunc)0, /* sq_inplace_concat */
	(ssizeargfunc)0, /* sq_inplace_repeat */
};

/* Fragment getsetters */

PyDoc_STRVAR(rate_doc, "Get the sample rate in Hz.");

static PyObject *Fragment_get_rate(Fragment *self, void *_)
{
	return Py_BuildValue("I", self->rate);
}

PyDoc_STRVAR(duration_doc, "Get the fragment duration in seconds.");

static PyObject *Fragment_get_duration(Fragment *self, void *_)
{
	return Py_BuildValue("f", (double)self->length / self->rate);
}

PyDoc_STRVAR(channels_doc, "Get the number of channels.");

static PyObject *Fragment_get_channels(Fragment *self, void *_)
{
	return Py_BuildValue("I", self->n_channels);
}

PyDoc_STRVAR(name_doc, "Get and set the fragment name.");

static PyObject *Fragment_get_name(Fragment *self, void *_)
{
	if (self->name == NULL)
		Py_RETURN_NONE;

	return PyString_FromString(self->name);
}

static int Fragment_set_name(Fragment *self, PyObject *value, void *_)
{
	if (self->name != NULL)
		free((void *)self->name);

	if (!PyString_Check(value)) {
		PyErr_SetString(PyExc_TypeError,
				"Fragment name must be a string");
		return -1;
	}

	self->name = strdup(PyString_AS_STRING(value));

	return 0;
}

static PyGetSetDef Fragment_getsetters[] = {
	{ "rate", (getter)Fragment_get_rate, NULL, rate_doc },
	{ "duration", (getter)Fragment_get_duration, NULL, duration_doc },
	{ "channels", (getter)Fragment_get_channels, NULL, channels_doc },
	{ "name", (getter)Fragment_get_name, (setter)Fragment_set_name,
	  name_doc },
	{ NULL }
};

/* Fragment methods */

static void splat_import_float64(sample_t *out, const char *in, size_t n,
				 size_t step)
{
	while (n--) {
		*out++ = *(const double *)in;
		in += step;
	}
}

static void splat_export_float64(char *out, const sample_t **in,
				 unsigned channels, size_t n)
{
	double *out64 = (double *)out;

	while (n--) {
		unsigned c;

		for (c = 0; c < channels; ++c)
			*out64++ = *(in[c]++);
	}
}

static void splat_import_float32(sample_t *out, const char *in, size_t n,
				 size_t step)
{
	while (n--) {
		*out++ = *(const float *)in;
		in += step;
	}
}

static void splat_export_float32(char *out, const sample_t **in,
				 unsigned channels, size_t n)
{
	float *out32 = (float *)out;

	while (n--) {
		unsigned c;

		for (c = 0; c < channels; ++c)
			*out32++ = *(in[c]++);
	}
}

static void splat_import_int24(sample_t *out, const char *in, size_t n,
			       size_t step)
{
	static const int32_t neg24 = 1 << 23;
	static const int32_t neg_mask32 = 0xFF000000;
	static const sample_t scale = (1 << 23) - 1;

	while (n--) {
		const uint8_t *in8 = (const uint8_t *)in;
		int32_t sample32;

		sample32 = *in8++;
		sample32 += (*in8++) << 8;
		sample32 += (*in8++) << 16;

		if (sample32 & neg24)
			sample32 |= neg_mask32;

		*out++ = sample32 / scale;
		in += step;
	}
}

static void splat_export_int24(char *out, const sample_t **in,
			       unsigned channels, size_t n)
{
	static const int32_t scale = (1 << 23) - 1;

	while (n--) {
		unsigned c;

		for (c = 0; c < channels; ++c) {
			const sample_t z = *(in[c]++);
			int32_t s;

			if (z < -1.0)
				s = -scale;
			else if (z > 1.0)
				s = scale;
			else
				s = z * scale;

			*out++ = s & 0xFF;
			*out++ = (s >> 8) & 0xFF;
			*out++ = (s >> 16) & 0xFF;
		}
	}
}

static void splat_import_int16(sample_t *out, const char *in, size_t n,
			       size_t step)
{
	static const sample_t scale = (1 << 15) - 1;

	while (n--) {
		*out++ = *(int16_t *)in / scale;
		in += step;
	}
}

static void splat_export_int16(char *out, const sample_t **in,
			       unsigned channels, size_t n)
{
	static const long scale = (1 << 15) - 1;

	while (n--) {
		unsigned c;

		for (c = 0; c < channels; ++c) {
			const sample_t z = *(in[c]++);
			int16_t s;

			if (z < -1.0)
				s = -scale;
			else if (z > 1.0)
				s = scale;
			else
				s = z * scale;

			*out++ = s & 0xFF;
			*out++ = (s >> 8) & 0xFF;
		}
	}
}

static void splat_import_int8(sample_t *out, const char *in, size_t n,
			      size_t step)
{
	static const sample_t scale = 127.0;

	while (n--) {
		*out++ = *(int8_t *)in / scale;
		in += step;
	}
}

static void splat_export_int8(char *out, const sample_t **in,
			      unsigned channels, size_t n)
{
	while (n--) {
		unsigned c;

		for (c = 0; c < channels; ++c) {
			const sample_t z = (*in[c]++);
			int8_t s;

			if (z < -1.0)
				s = 0;
			else if (z > 1.0)
				s = 255;
			else
				s = z * 127.0;

			*out++ = s;
		}
	}
}

static const struct splat_raw_io splat_raw_io_table[] = {
	{ SPLAT_FLOAT_64, 64, splat_import_float64, splat_export_float64 },
	{ SPLAT_FLOAT_32, 32, splat_import_float32, splat_export_float32 },
	{ SPLAT_INT_24, 24, splat_import_int24, splat_export_int24, },
	{ SPLAT_INT_16, 16, splat_import_int16, splat_export_int16, },
	{ SPLAT_INT_8, 8, splat_import_int8, splat_export_int8 },
};

static const struct splat_raw_io *splat_get_raw_io(const char *sample_type)
{
	const struct splat_raw_io *it;
	const struct splat_raw_io * const end =
		&splat_raw_io_table[ARRAY_SIZE(splat_raw_io_table)];

	for (it = splat_raw_io_table; it != end; ++it)
		if (!strcmp(sample_type, it->sample_type))
			return it;

	PyErr_SetString(PyExc_ValueError, "unsupported sample type");

	return NULL;
}

PyDoc_STRVAR(Fragment_import_bytes_doc,
"import_bytes(raw_bytes, rate, channels, sample_type=splat.SAMPLE_TYPE, "
"offset=None, start=None, end=None)\n"
"\n"
"Import data as raw bytes.\n"
"\n"
"The ``sample_type`` gives the format of the raw data to import as samples, "
":ref:`sample_formats` for more details. "
"The ``rate`` and ``channels`` need to match the Fragment instance values. "
"The ``offset`` argument can be used as a sample number to specify the point "
"where the data starts to be imported into the fragment. "
"The ``start`` and ``end`` arguments can be defined as sample numbers to "
"import only a subset of the data.\n");

static PyObject *Fragment_import_bytes(Fragment *self, PyObject *args,
				       PyObject *kw)
{
	static char *kwlist[] = {
		"raw_bytes", "rate", "channels", "sample_type",
		"offset", "start", "end", NULL };
	PyObject *bytes_obj;
	unsigned rate;
	unsigned n_channels;
	const char *sample_type = SPLAT_NATIVE_SAMPLE_TYPE;
	PyObject *offset_obj = Py_None;
	PyObject *start_obj = Py_None;
	PyObject *end_obj = Py_None;

	size_t sample_size;
	size_t bytes_size;
	size_t frame_size;
	size_t bytes_length;
	const struct splat_raw_io *io;
	size_t offset;
	size_t start;
	size_t end;
	size_t length;
	const char *bytes;
	unsigned c;

	if (!PyArg_ParseTupleAndKeywords(args, kw, "O!II|sOOO", kwlist,
					 &PyByteArray_Type, &bytes_obj, &rate,
					 &n_channels, &sample_type,
					 &offset_obj, &start_obj, &end_obj))
		return NULL;

	if (rate != self->rate) {
		PyErr_SetString(PyExc_ValueError, "wrong sample rate");
		return NULL;
	}

	if (n_channels != self->n_channels) {
		PyErr_SetString(PyExc_ValueError, "wrong number of channels");
		return NULL;
	}

	io = splat_get_raw_io(sample_type);

	if (io == NULL)
		return NULL;

	bytes_size = PyByteArray_Size(bytes_obj);
	sample_size = io->sample_width / 8;
	frame_size = sample_size * n_channels;
	bytes_length = bytes_size / frame_size;

	if (bytes_size % frame_size) {
		PyErr_SetString(PyExc_ValueError,
				"buffer length not multiple of frame size");
		return NULL;
	}

	if (offset_obj == Py_None)
		offset = 0;
	else if (frag_get_sample_number(&offset, 0, LONG_MAX, offset_obj))
		return NULL;

	if (start_obj == Py_None)
		start = 0;
	else if (frag_get_sample_number(&start, 0, bytes_length, start_obj))
		return NULL;

	if (end_obj == Py_None)
		end = bytes_length;
	else if (frag_get_sample_number(&end, start, bytes_length, end_obj))
		return NULL;

	length = end - start;

	if (frag_grow(self, (offset + length)))
		return NULL;

	bytes = PyByteArray_AsString(bytes_obj);

	for (c = 0; c < self->n_channels; ++c) {
		const char *in =
			bytes + (start * frame_size) + (c * sample_size);
		sample_t *out = &self->data[c][offset];

		io->import(out, in, length, frame_size);
	}

	Py_RETURN_NONE;
}

PyDoc_STRVAR(Fragment_export_bytes_doc,
"export_bytes(sample_type=splat.SAMPLE_TYPE, start=None, end=None)\n"
"\n"
"Export audio data as raw bytes.\n"
"\n"
"The ``sample_type`` is a string to specify the format of the exported "
"samples.  See :ref:`sample_formats` for more details.\n"
"\n"
"The ``start`` and ``end`` arguments can be specified in sample numbers to "
"only get a subset of the data.\n"
"\n"
"A ``bytearray`` object is then returned with the exported sample data.\n");

static PyObject *Fragment_export_bytes(Fragment *self, PyObject *args,
				       PyObject *kw)
{
	static char *kwlist[] = { "sample_type", "start", "end", NULL };
	const char *sample_type = SPLAT_NATIVE_SAMPLE_TYPE;
	PyObject *start_obj = Py_None;
	PyObject *end_obj = Py_None;

	const struct splat_raw_io *io;
	size_t sample_size;
	size_t frame_size;
	size_t start;
	size_t end;
	size_t length;
	unsigned c;
	PyObject *bytes_obj;
	Py_ssize_t bytes_size;
	char *out;
	const sample_t *in[MAX_CHANNELS];

	if (!PyArg_ParseTupleAndKeywords(args, kw, "|sOO", kwlist,
					 &sample_type, &start_obj, &end_obj))
		return NULL;

	io = splat_get_raw_io(sample_type);

	if (io == NULL)
		return NULL;

	sample_size = io->sample_width / 8;
	frame_size = sample_size * self->n_channels;

	if (start_obj == Py_None)
		start = 0;
	else if (frag_get_sample_number(&start, 0, self->length, start_obj))
		return NULL;

	if (end_obj == Py_None)
		end = self->length;
	else if (frag_get_sample_number(&end, start, self->length, end_obj))
		return NULL;

	length = end - start;
	bytes_size = length * frame_size;
	bytes_obj = PyByteArray_FromStringAndSize(NULL, bytes_size);

	if (bytes_obj == NULL)
		return PyErr_NoMemory();

	out = PyByteArray_AS_STRING(bytes_obj);

	for (c = 0; c < self->n_channels; ++c)
		in[c] = &self->data[c][start];

	io->export(out, in, self->n_channels, length);

	return bytes_obj;
}

static void frag_mix_floats(Fragment *self, const Fragment *frag,
			    size_t offset, size_t start, size_t length,
			    const double *levels, int zero_dB)
{
	unsigned c;

	for (c = 0; c < self->n_channels; ++c) {
		const sample_t *src = &frag->data[c][start];
		sample_t *dst =  &self->data[c][offset];
		Py_ssize_t i = length;

		if (zero_dB) {
			while (i--)
				*dst++ += *src++;
		} else {
			const double g = levels[c];

			while (i--)
				*dst++ += g * (*src++);
		}
	}
}

static int frag_mix_signals(Fragment *self, const Fragment *frag,
			    size_t offset, size_t start, size_t length,
			    const struct splat_levels *levels)
{
	struct splat_signal sig;
	PyObject *signals[MAX_CHANNELS];
	unsigned c;
	size_t in;
	size_t i;

	for (c = 0; c < frag->n_channels; ++c)
		signals[c] = levels->obj[c];

	if (splat_signal_init(&sig, length, offset, signals, self->n_channels,
			      self->rate))
		return -1;

	in = sig.cur;
	i = 0;

	while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
		size_t j;

		for (j = 0; j < sig.len; ++i, ++j, ++in) {
			for (c = 0; c < frag->n_channels; ++c) {
				double a = dB2lin(sig.vectors[c].data[j]);

				self->data[c][i] += frag->data[c][in] * a;
			}
		}
	}

	splat_signal_free(&sig);

	return (sig.stat == SIGNAL_VECTOR_ERROR) ? -1 : 0;
}

PyDoc_STRVAR(Fragment_mix_doc,
"mix(fragment, offset=0.0, skip=0.0, levels=None, duration=None)\n"
"\n"
"Mix the given other ``fragment`` data into this instance.\n"
"\n"
"This is achieved by simply adding the corresponding samples of an incoming "
"fragment to this fragment' samples.  The ``offset``, ``skip`` and "
"``duration`` values in seconds can be used to alter the mixing times.  The "
"incoming fragment can start being mixed with an ``offset`` into this "
"fragment, its beginning can be skipped until the given ``skip`` time, and "
"the ``duration`` to be mixed can be manually limited.  These values will be "
"automatically adjusted to remain within the available incoming data.  The "
"length of this fragment will be automatically increased if necessary to hold "
"the mixed data.\n"
"\n"
"The ``levels`` argument can be used to alter the amplitude of the incoming "
"fragment as gain signals while mixing - this does not affect it directly.\n"
"\n"
"Please note that the two fragments must use the same sample rate and have "
"the same number of channels.\n");

static PyObject *Fragment_mix(Fragment *self, PyObject *args, PyObject *kw)
{
	static char *kwlist[] = {
		"frag", "offset", "skip", "levels", "duration", NULL };
	Fragment *frag;
	double offset = 0.0;
	double skip = 0.0;
	PyObject *levels_obj = Py_None;
	PyObject *duration_obj = Py_None;

	struct splat_levels levels;
	ssize_t length;
	ssize_t offset_sample;
	ssize_t skip_sample;
	size_t total_length;

	if (!PyArg_ParseTupleAndKeywords(args, kw, "O!|ddOO", kwlist,
					 &splat_FragmentType, &frag, &offset,
					 &skip, &levels_obj, &duration_obj))
		return NULL;

	if (frag->n_channels != self->n_channels) {
		PyErr_SetString(PyExc_ValueError, "channels number mismatch");
		return NULL;
	}

	if (frag->rate != self->rate) {
		PyErr_SetString(PyExc_ValueError, "sample rate mismatch");
		return NULL;
	}

	if (levels_obj == Py_None)
		levels_obj = splat_zero;

	if (frag_get_levels(self, &levels, levels_obj))
		return NULL;

	if (duration_obj != Py_None) {
		if (!PyFloat_Check(duration_obj)) {
			PyErr_SetString(PyExc_ValueError,
					"duration must be float");
			return NULL;
		}

		length = PyFloat_AS_DOUBLE(duration_obj) * self->rate;
	} else {
		length = frag->length;
	}

	offset_sample = offset * self->rate;
	offset_sample = max(offset_sample, 0);
	skip_sample = skip * self->rate;
	skip_sample = minmax(skip_sample, 0, frag->length);
	length = minmax(length, 0, (frag->length - skip_sample));
	total_length = offset_sample + length;

	if (frag_grow(self, total_length))
		return NULL;

	if (levels.all_floats)
		frag_mix_floats(self, frag, offset_sample, skip_sample,
				length, levels.fl, levels_obj == splat_zero);
	else if (frag_mix_signals(self, frag, offset_sample, skip_sample,
				  length, &levels))
		return NULL;

	Py_RETURN_NONE;
}

PyDoc_STRVAR(Fragment_get_peak_doc,
"get_peak()\n"
"\n"
"Get peak and average values for the whole fragment and for each channel.\n"
"\n"
"Scan all the data and look for the peak maximum, minimum and absolute values "
"as well as the average values for each channel and for the whole fragment. "
"The results are returned as a 2-tuple, the first item being for the whole "
"fragment and the second one a list with each channel.  Both results are "
"contained in a dictionary with ``pos``, ``neg``, ``peak`` and ``avg`` values "
"respectively for positive, negative, absolute peak and average values.\n");

static PyObject *Fragment_get_peak(Fragment *self, PyObject *_)
{
	struct splat_peak chan_peak[MAX_CHANNELS];
	struct splat_peak frag_peak;
	unsigned c;

	PyObject *ret;
	PyObject *frag_peak_obj;
	PyObject *chan_peak_obj;

	frag_get_peak(self, chan_peak, &frag_peak, 1);

	frag_peak_obj = splat_peak_dict(&frag_peak);

	if (frag_peak_obj == NULL)
		return PyErr_NoMemory();

	chan_peak_obj = PyList_New(self->n_channels);

	if (chan_peak_obj == NULL)
		return PyErr_NoMemory();

	for (c = 0; c < self->n_channels; ++c) {
		PyObject *peak_dict = splat_peak_dict(&chan_peak[c]);

		if (peak_dict == NULL)
			return PyErr_NoMemory();

		PyList_SET_ITEM(chan_peak_obj, c, peak_dict);
	}

	ret = Py_BuildValue("(OO)", frag_peak_obj, chan_peak_obj);
	Py_DECREF(frag_peak_obj);
	Py_DECREF(chan_peak_obj);

	return ret;
}

PyDoc_STRVAR(Fragment_normalize_doc,
"normalize(level=-0.05, zero=True)\n"
"\n"
"Normalize the amplitude.\n"
"\n"
"The ``level`` value in dB is the resulting maximum amplitude after "
"normalization.  The default value of -0.05 dB is the maximum level while "
"ensuring no clipping occurs due to rounding errors, even when saving with "
"8-bit sample resolution. "
"The same gain is applied to all channels, so the relative difference in "
"levels between channels is preserved.\n"
"\n"
"When ``zero`` is ``True``, the average value is substracted from all the "
"fragment prior to amplification to avoid any offset and achieve maximum "
"amplitude.  With some imbalanced transitory signals, it may be better to not "
"remove the average value as this may have the undesirable effect of adding "
"some offset instead.\n");

static PyObject *Fragment_normalize(Fragment *self, PyObject *args)
{
	double level = -0.05;
	PyObject *zero = NULL;

	int do_zero;
	struct splat_peak chan_peak[MAX_CHANNELS];
	struct splat_peak frag_peak;
	unsigned c;
	double gain;

	if (!PyArg_ParseTuple(args, "|dO!", &level, &PyBool_Type, &zero))
		return NULL;

	if (self->n_channels > MAX_CHANNELS) {
		PyErr_SetString(PyExc_ValueError, "too many channels");
		return NULL;
	}

	level = dB2lin(level);
	do_zero = ((zero == NULL) || (zero == Py_True)) ? 1 : 0;
	frag_get_peak(self, chan_peak, &frag_peak, do_zero);

	if (do_zero) {
		double offset = 0.0;

		for (c = 0; c < self->n_channels; ++c) {
			const double avg = chan_peak[c].avg;

			if (fabs(offset) < fabs(avg))
				offset = avg;
		}

		gain = level / (frag_peak.peak + fabs(offset));
	} else {
		gain = level / frag_peak.peak;
	}

	if ((1.0 < gain) && (gain < 1.001)) {
		int zero;

		if (!do_zero)
			Py_RETURN_NONE;

		for (c = 0, zero = 1; c < self->n_channels && zero; ++c)
			if (fabs(chan_peak[c].avg) > 0.001)
				zero = 0;

		if (zero)
			Py_RETURN_NONE;
	}

	for (c = 0; c < self->n_channels; ++c) {
		const double chan_avg = chan_peak[c].avg;
		sample_t * const chan_data = self->data[c];
		const sample_t * const end = &chan_data[self->length];
		sample_t *it;

		for (it = chan_data; it != end; ++it) {
			*it -= chan_avg;
			*it *= gain;
		}
	}

	Py_RETURN_NONE;
}

static void frag_amp_floats(Fragment *self, const double *gains)
{
	unsigned c;

	for (c = 0; c < self->n_channels; ++c) {
		const double g = gains[c];
		size_t i;

		if (g == 1.0)
			continue;

		for (i = 0; i < self->length; ++i)
			self->data[c][i] *= g;
	}
}

static int frag_amp_signals(Fragment *self, const struct splat_levels *gains)
{
	struct splat_signal sig;
	PyObject *signals[MAX_CHANNELS];
	unsigned c;
	size_t in;
	size_t i;

	for (c = 0; c < self->n_channels; ++c)
		signals[c] = gains->obj[c];

	if (splat_signal_init(&sig, self->length, 0.0, signals,
			      self->n_channels, self->rate))
		return -1;

	in = sig.cur;
	i = 0;

	while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
		size_t j;

		for (j = 0; j < sig.len; ++i, ++j, ++in) {
			for (c = 0; c < self->n_channels; ++c) {
				double g = dB2lin(sig.vectors[c].data[j]);

				self->data[c][i] *= g;
			}
		}
	}

	splat_signal_free(&sig);

	return (sig.stat == SIGNAL_VECTOR_ERROR) ? -1 : 0;
}

PyDoc_STRVAR(Fragment_amp_doc,
"amp(gain)\n"
"\n"
"Amplify the fragment by the given ``gain`` in dB which can either be a "
"single floating point value to apply to all channels or a tuple with a value "
"for each individual channel.\n");

static PyObject *Fragment_amp(Fragment *self, PyObject *args)
{
	PyObject *gain_obj;

	struct splat_levels gains;

	if (!PyArg_ParseTuple(args, "O", &gain_obj))
		return NULL;

	if (frag_get_levels(self, &gains, gain_obj))
		return NULL;

	if (gains.all_floats)
		frag_amp_floats(self, gains.fl);
	else if (frag_amp_signals(self, &gains))
		return NULL;

	Py_RETURN_NONE;
}

PyDoc_STRVAR(Fragment_offset_doc,
"offset(value, start=0.0)\n"
"\n"
"Add an offset to the data already in the fragment starting at the ``start`` "
"time in seconds.  This is especially useful when generating a modulation "
"fragment.\n");

static PyObject *Fragment_offset(Fragment *self, PyObject *args)
{
	PyObject *offset;
	double start = 0.0;

	unsigned c;
	size_t i;

	if (!PyArg_ParseTuple(args, "O|d", &offset, &start))
		return NULL;

	if (PyFloat_Check(offset)) {
		const double offset_float = PyFloat_AS_DOUBLE(offset);

		for (c = 0; c < self->n_channels; ++c) {
			for (i = 0; i < self->length; ++i)
				self->data[c][i] += offset_float;
		}
	} else {
		struct splat_signal sig;

		if (splat_signal_init(&sig, self->length, (start * self->rate),
				      &offset, 1, self->rate))
			return NULL;

		i = 0;

		while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
			size_t j;

			for (j = 0; j < sig.len; ++i, ++j) {
				const double value = sig.vectors[0].data[j];

				for (c = 0; c < self->n_channels; ++c)
					self->data[c][i] += value;
			}
		}

		splat_signal_free(&sig);

		if (sig.stat == SIGNAL_VECTOR_ERROR)
			return NULL;
	}

	Py_RETURN_NONE;
}

PyDoc_STRVAR(Fragment_resize_doc,
"resize(duration=0.0, length=0)\n"
"\n"
"Resize the fragment to the given ``duration`` in seconds or ``length`` in "
"number of samples per channel.  If the fragment grows, silence is added at "
"the end.  When shrinking, the end of the fragment is lost.\n");

static PyObject *Fragment_resize(Fragment *self, PyObject *args, PyObject *kw)
{
	static char *kwlist[] = { "duration", "length", NULL };
	double duration = 0.0;
	unsigned long length = 0;

	if (!PyArg_ParseTupleAndKeywords(args, kw, "|dk", kwlist,
					 &duration, &length))
		return NULL;

	if (duration < 0.0) {
		PyErr_SetString(PyExc_ValueError, "negative duration");
		return NULL;
	}

	if (!length) {
		length = duration * self->rate;
	} else if (duration != 0.0) {
		PyErr_SetString(PyExc_ValueError,
				"cannot specify both length and duration");
		return NULL;
	}

	if (frag_resize(self, length))
		return NULL;

	Py_RETURN_NONE;
}

static PyMethodDef Fragment_methods[] = {
	{ "import_bytes", (PyCFunction)Fragment_import_bytes, METH_KEYWORDS,
	  Fragment_import_bytes_doc },
	{ "export_bytes", (PyCFunction)Fragment_export_bytes, METH_KEYWORDS,
	  Fragment_export_bytes_doc },
	{ "mix", (PyCFunction)Fragment_mix, METH_KEYWORDS,
	  Fragment_mix_doc },
	{ "get_peak", (PyCFunction)Fragment_get_peak, METH_NOARGS,
	  Fragment_get_peak_doc },
	{ "normalize", (PyCFunction)Fragment_normalize, METH_VARARGS,
	  Fragment_normalize_doc },
	{ "amp", (PyCFunction)Fragment_amp, METH_VARARGS,
	  Fragment_amp_doc },
	{ "offset", (PyCFunction)Fragment_offset, METH_VARARGS,
	  Fragment_offset_doc },
	{ "resize", (PyCFunction)Fragment_resize, METH_KEYWORDS,
	  Fragment_resize_doc },
	{ NULL }
};

static PyTypeObject splat_FragmentType = {
	PyObject_HEAD_INIT(NULL)
	0,                                 /* ob_size */
	"_splat.Fragment",                 /* tp_name */
	sizeof(Fragment),                  /* tp_basicsize */
	0,                                 /* tp_itemsize */
	(destructor)Fragment_dealloc,      /* tp_dealloc */
	0,                                 /* tp_print */
	0,                                 /* tp_getattr */
	0,                                 /* tp_setattr */
	0,                                 /* tp_compare */
	0,                                 /* tp_repr */
	0,                                 /* tp_as_number */
	&Fragment_as_sequence,             /* tp_as_sequence */
	0,                                 /* tp_as_mapping */
	0,                                 /* tp_hash  */
	0,                                 /* tp_call */
	0,                                 /* tp_str */
	0,                                 /* tp_getattro */
	0,                                 /* tp_setattro */
	0,                                 /* tp_as_buffer */
	BASE_TYPE_FLAGS,                   /* tp_flags */
	"Fragment of audio data",          /* tp_doc */
	0,                                 /* tp_traverse */
	0,                                 /* tp_clear */
	0,                                 /* tp_richcompare */
	0,                                 /* tp_weaklistoffset */
	0,                                 /* tp_iter */
	0,                                 /* tp_iternext */
	Fragment_methods,                  /* tp_methods */
	0,                                 /* tp_members */
	Fragment_getsetters,               /* tp_getset */
	0,                                 /* tp_base */
	0,                                 /* tp_dict */
	0,                                 /* tp_descr_get */
	0,                                 /* tp_descr_set */
	0,                                 /* tp_dictoffset */
	(initproc)Fragment_init,           /* tp_init */
	0,                                 /* tp_alloc */
	Fragment_new,                      /* tp_new */
};

/* -- Fragment internal functions -- */

static void frag_get_levels_float(Fragment *frag, struct splat_levels *levels,
				  PyObject *levels_obj, double gain_log)
{
	const double gain_lin = dB2lin(gain_log);
	unsigned c;

	levels->n = frag->n_channels;
	levels->all_floats = 1;

	for (c = 0; c < frag->n_channels; ++c) {
		levels->obj[c] = levels_obj;
		levels->fl[c] = gain_lin;
	}
}

static int frag_get_levels_tuple(Fragment *frag, struct splat_levels *levels,
				 PyObject *levels_obj)
{
	const Py_ssize_t n_channels = PyTuple_GET_SIZE(levels_obj);
	unsigned c;

	if (n_channels > MAX_CHANNELS) {
		PyErr_SetString(PyExc_ValueError, "too many channels");
		return -1;
	}

	if (n_channels != frag->n_channels) {
		PyErr_SetString(PyExc_ValueError, "channels number mismatch");
		return -1;
	}

	levels->n = n_channels;
	levels->all_floats = 1;

	for (c = 0; c < n_channels; ++c) {
		levels->obj[c] = PyTuple_GetItem(levels_obj, c);

		if (levels->all_floats) {
			double level_dB;

			if (!splat_obj2double(levels->obj[c], &level_dB))
				levels->fl[c] = dB2lin(level_dB);
			else
				levels->all_floats = 0;
		}
	}

	return 0;
}

static void frag_get_levels_signal(Fragment *frag, struct splat_levels *levels,
				   PyObject *levels_obj)
{
	unsigned c;

	levels->n = frag->n_channels;
	levels->all_floats = 0;

	for (c = 0; c < frag->n_channels; ++c)
		levels->obj[c] = levels_obj;
}

static int frag_get_levels(Fragment *frag, struct splat_levels *levels,
			   PyObject *levels_obj)
{
	double gain_log;
	int res = 0;

	if (!splat_obj2double(levels_obj, &gain_log))
		frag_get_levels_float(frag, levels, levels_obj, gain_log);
	else if (PyTuple_Check(levels_obj))
		res = frag_get_levels_tuple(frag, levels, levels_obj);
	else
		frag_get_levels_signal(frag, levels, levels_obj);

	return res;
}

static int frag_resize(Fragment *frag, size_t length)
{
	const size_t start = frag->length * sizeof(sample_t);
	const size_t size = length * sizeof(sample_t);
	const ssize_t extra = size - start;
	unsigned c;

	for (c = 0; c < frag->n_channels; ++c) {
		if (frag->data[c] == NULL)
			frag->data[c] = PyMem_Malloc(size);
		else
			frag->data[c] = PyMem_Realloc(frag->data[c], size);

		if (frag->data[c] == NULL) {
			PyErr_NoMemory();
			return -1;
		}

		if (extra > 0)
			memset(&frag->data[c][frag->length], 0, extra);
	}

	frag->length = length;

	return 0;
}

static int frag_get_sample_number(size_t *val, long min_val, long max_val,
				  PyObject *obj)
{
	long tmp_val;

	if (!PyInt_Check(obj)) {
		PyErr_SetString(PyExc_TypeError,
				"sample number must be an integer");
		return -1;
	}

	tmp_val = min(PyInt_AsLong(obj), max_val);
	*val = max(tmp_val, min_val);

	return 0;
}

static void frag_get_peak(Fragment *frag, struct splat_peak *chan_peak,
			  struct splat_peak *frag_peak, int do_avg)
{
	unsigned c;

	frag_peak->avg = 0.0;
	frag_peak->pos = -1.0;
	frag_peak->neg = 1.0;
	frag_peak->peak = 0.0;

	for (c = 0; c < frag->n_channels; ++c) {
		sample_t * const chan_data = frag->data[c];
		const sample_t * const end = &chan_data[frag->length];
		const sample_t *it;
		double avg = 0.0;
		double pos = -1.0;
		double neg = 1.0;

		for (it = chan_data; it != end; ++it) {
			if (do_avg)
				avg += *it / frag->length;

			if (*it > pos)
				pos = *it;
			else if (*it < neg)
				neg = *it;
		}

		chan_peak[c].avg = avg;
		chan_peak[c].pos = pos;
		chan_peak[c].neg = neg;

		if (do_avg)
			frag_peak->avg += avg / frag->n_channels;

		if (pos > frag_peak->pos)
			frag_peak->pos = pos;

		if (neg < frag_peak->neg)
			frag_peak->neg = neg;

		neg = fabsf(neg);
		pos = fabsf(pos);
		chan_peak[c].peak = (neg > pos) ? neg : pos;

		if (frag_peak->peak < chan_peak[c].peak)
			frag_peak->peak = chan_peak[c].peak;
	}
}

static PyObject *splat_peak_dict(const struct splat_peak *peak)
{
	return Py_BuildValue("{sdsdsdsd}", "avg", peak->avg, "pos", peak->pos,
			     "neg", peak->neg, "peak", peak->peak);
}


/* ----------------------------------------------------------------------------
 * _splat methods
 */

PyDoc_STRVAR(splat_lin2dB_doc,
"lin2dB(value)\n"
"\n"
"Convert floating point linear ``value`` to dB.\n");

static PyObject *splat_lin2dB(PyObject *self, PyObject *args)
{
	double level;

	if (!PyArg_ParseTuple(args, "d", &level))
		return NULL;

	return PyFloat_FromDouble(lin2dB(level));
}

PyDoc_STRVAR(splat_dB2lin_doc,
"dB2lin(value)\n"
"\n"
"Convert floating point dB ``value`` to linear.\n");

static PyObject *splat_dB2lin(PyObject *self, PyObject *args)
{
	double dB;

	if (!PyArg_ParseTuple(args, "d", &dB))
		return NULL;

	return PyFloat_FromDouble(dB2lin(dB));
}

PyDoc_STRVAR(splat_gen_ref_doc,
"gen_ref(frag)\n"
"\n"
"Generate a reference signal into a single channel fragment."
"\n"
"This is useful mainly for benchmarks and test purposes.\n");

static PyObject *splat_gen_ref(PyObject *self, PyObject *args)
{
	Fragment *frag;
	sample_t *data;
	size_t n;
	size_t i;

	if (!PyArg_ParseTuple(args, "O!", &splat_FragmentType, &frag))
		return NULL;

	if (frag->n_channels != 1) {
		PyErr_SetString(PyExc_ValueError,
				"fragment must have a single channel");
		return NULL;
	}

	if (frag->length == 0) {
		PyErr_SetString(PyExc_ValueError,
				"fragment length must be greater than 0");
		return NULL;
	}

	data = frag->data[0];
	n = frag->length;

	for (i = 0; i < n; ++i)
		*data++ = i / n;

	Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
 * Sources
 */

/* -- helpers for sources -- */

#define splat_check_all_floats(...)			\
	_splat_check_all_floats(PP_NARG(__VA_ARGS__), __VA_ARGS__)

static int _splat_check_all_floats(size_t n, ...)
{
	va_list objs;
	size_t i;

	va_start(objs, n);

	for (i = 0; i < n; ++i) {
		PyObject *obj = va_arg(objs, PyObject *);

		if (!PyFloat_Check(obj))
			break;
	}

	va_end(objs);

	return (i == n);
}

/* -- sine source -- */

static void splat_sine_floats(Fragment *frag, const double *levels,
			      double freq, double phase)
{
	const double k = 2 * M_PI * freq / frag->rate;
	const long ph = phase * frag->rate;
	size_t i;

	for (i = 0; i < frag->length; ++i) {
		const double s = sin(k * (i + ph));
		unsigned c;

		for (c = 0; c < frag->n_channels; ++c)
			frag->data[c][i] = s * levels[c];
	}
}

static int splat_sine_signals(Fragment *frag, PyObject **levels,
			      PyObject *freq, PyObject *phase, double origin)
{
	enum {
		SIG_FREQ = 0,
		SIG_PHASE,
		SIG_AMP,
	};
	static const double k = 2 * M_PI;
	struct splat_signal sig;
	PyObject *signals[SIG_AMP + MAX_CHANNELS];
	unsigned c;
	size_t i;

	signals[SIG_FREQ] = freq;
	signals[SIG_PHASE] = phase;

	for (c = 0; c < frag->n_channels; ++c)
		signals[SIG_AMP + c] = levels[c];

	if (splat_signal_init(&sig, frag->length, (origin * frag->rate),
			      signals, (SIG_AMP + frag->n_channels),
			      frag->rate))
		return -1;

	i = 0;

	while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
		size_t j;

		for (j = 0; j < sig.len; ++i, ++j) {
			const double t = (double)i / frag->rate;
			const double f = sig.vectors[SIG_FREQ].data[j];
			const double ph = sig.vectors[SIG_PHASE].data[j];
			const double s = sin(k * f * (t + ph + origin));

			for (c = 0; c < frag->n_channels; ++c) {
				const double a =
					sig.vectors[SIG_AMP + c].data[j];

				frag->data[c][i] = s * dB2lin(a);
			}
		}
	}

	splat_signal_free(&sig);

	return (sig.stat == SIGNAL_VECTOR_ERROR) ? -1 : 0;
}

PyDoc_STRVAR(splat_sine_doc,
"sine(fragment, levels, frequency, phase=0.0, origin=0.0)\n"
"\n"
"Generate a sine wave for the given ``levels``, ``frequency`` and ``phase`` "
"signals over the entire ``fragment`` with the give ``origin`` in time.\n");

static PyObject *splat_sine(PyObject *self, PyObject *args)
{
	Fragment *frag;
	PyObject *levels_obj;
	PyObject *freq;
	PyObject *phase = splat_zero;
	double origin = 0.0;

	struct splat_levels levels;
	int all_floats;


	if (!PyArg_ParseTuple(args, "O!OO|Od", &splat_FragmentType, &frag,
			      &levels_obj, &freq, &phase, &origin))
		return NULL;

	if (frag_get_levels(frag, &levels, levels_obj))
		return NULL;

	all_floats = levels.all_floats && splat_check_all_floats(freq, phase);

	if (all_floats)
		splat_sine_floats(frag, levels.fl, PyFloat_AS_DOUBLE(freq),
				  PyFloat_AS_DOUBLE(phase) + origin);
	else if (splat_sine_signals(frag, levels.obj, freq, phase, origin))
		return NULL;

	Py_RETURN_NONE;
}

/* -- square source -- */

static void splat_square_floats(Fragment *frag, const double *fl_pos,
				double freq, double phase, double ratio)
{
	const double k = freq / frag->rate;
	const double ph0 = freq * phase;
	double fl_neg[MAX_CHANNELS];
	unsigned c;
	Py_ssize_t i;

	ratio = min(ratio, 1.0);
	ratio = max(ratio, 0.0);

	for (c = 0; c < frag->n_channels; ++c)
		fl_neg[c] = -fl_pos[c];

	for (i = 0; i < frag->length; ++i) {
		double n_periods;
		const double t_rel = modf(((i * k) + ph0), &n_periods);
		const double *levels;

		if (t_rel < ratio)
			levels = fl_pos;
		else
			levels = fl_neg;

		for (c = 0; c < frag->n_channels; ++c)
			frag->data[c][i] = levels[c];
	}
}

static int splat_square_signals(Fragment *frag, PyObject **levels,
				PyObject *freq, PyObject *phase,
				PyObject *ratio, double origin)
{
	enum {
		SIG_FREQ = 0,
		SIG_PHASE,
		SIG_RATIO,
		SIG_AMP,
	};
	struct splat_signal sig;
	PyObject *signals[SIG_AMP + MAX_CHANNELS];
	unsigned c;
	size_t i;

	signals[SIG_FREQ] = freq;
	signals[SIG_PHASE] = phase;
	signals[SIG_RATIO] = ratio;

	for (c = 0; c < frag->n_channels; ++c)
		signals[SIG_AMP + c] = levels[c];

	if (splat_signal_init(&sig, frag->length, (origin * frag->rate),
			      signals, (SIG_AMP + frag->n_channels),
			      frag->rate))
		return -1;

	i = 0;

	while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
		size_t j;

		for (j = 0; j < sig.len; ++i, ++j) {
			const double f = sig.vectors[SIG_FREQ].data[j];
			const double ph = sig.vectors[SIG_PHASE].data[j];
			const double t = (double)i / frag->rate;
			const double tph = t + ph + origin;
			double n_periods;
			const double t_rel = modf((f * (tph)), &n_periods);
			double ratio = sig.vectors[SIG_RATIO].data[j];
			double s;

			ratio = min(ratio, 1.0);
			ratio = max(ratio, 0.0);
			s = (t_rel < ratio) ? 1.0 : -1.0;

			for (c = 0; c < frag->n_channels; ++c) {
				const double a =
					sig.vectors[SIG_AMP + c].data[j];

				frag->data[c][i] = dB2lin(a) * s;
			}
		}
	}

	splat_signal_free(&sig);

	return (sig.stat == SIGNAL_VECTOR_ERROR) ? -1 : 0;
}

PyDoc_STRVAR(splat_square_doc,
"square(fragment, levels, frequency, phase=0.0, origin=0.0, ratio=0.5)\n"
"\n"
"Generate a square wave with the given ``ratio`` over the entire "
"``fragment``.\n");

static PyObject *splat_square(PyObject *self, PyObject *args)
{
	Fragment *frag;
	PyObject *levels_obj;
	PyObject *freq;
	PyObject *phase = splat_zero;
	double origin = 0.0;
	PyObject *ratio = splat_init_source_ratio;

	struct splat_levels levels;
	int all_floats;

	if (!PyArg_ParseTuple(args, "O!OO|OdO", &splat_FragmentType, &frag,
			      &levels_obj, &freq, &phase, &origin, &ratio))
		return NULL;

	if (frag_get_levels(frag, &levels, levels_obj))
		return NULL;

	all_floats = levels.all_floats;
	all_floats = all_floats && splat_check_all_floats(freq, phase, ratio);

	if (all_floats)
		splat_square_floats(frag, levels.fl, PyFloat_AS_DOUBLE(freq),
				    PyFloat_AS_DOUBLE(phase) + origin,
				    PyFloat_AS_DOUBLE(ratio));
	else if (splat_square_signals(frag, levels.obj, freq, phase, ratio,
				      origin))
		return NULL;

	Py_RETURN_NONE;
}

/* -- triangle source -- */

static void splat_triangle_floats(Fragment *frag, const double *lvls,
				  double freq, double phase, double ratio)
{
	const double k = freq / frag->rate;
	const double ph0 = freq * phase;
	double a1[MAX_CHANNELS], b1[MAX_CHANNELS];
	double a2[MAX_CHANNELS], b2[MAX_CHANNELS];
	const double *a, *b;
	unsigned c;
	Py_ssize_t i;

	ratio = min(ratio, 1.0);
	ratio = max(ratio, 0.0);

	for (c = 0; c < frag->n_channels; ++c) {
		const double llin = lvls[c];

		a1[c] = 2 * llin / ratio;
		b1[c] = -llin;
		a2[c] = -2 * llin / (1 - ratio);
		b2[c] = llin - (a2[c] * ratio);
	}

	for (i = 0; i < frag->length; ++i) {
		double n_periods;
		const double t_rel = modf(((i * k) + ph0), &n_periods);

		if (t_rel < ratio) {
			a = a1;
			b = b1;
		} else {
			a = a2;
			b = b2;
		}

		for (c = 0; c < frag->n_channels; ++c)
			frag->data[c][i] = (a[c] * t_rel) + b[c];
	}
}

static int splat_triangle_signals(Fragment *frag, PyObject **levels,
				  PyObject *freq, PyObject *phase,
				  PyObject *ratio, double origin)
{
	enum {
		SIG_FREQ = 0,
		SIG_PHASE,
		SIG_RATIO,
		SIG_AMP,
	};
	struct splat_signal sig;
	PyObject *signals[SIG_AMP + MAX_CHANNELS];
	unsigned c;
	size_t i;

	signals[SIG_FREQ] = freq;
	signals[SIG_PHASE] = phase;
	signals[SIG_RATIO] = ratio;

	for (c = 0; c < frag->n_channels; ++c)
		signals[SIG_AMP + c] = levels[c];

	if (splat_signal_init(&sig, frag->length, (origin * frag->rate),
			      signals, (SIG_AMP + frag->n_channels),
			      frag->rate))
		return -1;

	i = 0;

	while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
		size_t j;

		for (j = 0; j < sig.len; ++i, ++j) {
			const double f = sig.vectors[SIG_FREQ].data[j];
			const double ph = sig.vectors[SIG_PHASE].data[j];
			const double t = (double)i / frag->rate;
			const double tph = t + ph + origin;
			double n_periods;
			const double t_rel = modf((f * (tph)), &n_periods);
			double ratio = sig.vectors[SIG_RATIO].data[j];

			ratio = min(ratio, 1.0);
			ratio = max(ratio, 0.0);

			for (c = 0; c < frag->n_channels; ++c) {
				const double l_log =
					sig.vectors[SIG_AMP + c].data[j];
				const double l = dB2lin(l_log);
				double a, b;

				if (t_rel < ratio) {
					a = 2 * l / ratio;
					b = -l;
				} else {
					a = -2 * l / (1 - ratio);
					b = l - (a * ratio);
				}

				frag->data[c][i] = (a * t_rel) + b;
			}
		}
	}

	splat_signal_free(&sig);

	return (sig.stat == SIGNAL_VECTOR_ERROR) ? -1 : 0;
}

PyDoc_STRVAR(splat_triangle_doc,
"triangle(fragment, levels, frequency, phase=0.0, origin=0.0, ratio=0.5)\n"
"\n"
"Generate a triangle wave with the given ``ratio`` over the entire "
"``fragment``.\n");

static PyObject *splat_triangle(PyObject *self, PyObject *args)
{
	Fragment *frag;
	PyObject *levels_obj;
	PyObject *freq;
	PyObject *phase = splat_zero;
	double origin = 0.0;
	PyObject *ratio = splat_init_source_ratio;

	struct splat_levels levels;
	int all_floats;

	if (!PyArg_ParseTuple(args, "O!OO|OdO", &splat_FragmentType, &frag,
			      &levels_obj, &freq, &phase, &origin, &ratio))
		return NULL;

	if (frag_get_levels(frag, &levels, levels_obj))
		return NULL;

	all_floats = levels.all_floats;
	all_floats = all_floats && splat_check_all_floats(freq, phase, ratio);

	if (all_floats)
		splat_triangle_floats(frag, levels.fl, PyFloat_AS_DOUBLE(freq),
				      PyFloat_AS_DOUBLE(phase) + origin,
				      PyFloat_AS_DOUBLE(ratio));
	else if (splat_triangle_signals(frag, levels.obj, freq, phase, ratio,
					origin))
		return NULL;

	Py_RETURN_NONE;
}

/* -- overtones source -- */

struct overtone {
	PyObject *ratio;
	double fl_ratio;
	PyObject *phase;
	double fl_phase;
	struct splat_levels levels;
};

static void splat_overtones_float(Fragment *frag, const double *levels,
				  double freq, double phase,
				  struct overtone *overtones, Py_ssize_t n)
{
	const double k = 2 * M_PI * freq;
	const double max_ratio = (frag->rate / freq) / 2;
	struct overtone *ot;
	const struct overtone *ot_end = &overtones[n];
	unsigned c;
	size_t i;

	/* Silence harmonics above (rate / 2) to avoid spectrum overlap
	   and multiply each overtone levels with global levels. */
	for (ot = overtones; ot != ot_end; ++ot) {
		if (ot->fl_ratio >= max_ratio) {
			for (c = 0; c < frag->n_channels; ++c)
				ot->levels.fl[c] = 0.0f;
		} else {
			for (c = 0; c < frag->n_channels; ++c)
				ot->levels.fl[c] *= levels[c];
		}
	}

	for (i = 0; i < frag->length; ++i) {
		const double t = phase + ((double)i / frag->rate);

		for (ot = overtones; ot != ot_end; ++ot) {
			const double s =
				sin(k * ot->fl_ratio * (t + ot->fl_phase));

			for (c = 0; c < frag->n_channels; ++c)
				frag->data[c][i] += s * ot->levels.fl[c];
		}
	}
}

static int splat_overtones_mixed(Fragment *frag, PyObject **levels,
				 PyObject *freq, PyObject *phase,
				 struct overtone *overtones, Py_ssize_t n,
				 double origin)
{
	enum {
		SIG_FREQ = 0,
		SIG_PHASE,
		SIG_AMP,
	};
	const double k = 2 * M_PI;
	const double half_rate = frag->rate / 2;
	PyObject *signals[SIG_AMP + MAX_CHANNELS];
	struct splat_signal sig;
	struct overtone *ot;
	const struct overtone *ot_end = &overtones[n];
	unsigned c;
	size_t i;

	signals[SIG_FREQ] = freq;
	signals[SIG_PHASE] = phase;

	for (c = 0; c < frag->n_channels; ++c)
		signals[SIG_AMP + c] = levels[c];

	if (splat_signal_init(&sig, frag->length, (origin * frag->rate),
			      signals, (SIG_AMP + frag->n_channels),
			      frag->rate))
		return -1;

	i = 0;

	while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
		size_t j;

		for (j = 0; j < sig.len; ++i, ++j) {
			const double f = sig.vectors[SIG_FREQ].data[j];
			const double max_ratio = half_rate / f;
			const double m = k * f;
			const double ph = sig.vectors[SIG_PHASE].data[j];
			const double t = (double)i / frag->rate;
			const double tph = t + ph + origin;

			for (ot = overtones; ot != ot_end; ++ot) {
				double s;

				if (ot->fl_ratio >= max_ratio)
					continue;

				s = sin(m * ot->fl_ratio *
					(tph + ot->fl_phase));

				for (c = 0; c < frag->n_channels; ++c) {
					double x;

					x = sig.vectors[SIG_AMP + c].data[j];
					x = dB2lin(x);
					x *= ot->levels.fl[c];
					frag->data[c][i] += s * x;
				}
			}
		}
	}

	splat_signal_free(&sig);

	return (sig.stat == SIGNAL_VECTOR_ERROR) ? -1 : 0;
}

static int splat_overtones_signal(Fragment *frag, PyObject **levels,
				  PyObject *freq, PyObject *phase,
				  struct overtone *overtones, Py_ssize_t n,
				  double origin)
{
	enum {
		SIG_FREQ = 0,
		SIG_PHASE = 1,
		SIG_AMP = 2,
		SIG_OT = 2 + MAX_CHANNELS,
	};
	const double k = 2 * M_PI;
	const double half_rate = frag->rate / 2;
	PyObject **signals;
	struct splat_signal sig;
	struct overtone *ot;
	const struct overtone *ot_end = &overtones[n];
	static const size_t sig_freq = 0;
	static const size_t sig_phase = 1;
	static const size_t sig_amp = 2;
	const size_t sig_ot = sig_amp + frag->n_channels;
	/* for each overtone: ratio, phase and levels */
	const size_t sig_n = sig_ot + (n * (2 + frag->n_channels));
	unsigned c;
	size_t i;

	signals = PyMem_Malloc(sig_n * sizeof(PyObject *));

	if (signals == NULL) {
		PyErr_NoMemory();
		return -1;
	}

	signals[sig_freq] = freq;
	signals[sig_phase] = phase;

	for (c = 0; c < frag->n_channels; ++c)
		signals[sig_amp + c] = levels[c];

	{
		PyObject **sig_ot_it = &signals[sig_ot];

		for (ot = overtones; ot != ot_end; ++ot) {
			*sig_ot_it++ = ot->ratio;
			*sig_ot_it++ = ot->phase;

			for (c = 0; c < frag->n_channels; ++c)
				*sig_ot_it++ = ot->levels.obj[c];
		}
	}

	if (splat_signal_init(&sig, frag->length, (origin * frag->rate),
			      signals, sig_n, frag->rate))
		return -1;

	i = 0;

	while (splat_signal_next(&sig) == SIGNAL_VECTOR_CONTINUE) {
		size_t j;

		for (j = 0; j < sig.len; ++i, ++j) {
			const double t = (double)i / frag->rate;
			const double f = sig.vectors[sig_freq].data[j];
			const double max_ratio = half_rate / f;
			const double ph = sig.vectors[sig_phase].data[j];
			const double m = k * f;
			const double tph = t + ph + origin;
			const struct signal_vector *otv = &sig.vectors[sig_ot];

			for (ot = overtones; ot != ot_end; ++ot) {
				const double ratio = (otv++)->data[j];
				const double ot_ph = (otv++)->data[j];
				double s;

				if (ratio >= max_ratio) {
					otv += frag->n_channels;
					continue;
				}

				s = sin(m * ratio * (tph + ot_ph));

				for (c = 0; c < frag->n_channels; ++c) {
					double x, y;

					x = sig.vectors[sig_amp + c].data[j];
					y = (otv++)->data[j];
					frag->data[c][i] +=
						s * dB2lin(x) * dB2lin(y);
				}
			}
		}
	}

	splat_signal_free(&sig);
	PyMem_Free(signals);

	return (sig.stat == SIGNAL_VECTOR_ERROR) ? -1 : 0;
}

PyDoc_STRVAR(splat_overtones_doc,
"overtones(fragment, levels, frequency, overtones, phase=0.0, origin=0.0)\n"
"\n"
"Generate a sum of overtones as pure sine waves with the given fundamental "
"``frequency`` and ``levels`` in dB.\n"
"\n"
"The ``overtones`` are described with a list of 3-tuples containing the "
"ratio between the overtone and the fundamental frequency, the phase and "
"levels: ``(ratio, phase, levels)``.  All these values can be signals, and "
"the levels can either be a single value for all channels or individual "
"values for each channel.  The generation is performed over the entire "
"fragment.\n");

static PyObject *splat_overtones(PyObject *self, PyObject *args)
{
	enum {
		OT_RATIO = 0,
		OT_PHASE,
		OT_LEVELS,
	};
	Fragment *frag;
	PyObject *levels_obj;
	PyObject *freq;
	PyObject *overtones_obj;
	PyObject *phase = splat_zero;
	double origin = 0.0;

	struct splat_levels levels;
	struct overtone *overtones;
	struct overtone *ot;
	Py_ssize_t n;
	Py_ssize_t pos;
	int all_floats;
	int ot_all_floats;
	int stat = 0;

	if (!PyArg_ParseTuple(args, "O!OOO!|Od", &splat_FragmentType, &frag,
			      &levels_obj, &freq, &PyList_Type, &overtones_obj,
			      &phase, &origin))
		return NULL;

	if (frag_get_levels(frag, &levels, levels_obj))
		return NULL;

	n = PyList_GET_SIZE(overtones_obj);
	overtones = PyMem_Malloc(n * sizeof(struct overtone));

	if (overtones == NULL)
		return PyErr_NoMemory();

	all_floats = levels.all_floats && splat_check_all_floats(freq, phase);
	ot_all_floats = 1;

	for (pos = 0, ot = overtones; pos < n; ++pos, ++ot) {
		PyObject *ot_params = PyList_GET_ITEM(overtones_obj, pos);
		PyObject *ot_levels;

		if (!PyTuple_Check(ot_params) ||
		    (PyTuple_GET_SIZE(ot_params) != 3)) {
			PyErr_SetString(PyExc_ValueError,
					"overtone params must be a 3-tuple");
			goto free_overtones;
		}

		ot->ratio = PyTuple_GET_ITEM(ot_params, OT_RATIO);

		if (ot_all_floats && PyFloat_Check(ot->ratio))
			ot->fl_ratio = PyFloat_AS_DOUBLE(ot->ratio);
		else
			ot_all_floats = 0;

		ot->phase = PyTuple_GET_ITEM(ot_params, OT_PHASE);

		if (ot_all_floats && PyFloat_Check(ot->phase))
			ot->fl_phase = PyFloat_AS_DOUBLE(ot->phase);
		else
			ot_all_floats = 0;

		ot_levels = PyTuple_GET_ITEM(ot_params, OT_LEVELS);

		if (frag_get_levels(frag, &ot->levels, ot_levels))
			goto free_overtones;

		ot_all_floats = ot_all_floats && ot->levels.all_floats;
	}

	all_floats = all_floats && ot_all_floats;

	if (all_floats)
		splat_overtones_float(frag, levels.fl, PyFloat_AS_DOUBLE(freq),
				      PyFloat_AS_DOUBLE(phase) + origin,
				      overtones, n);
	else if (ot_all_floats)
		stat = splat_overtones_mixed(frag, levels.obj, freq, phase,
					     overtones, n, origin);
	else
		stat = splat_overtones_signal(frag, levels.obj, freq, phase,
					      overtones, n, origin);
free_overtones:
	PyMem_Free(overtones);

	if (stat)
		return NULL;

	Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
 * Filters
 */

PyDoc_STRVAR(splat_dec_envelope_doc,
"dec_envelope(fragment, k=1.0, p=1.0)\n"
"\n"
"This filter applies a decreasing envelope over the ``fragment`` with ``k`` "
"and ``p`` arguments as follows, for a sound signal ``s`` at index ``i``:\n"
"\n"
".. math::\n"
"\n"
"   s[i] = \\frac{s[i]}{(1 + \\frac{i}{k})^p}\n"
"\n");

static PyObject *splat_dec_envelope(PyObject *self, PyObject *args)
{
	Fragment *frag;
	double k = 1.0;
	double p = 1.0;

	unsigned c;

	if (!PyArg_ParseTuple(args, "O!|dd", &splat_FragmentType, &frag,
			      &k, &p))
		return NULL;

	if (k == 0.0) {
		PyErr_SetString(PyExc_ValueError, "k must not be 0");
		return NULL;
	}

	for (c = 0; c < frag->n_channels; ++c) {
		size_t i;

		for (i = 0; i < frag->length; ++i) {
			const double m = pow(1.0 + ((double)i / k), p);
			frag->data[c][i] /= m;
		}
	}

	Py_RETURN_NONE;
}

PyDoc_STRVAR(splat_reverse_doc,
"reverse(fragment)\n"
"\n"
"Reverse the order of all the ``fragment`` samples.\n");

static PyObject *splat_reverse(PyObject *self, PyObject *args)
{
	Fragment *frag;

	unsigned c;

	if (!PyArg_ParseTuple(args, "O!", &splat_FragmentType, &frag))
		return NULL;

	for (c = 0; c < frag->n_channels; ++c) {
		size_t i;
		size_t j;

		for (i = 0, j = (frag->length - 1); i < j; ++i, --j) {
			const double s = frag->data[c][i];

			frag->data[c][i] = frag->data[c][j];
			frag->data[c][j] = s;
		}
	}

	Py_RETURN_NONE;
}

PyDoc_STRVAR(splat_reverb_doc,
"reverb(fragment, delays, time_factor=0.2, gain_factor=6.0, seed=0)\n"
"\n"
"This filter creates a fast basic reverb effect with some randomness.\n"
"\n"
"The ``delays`` are a list of 2-tuples with a delay duration in seconds and "
"a gain in dB.  They are used to repeat and mix the whole ``fragment`` once "
"for each element in the list, shifted by the given time and amplified by the "
"given gain.  All values must be floating point numbers.  The time delay must "
"not be negative - it's a *causal* reverb.\n"
"\n"
"The ``time_factor`` and ``gain_factor`` parameters are used when adding a "
"random element to the delay and gain.  For example, a ``time_factor`` of 0.2 "
"means the delay will be randomly picked between 1.0 and 1.2 times the value "
"given in the ``delays`` list.  Similarly, for a ``gain_factor`` of 6.0dB the "
"gain will be randomly picked within +/- 6dB around the given value in "
"``delays``.\n"
"\n"
"The ``seed`` argument can be used to initialise the pseudo-random number "
"sequence.  With the default value of 0, the seed will be initialised based "
"on the current time.\n"
"\n"
".. note::\n"
"\n"
"   This filter function can also produce a *delay* effect by specifiying "
"   only a few regularly spaced ``delays``.\n");

static PyObject *splat_reverb(PyObject *self, PyObject *args)
{
	struct delay {
		size_t time;
		double gain;
#if USE_V4SF
		v4sf gain4;
#endif
	};

	Fragment *frag;
	PyObject *delays_list;
	double time_factor = 0.2;
	double gain_factor = 6.0;
	unsigned int seed = 0;

	struct delay *delays[MAX_CHANNELS];
	Py_ssize_t n_delays;
	size_t max_delay;
	size_t max_index;
	size_t d;
	unsigned c;
	size_t i;

	if (!PyArg_ParseTuple(args, "O!O!|ddI", &splat_FragmentType, &frag,
			      &PyList_Type, &delays_list, &time_factor,
			      &gain_factor, &seed))
		return NULL;

	if (!seed)
		seed = time(0);

	srand(seed);

	n_delays = PyList_GET_SIZE(delays_list);

	for (c = 0; c < frag->n_channels; ++c) {
		delays[c] = PyMem_Malloc(n_delays * sizeof(struct delay));

		if (delays[c] == NULL) {
			while (--c)
				PyMem_Free(delays[c]);

			return PyErr_NoMemory();
		}
	}

	max_delay = 0;

	for (d = 0; d < n_delays; ++d) {
		PyObject *pair = PyList_GetItem(delays_list, d);
		double time;
		double gain;

		if (!PyTuple_Check(pair)) {
			PyErr_SetString(PyExc_TypeError,
					"delay values must be a tuple");
			return NULL;
		}

		if (PyTuple_GET_SIZE(pair) != 2) {
			PyErr_SetString(PyExc_ValueError,
					"delay tuple length must be 2");
			return NULL;
		}

		time = PyFloat_AsDouble(PyTuple_GetItem(pair, 0));

		if (time < 0.0) {
			PyErr_SetString(PyExc_ValueError,
					"delay time must be >= 0");
			return NULL;
		}

		for (c = 0; c < frag->n_channels; ++c) {
			const double c_time =
				(time
				 * (1.0 + (rand() * time_factor / RAND_MAX)));
#if USE_V4SF
			delays[c][d].time = c_time * frag->rate / 4;
#else
			delays[c][d].time = c_time * frag->rate;
#endif

			if (delays[c][d].time > max_delay)
				max_delay = delays[c][d].time;
		}

		gain = PyFloat_AsDouble(PyTuple_GetItem(pair, 1));

		for (c = 0; c < frag->n_channels; ++c) {
			const double c_gain_dB =
				(gain - gain_factor
				 + (rand() * gain_factor * 2.0 / RAND_MAX));
#if USE_V4SF
			const double c_gain = dB2lin(c_gain_dB);
			const v4sf gain4 = {c_gain, c_gain, c_gain, c_gain};
			delays[c][d].gain4 = gain4;
			delays[c][d].gain = c_gain;
#else
			delays[c][d].gain = dB2lin(c_gain_dB);
#endif
		}
	}

	max_index = frag->length - 1;

#if USE_V4SF
	max_delay *= 4;
#endif

	if (frag_grow(frag, (frag->length + max_delay)))
		return NULL;

	for (c = 0; c < frag->n_channels; ++c) {
		const struct delay *c_delay = delays[c];
#if USE_V4SF
		v4sf *c_data = (v4sf *)frag->data[c];
#else
		sample_t *c_data = frag->data[c];
#endif

		i = max_index;

#if USE_V4SF
		while (i % 4) {
			const double s = frag->data[c][i];

			for (d = 0; d < n_delays; ++d) {
				const double z = s * c_delay[d].gain;
				frag->data[c][i + (c_delay[d].time * 4)] += z;
			}

			i--;
		}

		i /= 4;
#endif

		do {
#if USE_V4SF
			const v4sf s = c_data[i];
#else
			const double s = c_data[i];
#endif

			for (d = 0; d < n_delays; ++d) {
#if USE_V4SF
				const v4sf z = s * c_delay[d].gain4;
#else
				const double z = s * c_delay[d].gain;
#endif
				c_data[i + c_delay[d].time] += z;
			}
		} while (i--);
	}

	for (c = 0; c < frag->n_channels; ++c)
		PyMem_Free(delays[c]);

	Py_RETURN_NONE;
}

static PyObject *splat_poly_value(PyObject *self, PyObject *args)
{
	PyObject *coefs;
	double x;

	if (!PyArg_ParseTuple(args, "O!d", &PyTuple_Type, &coefs, &x))
		return NULL;

	return PyFloat_FromDouble(splat_spline_tuple_value(coefs, x));
}

static PyObject *splat_spline_value(PyObject *self, PyObject *args)
{
	PyObject *spline;
	double x;

	PyObject *poly;

	if (!PyArg_ParseTuple(args, "O!d", &PyList_Type, &spline, &x))
		return NULL;

	poly = splat_find_spline_poly(spline, x, NULL);

	if (poly == NULL)
		return NULL;

	return PyFloat_FromDouble(splat_spline_tuple_value(poly, x));
}

static PyMethodDef splat_methods[] = {
	{ "lin2dB", splat_lin2dB, METH_VARARGS,
	  splat_lin2dB_doc },
	{ "dB2lin", splat_dB2lin, METH_VARARGS,
	  splat_dB2lin_doc },
	{ "gen_ref", splat_gen_ref, METH_VARARGS,
	  splat_gen_ref_doc },
	{ "sine", splat_sine, METH_VARARGS,
	  splat_sine_doc },
	{ "square", splat_square, METH_VARARGS,
	  splat_square_doc },
	{ "triangle", splat_triangle, METH_VARARGS,
	  splat_triangle_doc },
	{ "overtones", splat_overtones, METH_VARARGS,
	  splat_overtones_doc },
	{ "dec_envelope", splat_dec_envelope, METH_VARARGS,
	  splat_dec_envelope_doc },
	{ "reverse", splat_reverse, METH_VARARGS,
	  splat_reverse_doc },
	{ "reverb", splat_reverb, METH_VARARGS,
	  splat_reverb_doc },
	{ "poly_value", splat_poly_value, METH_VARARGS, NULL },
	{ "spline_value", splat_spline_value, METH_VARARGS, NULL },
	{ NULL, NULL, 0, NULL }
};

static void splat_init_sample_types(PyObject *m, const char *name,
				    PyObject *obj)
{
	size_t i;

	obj = PyDict_New();

	for (i = 0; i < ARRAY_SIZE(splat_raw_io_table); ++i) {
		const struct splat_raw_io *io = &splat_raw_io_table[i];

		PyDict_SetItem(obj, PyString_FromString(io->sample_type),
			       PyLong_FromLong(io->sample_width));
	}

	PyModule_AddObject(m, name, obj);
}

PyMODINIT_FUNC init_splat(void)
{
	struct splat_type {
		PyTypeObject *type;
		const char *name;
	};
	static const struct splat_type splat_types[] = {
		{ &splat_SplineType, "Spline" },
		{ &splat_SignalType, "Signal" },
		{ &splat_FragmentType, "Fragment" },
		{ NULL, NULL }
	};
	const struct splat_type *it;
	PyObject *m;

	for (it = splat_types; it->type != NULL; ++it) {
		if (it->type->tp_new == NULL)
			it->type->tp_new = PyType_GenericNew;

		if (PyType_Ready(it->type))
			return;
	}

	m = Py_InitModule("_splat", splat_methods);

	for (it = splat_types; it->type != NULL; ++it) {
		Py_INCREF((PyObject *)it->type);
		PyModule_AddObject(m, it->name, (PyObject *)it->type);
	}

	splat_init_source_ratio = PyFloat_FromDouble(0.5);
	PyModule_AddObject(m, "_init_source_ratio", splat_init_source_ratio);
	splat_zero = PyFloat_FromDouble(0.0);
	PyModule_AddObject(m, "_zero", splat_zero);
	splat_init_sample_types(m, "sample_types", splat_sample_types);

	PyModule_AddStringConstant(m, "SAMPLE_TYPE", SPLAT_NATIVE_SAMPLE_TYPE);
	PyModule_AddIntConstant(m, "SAMPLE_WIDTH", SPLAT_NATIVE_SAMPLE_WIDTH);
}
