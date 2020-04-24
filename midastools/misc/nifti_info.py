import SimpleITK as sitk
import argparse
from pathlib import Path
import nibabel as nib

# todo orientation
def main():
    """ Shows basic information for nifti files.
    (Size, Spacing, Origin, Direction)

    Returns:

    """

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('nii', help='.nii file')
    parser.add_argument('-m', '--multiline', action="store_true", help="multi line output")
    parser.add_argument('-s', '--short', action="store_true", help="short output (size, spacing)")
    args = parser.parse_args()
    nii_file = args.nii

    # Load nii file.
    reader = sitk.ImageFileReader()
    reader.SetImageIO('NiftiImageIO')
    reader.SetFileName(str(nii_file))
    img = reader.Execute()
    affine = nib.load(nii_file).affine
    
    sep = ''

    if args.multiline:
        sep = '\n'

    if args.short:
        template = ' Size: {}{} Spacing: {}{} Orientation: {}'
        print(template.format(img.GetSize(), sep,
                              img.GetSpacing(), sep,
                              nib.aff2axcodes(affine)))

    else:
        template = ' Size: {}{} Spacing: {}{} Origin: {}{} Direction: {}{} Orientation: {}'
        print(template.format(img.GetSize(), sep,
                              img.GetSpacing(), sep,
                              img.GetOrigin(), sep,
                              img.GetDirection(), sep,
                              nib.aff2axcodes(affine)))

if __name__ == '__main__':
    main()