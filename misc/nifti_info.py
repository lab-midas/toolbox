import SimpleITK as sitk
import argparse
from pathlib import Path

def main():
    """ Shows basic information for nifti files.
    (Size, Spacing, Origin, Direction)

    Returns:

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('nii', help='image .nii file', required=True)
    args = parser.parse_args()

    nii_file = args.nii
    if not nii_file:
        print('please specifiy .nii file')
        return 1
    nii_file = Path(nii_file)
    if not nii_file.exists():
        print(str(nii_file), ' does not exist.')

    reader = sitk.ImageFileReader()
    reader.SetImageIO('NiftiImageIO')
    reader.SetFileName(str(nii_file))
    img = reader.Execute()

    print('Size:      ', img.GetSize())
    print('Spacing:   ', img.GetSpacing())
    print('Origin:    ', img.GetOrigin())
    print('Direction: ', img.GetDirection())

    # todo switch one line / multi line output
    print('Size {} Spacing {} Origin {} Direction {}'.format(img.GetSize(),
                                                             img.GetSpacing(),
                                                             img.GetOrigin(),
                                                             img.GetDirection()))

    # todo show metadata
    #print('MetaData:  ')
    #for key in img.GetMetaDataKeys():
    #    print(key, ': ', img.GetMetaData(key))


if __name__ == '__main__':
    main()