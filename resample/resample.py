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


def resample_img(img, config):
    """ Resample image object to target spacing and size and
        transforms to target origin and direction.

    Args:
        img: sitk image
        config: Dictionary with target and interpolation parameters.

    Returns: Resampled and transformed sitk image.

    """
    # read parameters from config
    target_size = img.GetSize()
    if config['SetTargetSize']:
        target_size = config['TargetSize']

    target_spacing = img.GetSpacing()
    if config['SetTargetSpacing']:
        target_spacing = config['TargetSpacing']

    target_origin = img.GetOrigin()
    if config['SetTargetOrigin']:
        target_origin = config['TargetOrigin']

    target_direction = img.GetDirection()
    if config['SetTargetDirection']:
        target_direction = config['TargetDirection']

    default_value = config['DefaultValue']

    # set interpolation type
    if config['Interpolator'] == "BSpline":
        interpolator = sitk.sitkBSpline
    elif config['Interpolator'] == "Linear":
        interpolator = sitk.sitkLinear
    elif config['Interpolator'] == "NearestNeighbor":
        interpolator = sitk.sitkNearestNeighbor
    else:
        interpolator = sitk.sitkLinear

    rs_img = sitk.Resample(img,
                           target_size,
                           sitk.Transform(),
                           interpolator,
                           target_origin,
                           target_spacing,
                           target_direction,
                           default_value,
                           img.GetPixelIDValue())

    return rs_img


def resample_img_to_ref(img, config, ref_img=None):
    """ Resample and alignes image to reference image.
        Overwrite target spacing, size, origin and direction if given
        in configuration file.

    Args:
        img: sitk image
        ref_img: sitk image
        config: Dictionary with target and interpolation parameters.

    Returns:

    """
    # set interpolation type
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

    # read parameters from config
    target_size = img.GetSize()

    if config['SetTargetSize'] is None:
        target_size = ref_img.GetSize()
    else:
        target_size = config['SetTargetSize']
        target_size = target_size.tolist()

    target_spacing = img.GetSpacing()
    if config['SetTargetSpacing'] is None:
        target_spacing = ref_img.GetSpacing()
    else:
        target_spacing = config['SetTargetSpacing']

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


def align_and_resample_dir():
    work_dir = Path('/mnt/data/projects/PET/BClesions/normal')
    filepath_config = "/home/raheppt1/projects/toolbox/resample/config_a.json"
    with open(filepath_config, "r") as config_file:
        config = json.load(config_file)

        files = list(work_dir.glob(config['pattern_img']))
        files.sort()
        reffiles = list(work_dir.glob(config['pattern_ref']))
        reffiles.sort()

        for file in zip(files, reffiles):
            print(file)
            img = load_image_data(str(file[0]))
            refimg = load_image_data(str(file[1]))
            rs_img = resample_img_to_ref(img, refimg, config)
            writer = sitk.ImageFileWriter()
            outpath = file[0].parent.joinpath(file[0].name.replace('.nii', '_rs.nii'))
            writer.SetFileName(str(outpath))
            writer.Execute(rs_img)


def resample_dir():
    work_dir = Path('/mnt/data/projects/PET/BClesions/normal')
    filepath_config = "config.json"
    with open(filepath_config, "r") as config_file:
        config = json.load(config_file)
        files = list(work_dir.glob(config['pattern_img']))
        print(config['interpolator'])
        for file in files:
            print(file)
            img = load_image_data(str(file))
            rs_img = resample_img(img, config)
            writer = sitk.ImageFileWriter()
            outpath = file.parent.joinpath(file.name.replace('.nii', '_rs.nii'))
            writer.SetFileName(str(outpath))
            writer.Execute(rs_img)


def main():
    filepath = '/home/raheppt1/data/sample.nii'
    filepath_config = "resample/config.json"

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

    print('Resample nii image : ',str(nii_file))
    # todo test if nii file exists
    out_file = args.Output
    if not out_file:
        praefix = 'rs_'
        if args.Praefix:
            praefix = args.Praefix
        out_file = nii_file.parent.joinpath(praefix+nii_file.name)

    ref_file = args.Reference
    print(f'Reference: {ref_file}')
    # todo test if ref nii file exists

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

    #
    #  "interpolator": "BSpline", "NearestNeighbor", "Linear"
    #  "DefaultValue": 0.0,
    #
    #  "RefImage": false
    #  "SetTargetSize": false,
    #  "SetTargetSpacing": false,
    #  "SetTargetOrigin": false,
    #  "SetTargetDirection": false


    #work_dir = Path('/mnt/data/')

    #resample_dir()

    #np.fromstring('1, 2', dtype=int, sep=',')

if __name__ == '__main__':
    main()