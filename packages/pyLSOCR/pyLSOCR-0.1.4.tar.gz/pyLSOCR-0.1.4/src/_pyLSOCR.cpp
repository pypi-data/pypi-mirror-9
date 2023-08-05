#include <Python.h>
#include "structmember.h"

#define MODULESTR "_lsocr"
#define MODULEDOC "A wrapper module"
#define FT_VERSION "0.1"

#include "numpy/ndarrayobject.h"

#include <opencv/cv.h>
#include <opencv/cxcore.h>

#include <TextDetection.h>

//
// Opencv conversion stuff
//
#include "opencv_helpers.h"



////////////////////////////////////////////////////////////////////////////////
//
// Define the LSOCR wrapper class
//
typedef struct {
  PyObject_HEAD

} LSOCR;


static int 
LSOCR_clear(LSOCR*self)
{

	return 0;
}


static void
LSOCR_dealloc(LSOCR* self)
{
	LSOCR_clear(self);
	self->ob_type->tp_free((PyObject*)self);
}


//
// new and constructor
//
static PyObject *
LSOCR_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	LSOCR*self;

	self = (LSOCR*)type->tp_alloc(type, 0);
	if (self != NULL)  {
		// init routines
	}

	return (PyObject *)self;
}


static int
LSOCR_init(LSOCR*self, PyObject *args, PyObject *kwds)
{

	return 0;
}


//
// LSOCRmembers
//
static PyMemberDef LSOCR_members[] = {
    {NULL}  /* Sentinel */
};



static PyObject *
LSOCR_detect_text(LSOCR* self, PyObject *args, PyObject *kw)
{
    PyObject* pyobj_img = NULL;
    Mat img;
    PyObject* pyobj_dark_on_light = NULL;
    bool dark_on_light = true; // should there be a default?


    if (!PyArg_ParseTuple(args, "OO", &pyobj_img, &pyobj_dark_on_light  )
    		|| !pyopencv_to(pyobj_img, img)
    		|| !pyopencv_to( pyobj_dark_on_light, dark_on_light )
    ) {
        return NULL;
    }


    try {
    	IplImage inputImg = img;
    	IplImage * saveSWT;
    	std::vector<std::pair<int,int> > text_bounding_boxes;
    	// IplImage * textImage;
    	/*
    	double threshold_low = 175;
    	double threshold_high = 320;
    	*/
    	textDetection( &inputImg, dark_on_light, saveSWT, text_bounding_boxes ); // , threshold_low, threshold_high );
    	Mat SWTimg( saveSWT );
    	// Mat Textimg( textImage );

			PyObject *PList = PyList_New(0);

    	PyList_Append( PList, Py_BuildValue("N", pyopencv_from( SWTimg ) ) );
    	cvReleaseImage( &saveSWT );
    	// cvReleaseImage( &textImage );

    	for ( int i=0; i< text_bounding_boxes.size(); i+=2 ){
    		PyList_Append(PList,
    			Py_BuildValue("NNNN",
    				pyopencv_from( text_bounding_boxes[i].first ),
    				pyopencv_from( text_bounding_boxes[i].second ),
    				pyopencv_from( text_bounding_boxes[i+1].first ),
    				pyopencv_from( text_bounding_boxes[i+1].second )
    			)
    		);
    	}
    	/*
    	for (std::vector<std::pair<int,int> >::iterator it = text_bounding_boxes.begin(); it != text_bounding_boxes.end(); it++ ) {
    		PyList_Append(PList, Py_BuildValue("NN", pyopencv_from( it->first), pyopencv_from( it->second ) );
    	}
    	 */
    	return PList;
    } catch(...) {
      fprintf( stderr, "text_detect error\n" );
      Py_RETURN_NONE;
    }

}

static PyObject *
LSOCR_gen_text_masks(LSOCR* self, PyObject *args, PyObject *kw)
{
    PyObject* pyobj_img = NULL;
    Mat img;


    if (!PyArg_ParseTuple(args, "O", &pyobj_img )
    		|| !pyopencv_to(pyobj_img, img)
    ) {
        return NULL;
    }


    try {
    	IplImage inputImg = img;
    	IplImage * dark_text_mask;
    	IplImage * light_text_mask;

    	gen_text_masks( &inputImg, dark_text_mask, light_text_mask );
    	Mat dark_img( dark_text_mask );
    	Mat light_img( light_text_mask );
    	PyObject * ret_val = Py_BuildValue("NN", pyopencv_from( dark_img ), pyopencv_from( light_img ) );

    	cvReleaseImage( &dark_text_mask );
    	cvReleaseImage( &light_text_mask );

    	return ret_val;
    } catch(...) {
      fprintf( stderr, "text_mask error\n" );
      Py_RETURN_NONE;
    }

}



static PyMethodDef LSOCR_methods[] = {
    {"detect_text", (PyCFunction)LSOCR_detect_text, METH_VARARGS, "detect text in image."},
    {"gen_text_masks", (PyCFunction)LSOCR_gen_text_masks, METH_VARARGS, "text masks of input image."},
    {NULL}  /* Sentinel */
};


static PyTypeObject LSOCRType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_lsocr.LSOCR",             /*tp_name*/
    sizeof(LSOCR),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)LSOCR_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "LSOCR objects",           /* tp_doc */
    0,   /* tp_traverse */
    0,           /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    LSOCR_methods,             /* tp_methods */
    LSOCR_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)LSOCR_init,      /* tp_init */
    0,                         /* tp_alloc */
    LSOCR_new,                 /* tp_new */
};


//
// Module methods
//

static PyMethodDef ModuleMethods[] = {
    {NULL}  /* Sentinel */
};


//
// Create the module
//
#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_lsocr(void)
{
    import_array();

    if (PyType_Ready(&LSOCRType) < 0)
        return;

    PyObject* m = Py_InitModule3(MODULESTR, ModuleMethods, MODULEDOC);
    PyObject* d = PyModule_GetDict(m);

    PyDict_SetItemString(d, "__version__", PyString_FromString(FT_VERSION));

    Py_INCREF(&LSOCRType);
    PyModule_AddObject(m, "LSOCR", (PyObject *)&LSOCRType);
}
