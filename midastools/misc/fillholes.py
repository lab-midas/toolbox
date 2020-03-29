import SimpleITK as sitk
import scipy.ndimage.morphology
from pathlib import Path
import argparse
import numpy as np


def fillholes(nii_file,
              outpath):
    """Binary fill holes using scipy.ndimage

    Args:
        nii_file (str/Path): input nii mask file
        outpath (str/Path): output path to save modified file
    """

     # Read nii image.
    label = sitk.ReadImage(str(nii_file))
    print(label.GetSize())

    # Binary fill holes.
    input = sitk.GetArrayFromImage(label)
    output = scipy.ndimage.morphology.binary_fill_holes(input)
    output = output.astype(np.uint8)

    filled_label = sitk.GetImageFromArray(output)
    filled_label.SetDirection(label.GetDirection())
    filled_label.SetOrigin(label.GetOrigin())
    filled_label.SetSpacing(label.GetSpacing())
    #for index, x in np.ndenumerate(output):
    #   label.SetPixel(index[2], index[1], index[0], int(x))

    # Write result to outpath.
    writer = sitk.ImageFileWriter()
    print("Writing output to :", outpath)
    writer.SetFileName(str(outpath))
    writer.Execute(filled_label)


def main():
    # Commandline argument parsing.
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('nii_input', help='Input .nii file')
    parser.add_argument('-p', '--Praefix', help='Praefix for output filename')
    parser.add_argument('-o', '--Output', help='Output .nii file')
    args = parser.parse_args()

    nii_file = Path(args.nii_input)

    print('filling mask holes, nii image : ', str(nii_file))

    # If outpath is not set, use praefix and input filepath.
    outpath = args.Output
    if not outpath:
        praefix = 'filled_'
        if args.Praefix:
            praefix = args.Praefix
        outpath = nii_file.parent.joinpath(praefix + nii_file.name)

    fillholes(nii_file, outpath):

if __name__ == '__main__':
    main()
