import SimpleITK as sitk
import argparse
import numpy as np
from pathlib import Path
from skimage.measure import label


def lcomp(mask):
    """Computes largest connected component for binary mask.
    
    Args:
        mask (np.array): input binary mask
    
    Returns:
        np.array: largest connected component
    """

    labels = label(mask)
    unique, counts = np.unique(labels, return_counts=True)
    # the 0 label is by default background so take the rest
    list_seg = list(zip(unique, counts))[1:]
    largest = max(list_seg, key=lambda x: x[1])[0]
    labels_max = (labels == largest).astype(np.uint8)
    return labels_max


def lcomp_nii(nii_file,
              out_file):
    """Computes largest connected component for binary mask nii file.

    Args:
        nii_file (str/Path): input binary mask (nii)
        out_file (str/Path): largest component mask (nii)

    """
    # Read nii image.
    mask = sitk.ReadImage(str(nii_file))

    # Select largest component.
    input_mask = sitk.GetArrayFromImage(mask)
    lcomp_mask = lcomp(input_mask)

    lcomp_mask = sitk.GetImageFromArray(lcomp_mask)
    lcomp_mask.SetDirection(mask.GetDirection())
    lcomp_mask.SetOrigin(mask.GetOrigin())
    lcomp_mask.SetSpacing(mask.GetSpacing())

    # Write result to outpath.
    writer = sitk.ImageFileWriter()
    print("Writing output to :", out_file)
    writer.SetFileName(str(out_file))
    writer.Execute(lcomp_mask)
         

def main():
     # Commandline argument parsing.
    parser = argparse.ArgumentParser(description='Select largest connected component')
    parser.add_argument('nii_input', help='Input .nii file')
    parser.add_argument('-p', '--Praefix', help='Praefix for output filename')
    parser.add_argument('-o', '--Output', help='Output .nii file')
    args = parser.parse_args()

    nii_file = Path(args.nii_input)

    print('Selecting largest component, nii image : ', str(nii_file))

    # If outpath is not set, use praefix and input filepath.
    outpath = args.Output
    if not outpath:
        praefix = 'lcomp_'
        if args.Praefix:
            praefix = args.Praefix
        outpath = nii_file.parent.joinpath(praefix + nii_file.name)

    lcomp_nii(nii_file, outpath)


if __name__ == '__main__':
    main()
