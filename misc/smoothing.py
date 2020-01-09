from med_shape.utils_vtk import vtk_conversion, vtk_mesh
import SimpleITK as sitk
import numpy as np

path = '/home/raheppt1/samples_aorta/000_aorta.nii'
path_out = '/home/raheppt1/samples_aorta/000_aorta_smooth.nii'

img = sitk.ReadImage(path)
volume = sitk.GetArrayFromImage(img)
volume = volume.transpose([2, 1, 0])
vtk_data = vtk_conversion.np_to_vtk_data(volume)
vtk_image = vtk_conversion.vtk_data_to_image(vtk_data,
                                             dims=img.GetSize(),
                                             origin=img.GetOrigin(),
                                             spacing=img.GetSpacing())

vtk_poly = vtk_mesh.marching_cube(vtk_image)
vtk_poly = vtk_mesh.smooth(vtk_poly, smooth_filter='laplacian')

result = vtk_conversion.poly_to_img(vtk_poly,
                                    origin=img.GetOrigin(),
                                    dim=img.GetSize(),
                                    spacing=img.GetSpacing())

result = vtk_conversion.vtk_to_numpy_image(result)


img_result = sitk.GetImageFromArray(result.transpose([2, 1, 0]))
img_result.SetDirection(img.GetDirection())
img_result.SetOrigin(img.GetOrigin())
img_result.SetSpacing(img.GetSpacing())
sitk.WriteImage(img_result, path_out)