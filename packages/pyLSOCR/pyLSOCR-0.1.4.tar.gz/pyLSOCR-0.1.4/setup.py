
'''
# cmd to submit to pypi
python setup.py sdist upload
'''

'''
export PATH="/usr/local/bin:$PATH"
export PYTHONPATH=/usr/local/Cellar/opencv/2.4.8.2/lib/python2.7/site-packages/:$PYTHONPATH
'''


'''
import lsocr, cv2, numpy

def show_image( ci ):
    cv2.namedWindow('cropped')
    cv2.imshow('cropped',ci)
    cv2.waitKey(0)
    cv2.destroyWindow('cropped')

ocr = lsocr.LSOCR()
image=cv2.imread('/tmp/ci.jpg')
res = ocr.detect_text( image, False )
# swtimg, textimg = 
# dark_mask, light_mask = ocr.gen_text_masks( image )
# show_image( numpy.vstack( ( dark_mask, light_mask ) ) )
'''


from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())
        
# import numpy as np
import os


NAME = 'pyLSOCR'
PACKAGE_NAME = 'lsocr'
VERSION = '0.1.4'
DESCRIPTION = 'A python wrapper'
LONG_DESCRIPTION = """
"""
AUTHOR = 'Lingospot'
EMAIL = 'info@lingospot.com'
URL = ''
KEYWORDS = []
LICENSE = 'See separate LICENSE file'
CLASSIFIERS = [
    'License :: Other/Proprietary License',
    'Development Status :: 3 - Alpha',
    'Topic :: Scientific/Engineering'
]
TEXTDETECT_BASE = r'external'

INCLUDE_PATH=r'/usr/local/include'
OPENCV_INCLUDE_DIRS = [
    INCLUDE_PATH + p for p in (
        r'/opencv2',
    )
]

OPENCV_LIB_DIRS = [ '/usr/local/lib' ]
OPENCV_LIBS=[
    'opencv_core',
    'opencv_imgproc',
]


def main():
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        license=LICENSE,
        packages=[PACKAGE_NAME],
        cmdclass={'build_ext':build_ext},
        setup_requires=['numpy'],
        install_requires=['numpy'],
        ext_modules = [
           Extension(
                PACKAGE_NAME + '.' + "_lsocr",
                [os.path.join(TEXTDETECT_BASE, f) for f in
                    (
                        "TextDetection.cpp",
                    )
                ] + 
                ["src/_pyLSOCR.cpp"],


                include_dirs=[ os.path.join(TEXTDETECT_BASE, '') ] + OPENCV_INCLUDE_DIRS, # + [np.get_include()],
                libraries=OPENCV_LIBS + [ 'tesseract' ],
                library_dirs=OPENCV_LIB_DIRS,
            )
        ]
    )


if __name__ == '__main__':
    main()

