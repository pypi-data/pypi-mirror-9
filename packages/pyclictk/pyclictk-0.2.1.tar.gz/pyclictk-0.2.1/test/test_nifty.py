import unittest

__author__ = 'Alexander Weigl <Alexander.Weigl@student.kit.edu>'
__date__ = "2015-02-19"
__version__ = "0.1"

import clictk, os.path

ROOT = os.path.dirname(os.path.abspath(__file__))

from xml.etree import ElementTree
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")


from clictk import *


class ReadTests(unittest.TestCase):
    def test_compare_ok(self):
        ref1 = Executable(executable=None, category='Registration.NiftyReg', title='RegAladin (NiftyReg)',
                          description='Module/executable for global registration (rigid and/or affine) based on a block-matching approach and a trimmed least squared optimisation.',
                          version='0.0.1', license='BSD', contributor='Marc Modat, Pankaj Daga, David Cash (UCL)',
                          acknowledgements=None, documentation_url=None, parameter_groups=[
                ParameterGroup(label='Input images. Reference and floating images are mandatory',
                               description='Input images to perform the registration', advanced=False, parameters=[
                        Parameter(name='referenceImageName', type='image', default='required',
                                  description='Reference image filename (also called Target or Fixed)', channel='input',
                                  values=[], index=None, label='Reference image', longflag='ref',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingImageName', type='image', default='required',
                                  description='Floating image filename (also called Source or moving)', channel='input',
                                  values=[], index=None, label='Floating image', longflag='flo',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='referenceMaskImageName', type='image', default='',
                                  description='Filename of a mask image in the reference space', channel='input',
                                  values=[], index=None, label='Ref. mask', longflag='rmask',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingMaskImageName', type='image', default='',
                                  description='Filename of a mask image in the floating space. Only used when symmetric turned on',
                                  channel='input', values=[], index=None, label='Flo. mask', longflag='fmask',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='smoothReferenceWidth', type='float', default='0',
                                  description='Standard deviation in mm (voxel if negative) of the Gaussian kernel used to smooth the reference image',
                                  channel=None, values=[], index=None, label='Ref .Smooth', longflag='smooR',
                                  file_ext=None), Parameter(name='smoothFloatingWidth', type='float', default='0',
                                                            description='Standard deviation in mm (voxel if negative) of the Gaussian kernel used to smooth the Floating image',
                                                            channel=None, values=[], index=None, label='Flo. smooth',
                                                            longflag='smooF', file_ext=None),
                        Parameter(name='referenceLowerThreshold', type='float', default='0',
                                  description='Lower threshold value applied to the reference image', channel=None,
                                  values=[], index=None, label='Ref. Low Thr.', longflag='refLowThr', file_ext=None),
                        Parameter(name='referenceUpperThreshold', type='float', default='0',
                                  description='Upper threshold value applied to the reference image', channel=None,
                                  values=[], index=None, label='Ref. Up Thr.', longflag='refUpThr', file_ext=None),
                        Parameter(name='floatingLowerThreshold', type='float', default='0',
                                  description='Lower threshold value applied to the floating image', channel=None,
                                  values=[], index=None, label='Flo. Low Thr.', longflag='floLowThr', file_ext=None),
                        Parameter(name='floatingUpperThreshold', type='float', default='0',
                                  description='Upper threshold value applied to the floating image', channel=None,
                                  values=[], index=None, label='Flo. Up Thr.', longflag='floUpThr', file_ext=None)])])
        ref2 = Executable(executable=None, category='Registration.NiftyReg', title='RegAladin (NiftyReg)',
                          description='Module/executable for global registration (rigid and/or affine) based on a block-matching approach and a trimmed least squared optimisation.',
                          version='0.0.1', license='BSD', contributor='Marc Modat, Pankaj Daga, David Cash (UCL)',
                          acknowledgements=None, documentation_url=None, parameter_groups=[
                ParameterGroup(label='Input images. Reference and floating images are mandatory',
                               description='Input images to perform the registration', advanced=False, parameters=[
                        Parameter(name='referenceImageName', type='image', default='required',
                                  description='Reference image filename (also called Target or Fixed)', channel='input',
                                  values=[], index=None, label='Reference image', longflag='ref',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingImageName', type='image', default='required',
                                  description='Floating image filename (also called Source or moving)', channel='input',
                                  values=[], index=None, label='Floating image', longflag='flo',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='referenceMaskImageName', type='image', default='',
                                  description='Filename of a mask image in the reference space', channel='input',
                                  values=[], index=None, label='Ref. mask', longflag='rmask',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingMaskImageName', type='image', default='',
                                  description='Filename of a mask image in the floating space. Only used when symmetric turned on',
                                  channel='input', values=[], index=None, label='Flo. mask', longflag='fmask',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='smoothReferenceWidth', type='float', default='0',
                                  description='Standard deviation in mm (voxel if negative) of the Gaussian kernel used to smooth the reference image',
                                  channel=None, values=[], index=None, label='Ref .Smooth', longflag='smooR',
                                  file_ext=None), Parameter(name='smoothFloatingWidth', type='float', default='0',
                                                            description='Standard deviation in mm (voxel if negative) of the Gaussian kernel used to smooth the Floating image',
                                                            channel=None, values=[], index=None, label='Flo. smooth',
                                                            longflag='smooF', file_ext=None),
                        Parameter(name='referenceLowerThreshold', type='float', default='0',
                                  description='Lower threshold value applied to the reference image', channel=None,
                                  values=[], index=None, label='Ref. Low Thr.', longflag='refLowThr', file_ext=None),
                        Parameter(name='referenceUpperThreshold', type='float', default='0',
                                  description='Upper threshold value applied to the reference image', channel=None,
                                  values=[], index=None, label='Ref. Up Thr.', longflag='refUpThr', file_ext=None),
                        Parameter(name='floatingLowerThreshold', type='float', default='0',
                                  description='Lower threshold value applied to the floating image', channel=None,
                                  values=[], index=None, label='Flo. Low Thr.', longflag='floLowThr', file_ext=None),
                        Parameter(name='floatingUpperThreshold', type='float', default='0',
                                  description='Upper threshold value applied to the floating image', channel=None,
                                  values=[], index=None, label='Flo. Up Thr.', longflag='floUpThr', file_ext=None)])])
        ref3 = Executable(executable=None, category='Registration.NiftyReg', title='RegF3D (NiftyReg)',
                          description='Module/executable for local registration (non-rigid) based on a cubic B-Spline deformation model',
                          version='0.0.1', license='BSD', contributor='Marc Modat, Pankaj Daga (UCL)',
                          acknowledgements=None, documentation_url=None, parameter_groups=[
                ParameterGroup(label='Input images. Reference and floating images are mandatory',
                               description='Input images to perform the registration', advanced=False, parameters=[
                        Parameter(name='referenceImageName', type='image', default='required',
                                  description='Reference image filename (also called Target or Fixed)', channel='input',
                                  values=[], index=None, label='Reference image', longflag='ref',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingImageName', type='image', default='required',
                                  description='Floating image filename (also called Source or moving)', channel='input',
                                  values=[], index=None, label='Floating image', longflag='flo',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='referenceMaskImageName', type='image', default='',
                                  description='Reference mask image filename', channel='input', values=[], index=None,
                                  label='Ref. mask', longflag='rmask', file_ext='.nii,.nii.gz,.nrrd,.png')])])

        self.assertEquals(ref1, ref2)
        self.assertNotEqual(ref1, ref3)

    def test_reading_xml_reg_aladin(self):
        executable = Executable.from_xml(os.path.join(ROOT, "reg_aladin.xml"))

        reference = Executable(executable=None, category='Registration.NiftyReg', title='RegAladin (NiftyReg)',
                               description='Module/executable for global registration (rigid and/or affine) based on a block-matching approach and a trimmed least squared optimisation.',
                               version='0.0.1', license='BSD', contributor='Marc Modat, Pankaj Daga, David Cash (UCL)',
                               acknowledgements=None, documentation_url=None, parameter_groups=[
                ParameterGroup(label='Input images. Reference and floating images are mandatory',
                               description='Input images to perform the registration', advanced=False, parameters=[
                        Parameter(name='referenceImageName', type='image', default='required',
                                  description='Reference image filename (also called Target or Fixed)', channel='input',
                                  values=[], index=None, label='Reference image', longflag='ref',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingImageName', type='image', default='required',
                                  description='Floating image filename (also called Source or moving)', channel='input',
                                  values=[], index=None, label='Floating image', longflag='flo',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='referenceMaskImageName', type='image', default='',
                                  description='Filename of a mask image in the reference space', channel='input',
                                  values=[], index=None, label='Ref. mask', longflag='rmask',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingMaskImageName', type='image', default='',
                                  description='Filename of a mask image in the floating space. Only used when symmetric turned on',
                                  channel='input', values=[], index=None, label='Flo. mask', longflag='fmask',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='smoothReferenceWidth', type='float', default='0',
                                  description='Standard deviation in mm (voxel if negative) of the Gaussian kernel used to smooth the reference image',
                                  channel=None, values=[], index=None, label='Ref .Smooth', longflag='smooR',
                                  file_ext=None), Parameter(name='smoothFloatingWidth', type='float', default='0',
                                                            description='Standard deviation in mm (voxel if negative) of the Gaussian kernel used to smooth the Floating image',
                                                            channel=None, values=[], index=None, label='Flo. smooth',
                                                            longflag='smooF', file_ext=None),
                        Parameter(name='referenceLowerThreshold', type='float', default='0',
                                  description='Lower threshold value applied to the reference image', channel=None,
                                  values=[], index=None, label='Ref. Low Thr.', longflag='refLowThr', file_ext=None),
                        Parameter(name='referenceUpperThreshold', type='float', default='0',
                                  description='Upper threshold value applied to the reference image', channel=None,
                                  values=[], index=None, label='Ref. Up Thr.', longflag='refUpThr', file_ext=None),
                        Parameter(name='floatingLowerThreshold', type='float', default='0',
                                  description='Lower threshold value applied to the floating image', channel=None,
                                  values=[], index=None, label='Flo. Low Thr.', longflag='floLowThr', file_ext=None),
                        Parameter(name='floatingUpperThreshold', type='float', default='0',
                                  description='Upper threshold value applied to the floating image', channel=None,
                                  values=[], index=None, label='Flo. Up Thr.', longflag='floUpThr', file_ext=None)])])

        self.assertEquals(reference, executable)

    @unittest.expectedFailure
    def test_call_reg_aladin_error(self):
        executable = clictk.Executable.from_xml(os.path.join(ROOT, "reg_aladin.xml"))
        executable.cmdline(abc="test")  # should throw KeyError

    def test_call_reg_aladin_ok(self):
        executable = clictk.Executable.from_xml(os.path.join(ROOT, "reg_aladin.xml"))
        args = executable.cmdline(referenceImageName="image.png", floatingImageName="floating.png")
        ref = [None, '--ref', 'image.png', '--flo', 'floating.png']
        self.assertItemsEqual(ref, args)

    def test_reading_xml_reg_f3d(self):
        executable = clictk.Executable.from_xml(os.path.join(ROOT, "reg_f3d.xml"))
        reference = Executable(executable=None, category='Registration.NiftyReg', title='RegF3D (NiftyReg)',
                               description='Module/executable for local registration (non-rigid) based on a cubic B-Spline deformation model',
                               version='0.0.1', license='BSD', contributor='Marc Modat, Pankaj Daga (UCL)',
                               acknowledgements=None, documentation_url=None, parameter_groups=[
                ParameterGroup(label='Input images. Reference and floating images are mandatory',
                               description='Input images to perform the registration', advanced=False, parameters=[
                        Parameter(name='referenceImageName', type='image', default='required',
                                  description='Reference image filename (also called Target or Fixed)', channel='input',
                                  values=[], index=None, label='Reference image', longflag='ref',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='floatingImageName', type='image', default='required',
                                  description='Floating image filename (also called Source or moving)', channel='input',
                                  values=[], index=None, label='Floating image', longflag='flo',
                                  file_ext='.nii,.nii.gz,.nrrd,.png'),
                        Parameter(name='referenceMaskImageName', type='image', default='',
                                  description='Reference mask image filename', channel='input', values=[], index=None,
                                  label='Ref. mask', longflag='rmask', file_ext='.nii,.nii.gz,.nrrd,.png')])])
        self.assertEquals(executable, reference)

    def test_reading_xml_reg_jacobian(self):
        executable = clictk.Executable.from_xml(os.path.join(ROOT, "reg_jacobian.xml"))
        reference = Executable(executable=None, category='Registration.NiftyReg', title='RegJacobian (NiftyReg)',
                               description='NiftyReg module to create Jacobian-based images', version='0.0.1',
                               license='BSD', contributor='Marc Modat (UCL)', acknowledgements=None,
                               documentation_url=None, parameter_groups=[
                ParameterGroup(label='Input reference image', description='Input images', advanced=False, parameters=[
                    Parameter(name='InTrans', type='file', default='required', description='Input transformation',
                              channel='input', values=[], index=None, label='Input Trans.', longflag='trans',
                              file_ext='.nii,.nii.gz,.nrrd,.txt,.mat'),
                    Parameter(name='referenceImageName', type='image', default='required',
                              description='Reference image filename, required if the transformation is a spline parametrisation',
                              channel='input', values=[], index=None, label='Reference image', longflag='ref',
                              file_ext='.nii,.nii..gz,.nrrd,.png')])])
        self.assertEquals(reference, executable)


    def test_reading_xml_reg_tools(self):
        executable = clictk.Executable.from_xml(os.path.join(ROOT, "reg_tools.xml"))
        reference = Executable(executable=None, category='Registration.NiftyReg', title='RegTools (NiftyReg)',
                               description='NiftyReg module under construction', version='0.0.1', license='BSD',
                               contributor='Marc Modat (UCL)', acknowledgements=None, documentation_url=None,
                               parameter_groups=[
                                   ParameterGroup(label='Input and Output', description='Input image (mandatory)',
                                                  advanced=False, parameters=[
                                           Parameter(name='inputImageName', type='image', default='required',
                                                     description='Input image filename', channel='input', values=[],
                                                     index=None, label='Input image', longflag='in',
                                                     file_ext='.nii,.nii.gz,.nrrd,.png')])])
        self.assertEquals(executable, reference)


    def test_exec_xml_stub(self):
        return True


class ArgParseTest(unittest.TestCase):
    def test_argparse_1(self):
        executable = clictk.Executable.from_xml(os.path.join(ROOT, "reg_aladin.xml"))
        argparse = build_argument_parser(executable)
        argparse.print_help()

    def test_docopt(self):
        executable = clictk.Executable.from_xml(os.path.join(ROOT, "reg_aladin.xml"))
        print build_docopt(executable)