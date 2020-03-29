import SimpleITK as sitk
import scipy.ndimage.morphology
from pathlib import Path
import argparse
import numpy as np


def fillholes_nii(nii_file,
                  out_file):
    """Binary fill holes using scipy.ndimage

    Args:
        nii_file (str/Path): input nii mask file
        out_file (str/Path): output path to save modified file
    """
    # Read nii image.
    mask = sitk.ReadImage(str(nii_file))

    # Binary fill holes.
    input_mask = sitk.GetArrayFromImage(mask)
    output_mask = fillholes(input_mask)
    filled_mask = sitk.GetImageFromArray(output_mask)
    filled_mask.SetDirection(mask.GetDirection())
    filled_mask.SetOrigin(mask.GetOrigin())
    filled_mask.SetSpacing(mask.GetSpacing())

    # Write result to outpath.
    writer = sitk.ImageFileWriter()
    print("Writing output to :", out_file)
    writer.SetFileName(str(out_file))
    writer.Execute(filled_mask)


def fillholes(input_mask):
    """Binary fill holes using scipy.ndimage
    
    Args:
        input_mask (np.array): input mask
    
    Returns:
        np.array: filled mask
    """
    output_mask= scipy.ndimage.morphology.binary_fill_holes(input_mask)
    output_mask = output_mask.astype(np.uint8)
    return output_mask


def main():
    # Commandline argument parsing.
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('nii_input', help='Input .nii file')
    parser.add_argument('-p', '--Praefix', help='Praefix for output filename')
    parser.add_argument('-o', '--Output', help='Output .nii file')
    args = parser.parse_args()

    nii_file = Path(args.nii_input)

    print('Filling mask holes, nii image : ', str(nii_file))

    # If outpath is not set, use praefix and input filepath.
    outpath = args.Output
    if not outpath:
        praefix = 'filled_'
        if args.Praefix:
            praefix = args.Praefix
        outpath = nii_file.parent.joinpath(praefix + nii_file.name)

    fillholes_nii(nii_file, outpath)


if __name__ == '__main__':
    main()
