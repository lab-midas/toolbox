import SimpleITK as sitk
import json
import argparse
import numpy as np
from pathlib import Path


def load_image_data(filepath):
    """ Loads nii file into sitk image object.

    Args:
        filepath: Path (str/pathlib) to nii file.

    Returns: sitk image

    """
    reader = sitk.ImageFileReader()
    reader.SetImageIO('NiftiImageIO')
    reader.SetFileName(str(filepath))
    img = reader.Execute()
    return img


def load_dcm_data(dirpath):
    """ Reads dicom directory into sitk image object.

    Args:
        dirpath: dicom directory path

    Returns: sitk image

    """
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dirpath)
    reader.SetFileNames(dicom_names)
    return reader.Execute()


def resample_img_to_ref(img, config, ref_img=None):
    """ Resample and alignes image to reference image.
    
    Overwrite target spacing, size, origin and direction if specified
    in the configuration file.

    Args:
        img: sitk image (sitk object)
        ref_img: reference image (sitk object)
        config: dictionary with target and interpolation parameters.

    Returns:
        Resampled image (sitk object)

    """
    # Set interpolation type.
    if config['Interpolator'] == "BSpline":
        interpolator = sitk.sitkBSpline
    elif config['Interpolator'] == "Linear":
        interpolator = sitk.sitkLinear
    elif config['Interpolator'] == "NearestNeighbor":
        interpolator = sitk.sitkNearestNeighbor
    else:
        interpolator = sitk.sitkLinear

    # If no reference image is given, use the parameters of the
    # input image.
    if not ref_img:
        ref_img = img

    # Read parameters from config.
    target_size = img.GetSize()
    target_spacing = img.GetSpacing()

    if config['SetTargetSpacing'] is None:
        target_spacing = ref_img.GetSpacing()
    else:
        target_spacing = config['SetTargetSpacing']
        # For values <= keep the spacing from img.
        for i, space in enumerate(target_spacing, 0):
            if space <= 0:
                target_spacing[i] = ref_img.GetSpacing()[i]

    if config['SetTargetSize'] is None:
        target_size = ref_img.GetSize()
    else:
        target_size = config['SetTargetSize']
        target_size = target_size.tolist()

        for i, size in enumerate(target_size, 0):
            # For values < 0 compute the size from target spacing.
            # For zero values keep the size from img.
            if size == 0:
                target_size[i] = ref_img.GetSize()[i]
            elif size < 0:
                img_size = ref_img.GetSize()[i]
                img_spacing = ref_img.GetSpacing()[i]
                new_spacing = target_spacing[i]
                target_size[i] = int(img_size*img_spacing/new_spacing)

    target_origin = img.GetOrigin()
    if config['SetTargetOrigin'] is None:
        target_origin = ref_img.GetOrigin()
    else:
        target_origin = config['SetTargetOrigin']

    target_direction = img.GetDirection()
    if config['SetTargetDirection'] is None:
        target_direction = ref_img.GetDirection()
    else:
        target_direction = config['SetTargetDirection']

    default_value = config['DefaultValue']

    rs_img = sitk.Resample(img,
                           target_size,
                           sitk.Transform(),
                           interpolator,
                           np.array(target_origin).astype(float),
                           np.array(target_spacing).astype(float),
                           np.array(target_direction).astype(float),
                           float(default_value),
                           img.GetPixelIDValue())

    return rs_img


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('nii_input', help='Input .nii file')
    parser.add_argument('-r', '--Reference', help='Reference .nii file')
    parser.add_argument('-o', '--Output', help='Output .nii file')
    parser.add_argument('-p', '--Praefix', help='Praefix for output filename')

    parser.add_argument('-I', '--Interpolator', help='Interpolator',
                        choices={'BSpline', 'NearestNeighbor', 'Linear'}, required=True)
    parser.add_argument('--SetSize', help='Target size: x.x,y.y,z.z')
    parser.add_argument('--SetSpacing', help='Target spacing (3d): x.x,y.y,z.z')
    parser.add_argument('--SetOrigin', help='Target origin (3d): x.x,y.y,z.z')
    parser.add_argument('--SetDirection', help='Target direction (9d): x.x,... ')
    parser.add_argument('-d', '--DefaultValue', help='Interpolation default value', type=float)
    args = parser.parse_args()

    nii_file = Path(args.nii_input)
    ref_file = args.Reference
    out_file = args.Output
    if not out_file:
        praefix = 'rs_'
        if args.Praefix:
            praefix = args.Praefix
        out_file = nii_file.parent.joinpath(nii_file.name.replace('.nii', praefix+'.nii'))
    
    print(f'Resample nii image: {str(nii_file)}')
    print(f'Reference: {str(ref_file)}')

    # create configuration dictionary
    config = {}
    config['Interpolator'] = args.Interpolator

    default_val = args.DefaultValue
    if not default_val:
        default_val = 0.0
    config['DefaultValue'] = default_val

    if args.SetSize:
        config['SetTargetSize'] = np.fromstring(args.SetSize, sep=',').astype(np.int)
    else:
        config['SetTargetSize'] = None

    if args.SetSpacing:
        config['SetTargetSpacing'] = np.fromstring(args.SetSpacing, sep=',').astype(np.float)
    else:
        config['SetTargetSpacing'] = None

    if args.SetOrigin:
        config['SetTargetOrigin'] = np.fromstring(args.SetOrigin, sep=',').astype(np.float)
    else:
        config['SetTargetOrigin'] = None

    if args.SetDirection:
        config['SetTargetDirection'] = np.fromstring(args.SetDirection, sep=',').astype(np.float)
    else:
        config['SetTargetDirection'] = None

    img = load_image_data(nii_file)
    ref_img = None
    if ref_file:
        ref_img = load_image_data(ref_file)

    print(config)
    # Resample image
    img_rs = resample_img_to_ref(img, config, ref_img)

    # Write output nii file.
    writer = sitk.ImageFileWriter()
    writer.SetFileName(str(out_file))
    writer.Execute(img_rs)

if __name__ == '__main__':
    main()
