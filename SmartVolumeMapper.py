

#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtk
import vtkmodules.vtkInteractionStyle
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkIOLegacy import vtkStructuredPointsReader
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersGeometry import vtkImageDataGeometryFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
#from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkCommonDataModel import (
    vtkCylinder,
    vtkSphere
)
from vtkmodules.vtkImagingCore import (
  vtkImageCast,
  vtkImageShiftScale
)
from vtkmodules.vtkRenderingCore import (
    vtkColorTransferFunction,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkVolume,
    vtkVolumeProperty
)
from vtkmodules.vtkRenderingVolume import vtkFixedPointVolumeRayCastMapper
# noinspection PyUnresolvedReferences
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkOpenGLRayCastImageDisplayHelper


def CreateImageData():
  # Create a spherical implicit function.
  sphere = vtkSphere()
  imageData = vtkImageData()

  sphere.SetRadius(0.1)
  sphere.SetCenter(0.0, 0.0, 0.0)

  _samplefunction = vtkSampleFunction()
  _samplefunction.SetImplicitFunction(sphere)
  _samplefunction.SetOutputScalarTypeToDouble()
  _samplefunction.SetSampleDimensions(127, 127,127) # intentional NPOT dimensions.
  _samplefunction.SetModelBounds(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
  _samplefunction.SetCapping(False)
  _samplefunction.SetComputeNormals(False)
  _samplefunction.SetScalarArrayName("values")
  _samplefunction.Update();

  a = _samplefunction.GetOutput().GetPointData().GetScalars("values")
  range = a.GetRange()

  t = vtkImageShiftScale()
  t.SetInputConnection(_samplefunction.GetOutputPort())

  t.SetShift(-range[0])
  magnitude = range[1] - range[0]
  if (magnitude == 0.0):
    magnitude = 1.0
  t.SetScale(255.0 / magnitude)
  t.SetOutputScalarTypeToUnsignedChar()
  t.Update()
  imageData.ShallowCopy(t.GetOutput())
  return imageData


def get_program_parameters():
  import argparse
  description = 'Read a VTK image data file.'
  epilogue = ''''''
  parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('filename', help='vase.vti')
  args = parser.parse_args()
  return args.filename

def main():
  imageData = vtkImageData()
  if (False):
    imageData = CreateImageData()
  else:
    reader = vtkXMLImageDataReader()
    #print(get_program_parameters())
    reader.SetFileName(get_program_parameters())
    reader.Update()
    imageData.ShallowCopy(reader.GetOutput())

  renWin = vtkRenderWindow()
  ren1 = vtkRenderer()
  ren1.SetBackground(0.1, 0.4, 0.2)
  renWin.AddRenderer(ren1)
  renWin.SetSize(301, 300) # intentional odd and NPOT  width/height
  iren = vtkRenderWindowInteractor()
  iren.SetRenderWindow(renWin)
  renWin.Render() # make sure we have an OpenGL context.

  volumeMapper = vtk.vtkSmartVolumeMapper()
  volumeMapper.SetBlendModeToComposite() # composite first
  volumeMapper.SetInputData(imageData)

  volumeProperty = vtkVolumeProperty()
  volumeProperty.ShadeOff()
 # volumeProperty.SetInterpolationType(VTK_LINEAR_INTERPOLATION)
  volumeProperty.SetInterpolationTypeToLinear()

  compositeOpacity = vtkPiecewiseFunction()
  compositeOpacity.AddPoint(0.0, 0.0)
  compositeOpacity.AddPoint(80.0, 1.0)
  compositeOpacity.AddPoint(80.1, 0.0)
  compositeOpacity.AddPoint(255.0, 0.0)
  volumeProperty.SetScalarOpacity(compositeOpacity) # composite first.

  color = vtkColorTransferFunction()
  color.AddRGBPoint(0.0, 0.0, 0.0, 1.0)
  color.AddRGBPoint(40.0, 1.0, 0.0, 0.0)
  color.AddRGBPoint(255.0, 1.0, 1.0, 1.0)
  volumeProperty.SetColor(color)

  volume = vtkVolume()
  volume.SetMapper(volumeMapper)
  volume.SetProperty(volumeProperty)
  ren1.AddViewProp(volume)
  ren1.ResetCamera()

  # Render composite. In default mode. For coverage.
  renWin.Render()

  # 3D texture mode. For coverage.
  #volumeMapper.SetRequestedRenderModeToRayCastAndTexture()
  renWin.Render()

  # Software mode, for coverage. It also makes sure we will get the same
  # regression image on all platforms.
  volumeMapper.SetRequestedRenderModeToRayCast()
  renWin.Render()
  iren.Start()

if __name__ == '__main__':
    main()
