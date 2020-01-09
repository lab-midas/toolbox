import argparse
import SimpleITK as sitk
import skimage
import nibabel as ni
import numpy as np
import matplotlib.pyplot as plt
import skimage.measure
from pathlib import Path


def isoncont(img, mask,
             b_out_labeled_mask=False,
             b_class_components=True,
             b_use_percentile_threshold=True,
             percentile_threshold=25,
             maximum_threshold=10,
             verbose=True):
    """
    Computes a mask based on percentile/relative maximum SUV value thresholds inside all
    connected components of the original mask.

    Args:
        img: Sitk PET-SUV image.
        mask: Tumor mask.
        b_out_labeled_mask: Output labeled component mask, no thresholding.
        b_class_components: Detected connected components and use component based threshold.
        b_use_percentile_threshold: Use percentile based thresholds (otherwise relative maximum value thresholds
                                    are used.
        percentile_threshold: Set percentile (SUV value) threshold in percent.
        maximum_threshold: Set relative maximum (SUV value) threshold.
        verbose:

    Returns: Sitk image with new mask.

    """
    maximum_threshold = float(maximum_threshold)

    # Get numpy array from sitk objects.
    amask = sitk.GetArrayFromImage(mask)
    aimg = sitk.GetArrayFromImage(img)

    # Classify connected image components
    if b_class_components:
        amask_comp, num_comp = skimage.measure.label(amask, neighbors=None, background=None, return_num=True,
                                                     connectivity=None)
    else:
        amask_comp = amask
        num_comp = 1

    print(f'Detected {num_comp} connected components.')

    # Create new mask based on the selected threshold.
    amask_th = np.zeros_like(amask)

    # Calculate SUV value thresholds for each connected component.
    for comp in range(num_comp):

        if verbose:
            print(f'Component {comp}')

        sel_comp = (amask_comp == (comp +1))
        # Get SUV values inside the selected component.
        suv_values = aimg[sel_comp]

        suv_max = np.max(suv_values)

        if verbose:
            print(f'#SUV values {suv_values.shape}')
            print(f'Max. SUV value: {np.max(suv_values)}')
            print(f'{percentile_threshold} percentile SUV value threshold {np.percentile(suv_values, percentile_threshold)}')
            print(f'Relative max. SUV value threshold ({maximum_threshold}%): {suv_max * maximum_threshold/100.0}')

        if b_use_percentile_threshold:
            th = np.percentile(suv_values, percentile_threshold)
        else:
            th = suv_max * maximum_threshold/100.0

        if verbose:
            print(f'Used threshold: {th}')

        amask_th = amask_th + \
                   np.logical_and(np.greater_equal(aimg, th), sel_comp)

    # Create mask_out sitk img. If out_labeled_mask, the output image just
    # contains the labeled connected component mask.
    mask_out = sitk.GetImageFromArray(amask_th.astype(np.uint8))
    if b_out_labeled_mask:
        mask_out = sitk.GetImageFromArray(amask_comp.astype(np.uint8))

    # Copy MetaData from original mask.
    mask_out.SetDirection(mask.GetDirection())
    mask_out.SetOrigin(mask.GetOrigin())
    mask_out.SetSpacing(mask.GetSpacing())

    return mask_out


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--pet',  help='pet image .nii file', required=True)
    parser.add_argument('-m', '--mask', help='mask .nii file', required=True)
    parser.add_argument('-o', '--out',  help='output .nii file')
    parser.add_argument('-l', '--Praefix', help='praefix for output filename')

    parser.add_argument('--ThresholdType', help='threshold type',
                        choices={'Maximum', 'Percentile'})

    parser.add_argument('-p', '--SetPercentileThreshold', help='percentile threshold (percent)', type=int)
    parser.add_argument('-q', '--SetMaximumThreshold', help='relative maximum threshold (percent)', type=int)
    parser.add_argument('-c', '--OutputCompLabels', help='output component label mask', action='store_true')
    parser.add_argument('-g', '--NoComponents', help='do not detect connected components first', action='store_true')
    parser.add_argument('-v', '--Verbose', help='verbose', action='store_true')

    args = parser.parse_args()

    path_pet = Path(args.pet)
    path_mask = Path(args.mask)
    # todo test if nii file exists
    path_mask_out = args.out
    if not path_mask_out:
        praefix = 'iso_'
        if args.Praefix:
            praefix = args.Praefix
        path_mask_out = path_mask.parent.joinpath(praefix + path_mask.name)

    maximum_threshold = 10.0
    if args.SetMaximumThreshold:
        maximum_threshold = float(args.SetMaximumThreshold)
    percentile_threshold = 25
    if args.SetPercentileThreshold:
        percentile_threshold = args.SetPercentileThreshold

    b_use_percentile_threshold = True
    if args.ThresholdType:
        if args.ThresholdType == 'Maximum':
            b_use_percentile_threshold = False

    # Read image and mask data.
    img = sitk.ReadImage(str(path_pet))
    mask = sitk.ReadImage(str(path_mask))

    verbose = args.Verbose
    b_class_components = not args.NoComponents
    b_out_labeled_mask = args.OutputCompLabels

    mask_out = isoncont(img, mask,
                        b_out_labeled_mask=b_out_labeled_mask,
                        b_class_components=b_class_components,
                        b_use_percentile_threshold=b_use_percentile_threshold,
                        percentile_threshold=percentile_threshold,
                        maximum_threshold=maximum_threshold,
                        verbose=verbose)

    writer = sitk.ImageFileWriter()
    writer.SetFileName(str(path_mask_out))
    writer.Execute(mask_out)


if __name__ == '__main__':
    main()