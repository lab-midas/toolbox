from midastools.vtk import vtk_conversion, vtk_mesh
import SimpleITK as sitk
import numpy as np
import argparse
from pathlib import Path


def smooth_img(volume,
               smooth_filter='sinc',
               smooth_iter=40,
               relaxation=0.2):
    """Smooths mask volume.

    Args:
        volume (np.array): mask volume
        smooth_filter: 'sinc' oder 'laplacian'
        smooth_iter: laplacian smoothing parameters
        relaxation: laplacian smoothing parameters

    Returns: sitk image

    """
    vtk_data = vtk_conversion.np_to_vtk_data(volume)
    vtk_image = vtk_conversion.vtk_data_to_image(vtk_data, dims=3)

    vtk_poly = vtk_mesh.marching_cube(vtk_image)
    vtk_poly = vtk_mesh.smooth(vtk_poly, smooth_filter='laplacian')

    result = vtk_conversion.poly_to_img(vtk_poly)

    result = vtk_conversion.vtk_to_numpy_image(result)
    return result


def smooth_nii(nii_file,
               out_file,
               smooth_filter='sinc',
               smooth_iter=40,
               relaxation=0.2):
    """Smooths input nii file and saves the smoothed volume.
    
    Args:
        nii_file (str/Path): input nii mask file
        outpath (str/Path): output path to save modified file
        smooth_filter: 'sinc' oder 'laplacian'
        smooth_iter: laplacian smoothing parameters
        relaxation: laplacian smoothing parameters
    """
    img = sitk.ReadImage(str(nii_file))
    volume = sitk.GetArrayFromImage(img)
    volume = volume.transpose([2, 1, 0])

    result = smooth_img(volume,
                        smooth_filter='sinc',
                        smooth_iter=40,
                        relaxation=0.2)
    
    img_result = sitk.GetImageFromArray(result.transpose([2, 1, 0]))
    img_result.SetDirection(img.GetDirection())
    img_result.SetOrigin(img.GetOrigin())
    img_result.SetSpacing(img.GetSpacing())

    sitk.WriteImage(img_result, str(out_file))


def main():
    path = '/home/raheppt1/samples_aorta/000_aorta.nii'
    path_out = '/home/raheppt1/samples_aorta/000_aorta_smooth.nii'

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('nii_input', help='Input .nii file')
    parser.add_argument('-o', '--Output', help='Output .nii file')
    parser.add_argument('-p', '--Praefix', help='Praefix for output filename')

    parser.add_argument('-f', '--Filter', help='FilterType',
                        choices={'sinc', 'laplacian'})

    parser.add_argument('--smooth_iter', help='laplacian smoothing iterations', type=int)
    parser.add_argument('--relaxation', help='laplacian smoothing relaxation', type=float)
    args = parser.parse_args()

    nii_file = Path(args.nii_input)

    print(f'Smoothing nii image : {str(nii_file)} ...')

    out_file = args.Output
    if not out_file:
        praefix = 'smooth_'
        if args.Praefix:
            praefix = args.Praefix
        out_file = nii_file.parent.joinpath(praefix + nii_file.name)

    smooth_filter = 'sinc'
    if args.Filter:
        smooth_filter = args.Filter

    smooth_iter = 40
    if args.smooth_iter:
        smooth_iter = args.smooth_iter

    relaxation = 0.2
    if args.relaxation:
        relaxation = args.relaxation

    smooth_nii(nii_file, out_file, smooth_filter, smooth_iter, relaxation)


if __name__ == '__main__':
    main()
