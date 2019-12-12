import SimpleITK as sitk
import json
import argparse
from pathlib import Path


def load_image_data(filepath):
    reader = sitk.ImageFileReader()
    reader.SetImageIO('NiftiImageIO')
    reader.SetFileName(filepath)
    img = reader.Execute()
    return img


def load_dcm_data(dirpath):
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dirpath)
    reader.SetFileNames(dicom_names)
    return reader.Execute()


def resample_img(img, config):

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
    if config['interpolator'] == "BSpline":
        interpolator = sitk.sitkBSpline
    elif config['interpolator'] == "Linear":
        interpolator = sitk.sitkLinear
    elif config['interpolator'] == "NearestNeighbor":
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


def resample_img_to_ref(img, ref_img, config):

    # set interpolation type
    if config['interpolator'] == "BSpline":
        interpolator = sitk.sitkBSpline
    elif config['interpolator'] == "Linear":
        interpolator = sitk.sitkLinear
    elif config['interpolator'] == "NearestNeighbor":
        interpolator = sitk.sitkNearestNeighbor
    else:
        interpolator = sitk.sitkLinear

    default_value = config['DefaultValue']

    rs_img = sitk.Resample(img,
                           ref_img.GetSize(),
                           sitk.Transform(),
                           interpolator,
                           ref_img.GetOrigin(),
                           ref_img.GetSpacing(),
                           ref_img.GetDirection(),
                           default_value,
                           img.GetPixelIDValue())

    return rs_img


def main():
    print('Resample medical image date ')
    filepath = '/home/raheppt1/data/sample.nii'
    filepath_config = "resample/config.json"

    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')
    #args = parser.parse_args()
    #args.accumulate(args.integers)

    work_dir = Path('/home/raheppt1/data/')


    filepath_config = "resample/config_a.json"
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
    return


    with open(filepath_config, "r") as config_file:
        config = json.load(config_file)
        print(config['interpolator'])
        for file in files:
            print(file)
            img = load_image_data(str(file))
            rs_img = resample_img(img, config)
            writer = sitk.ImageFileWriter()
            outpath = file.parent.joinpath(file.name.replace('.nii', '_rs.nii'))
            writer.SetFileName(str(outpath))
            writer.Execute(rs_img)


if __name__ == '__main__':
    main()