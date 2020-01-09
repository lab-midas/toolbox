import SimpleITK as sitk
import argparse
from pathlib import Path

def main():
    """ Shows basic information for nifti files.
    (Size, Spacing, Origin, Direction)

    Returns:

    """

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('nii', help='.nii file')
    parser.add_argument('-m', '--multiline', action="store_true", help="multi line output")
    args = parser.parse_args()
    nii_file = args.nii

    # Load nii file.
    reader = sitk.ImageFileReader()
    reader.SetImageIO('NiftiImageIO')
    reader.SetFileName(str(nii_file))
    img = reader.Execute()

    # todo switch one line / multi line output
    template = ' Size: {}{} Spacing: {}{} Origin: {}{} Direction: {}'
    sep = ''
    if args.multiline:
        sep = '\n'
    print(template.format(img.GetSize(), sep,
                          img.GetSpacing(), sep,
                          img.GetOrigin(), sep,
                          img.GetDirection()))

    # todo show metadata
    #print('MetaData:  '
    #for key in img.GetMetaDataKeys():
    #    print(key, ': ', img.GetMetaData(key))

if __name__ == '__main__':
    main()