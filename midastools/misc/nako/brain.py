import tempfile
import re
import shutil
import time
import subprocess
import argparse
import tempfile
from pathlib import Path
import dicom2nifti
from zipfile import ZipFile
import SimpleITK as sitk
import nibabel as nib
import intensity_normalization
from nipype.interfaces import fsl


def n4_bias_field_correction(input_file,
                             output_file,
                             mask_file=None,
                             number_iterations=[50,50,50,50]):
    """ N4 bias field correction for brain mri.
    
    Additional information:
    https://simpleitk.readthedocs.io/en/latest/Examples/N4BiasFieldCorrection/Documentation.html
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3071855/

    Args:
        input_file (str/Path): nii input file
        output_file (str/Path): nii output file
        mask_file (str/Path, optional): path to store nii mask. Defaults to None.
        number_iterations (list, optional): Iterations per level. Defaults to [50,50,50].
    """

    input_img = sitk.ReadImage(str(input_file))
    mask_image = sitk.OtsuThreshold(input_img, 0, 1, 200)
    input_img = sitk.Cast(input_img, sitk.sitkFloat32)
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    corrector.SetMaximumNumberOfIterations(number_iterations)
    output_img = corrector.Execute(input_img, mask_image)
    sitk.WriteImage(output_img, str(output_file))
    if mask_file:
        sitk.WriteImage(mask_image, str(mask_file))


def flirt_registration(input_file,
                       output_file,
                       matrix_file,
                       ref_file,
                       verbose=False):
    """Registration to MNI template using FSL-FLIRT
    
    Ubuntu: Create link for flirt
    sudo ln -s /usr/bin/fsl5.0-flirt /usr/bin/flirt

    Args:
        input_file (str/Path): input file (nii.gz)
        output_file (str/Path): output file (nii.gz)
        matrix_file (str/Path): transformation matrix (.mat)
        ref_file (str/Path): path to MNI-152-1mm reference file (nii.gz)
        verbose (bool): print fsl command 
    """
    flt = fsl.FLIRT(bins=256, cost_func='mutualinfo')
    flt.inputs.in_file = str(input_file)
    flt.inputs.reference = str(ref_file)
    flt.inputs.output_type = "NIFTI_GZ"
    if not verbose:
        flt.inputs.verbose=0
    flt.inputs.out_file = str(output_file)
    flt.inputs.out_matrix_file = str(matrix_file)
    if verbose:
        print(flt.cmdline)
    flt.run()


def robex_skull_stripping(input_file,
                          output_file,
                          mask_file,
                          robex_dir,
                          verbose):
    """Skull stripping using ROBEX
    
    Create stripped output (nii.gz) and brain mask (nii.gz).
    Publication: http://pages.ucsd.edu/~ztu/publication/TMI11_ROBEX.pdf
    Download and extract ROBEX 1.3 from https://www.nitrc.org/projects/robex

    Args:
        input_file (str/Path): input file (nii.gz)
        output_file (str/Path): output file (nii.gz)
        mask_file (str/Path): output mask file (nii.gz)
        robex_dir (str/Path):  extracted ROBEX archive
        verbose (bool): print stdout from ROBEX 
    """
    robex_dir = Path(robex_dir)
    out = subprocess.Popen([str(robex_dir.joinpath('ROBEX')),
                            str(input_file),
                            str(output_file),
                            str(mask_file)],
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,
                            cwd=str(robex_dir))
    stdout, stderr = out.communicate()
    if verbose:
        print(stdout)
        print(stderr)
    return


def fcm_normalize(input_file,
                  mask_file,
                  output_file,
                  output_mask):
    """Fuzzy C-means (FCM)-segmentation-based white matter (WM) mean normalization
    
    Computes normalized image and the wm mask.

    Paper: https://arxiv.org/abs/1812.04652

    Install the following package (git clone + pip install ./)
    https://github.com/jcreinhold/intensity-normalization
    Requirements have to be installed manually! 
    (matplotlib, numpy, nibabel, scikit-fuzzy, scikit-learn, scipy, statsmodel)

    Args:
        input_file (str/Path): input file (nii.gz)
        mask_file (str/Path):  brain mask (nii.gz) file (e.g. created by ROBEX)
        output_file (str/Path): path to normalized output (nii.gz)
        output_mask (str/Path): path to wm mask (nii.gz)
    """

    img = nib.load(str(input_file))
    brain_mask = nib.load(str(mask_file))

    wm_mask = intensity_normalization.normalize.fcm.find_tissue_mask(img, brain_mask)
    normalized = intensity_normalization.normalize.fcm.fcm_normalize(img, wm_mask)

    nib.save(wm_mask, str(output_mask))
    nib.save(normalized, str(output_file))

    return output_file, output_mask


def process_brain_t1(input_file,
                     output_dir,
                     reference_file='/mnt/qdata/tools/fsl/ref/MNI152_T1_1mm.nii.gz',
                     robex_dir='/mnt/qdata/tools/robex',
                     split=0,
                     verbose=False):
    print(split)    
    input_file = Path(input_file)
    reference_file = Path(reference_file)
    output_dir = Path(output_dir)

    # create output directories
    output_dir.joinpath('raw').mkdir(exist_ok=True)
    #output_dir.joinpath('n4').mkdir(exist_ok=True) tmp 
    output_dir.joinpath('n4_flirt').mkdir(exist_ok=True)
    #output_dir.joinpath('n4_flirt_robex').mkdir(exist_ok=True)
    output_dir.joinpath('n4_flirt_robex_fcm').mkdir(exist_ok=True) # and robex mask, delete robex output

    # start timer
    t = time.time()

    # bias field correction
    print('(n4) bias field correction ...')
    n4_file = output_dir.joinpath(
        'n4_flirt', input_file.name.replace('.nii.gz', '_n4.nii.gz'))
    # split < -1 process the whole pipeline at once
    # split == 0 bias field corrections only ...
    if split <= 0: 
        n4_bias_field_correction(input_file, n4_file)

    # split < -1 process the whole pipeline at once
    # split == 1 continue with coregistration ...
    if split < 0 or split == 1:
        # mni coregistration
        print('(fsl-flirt) mni template registration ...')
        input_file = n4_file
        n4_flirt_file = output_dir.joinpath(
        'n4_flirt', input_file.name.replace('.nii.gz', '_flirt.nii.gz'))
        n4_flirt_matrix = output_dir.joinpath(
        'n4_flirt', input_file.name.replace('.nii.gz', '_flirt.mat'))
        flirt_registration(input_file, n4_flirt_file,
                        n4_flirt_matrix, reference_file, verbose=verbose)

        # robex skull stripping 
        print('(robex) skull stripping ...')
        input_file = n4_flirt_file
        n4_flirt_robex_file = output_dir.joinpath('n4_flirt_robex_fcm',
                                                    input_file.name.replace('.nii.gz', '_robex.nii.gz'))
        n4_flirt_robex_mask = output_dir.joinpath('n4_flirt_robex_fcm',
                                                    input_file.name.replace('.nii.gz', '_robexmask.nii.gz'))
        robex_skull_stripping(input_file, 
                            n4_flirt_robex_file,
                            n4_flirt_robex_mask,
                            robex_dir,
                            verbose=verbose)
        # delete stripped mri (can be produced later on, using the dilated mask)
        n4_flirt_robex_file.unlink()

        print('(fcm) intensity normalization')
        input_file = n4_flirt_file
        mask_file = n4_flirt_robex_mask
        n4_flirt_fcmwmmask = str(output_dir.joinpath('n4_flirt_robex_fcm',
            input_file.name.replace('.nii.gz', '_fcmwmmask.nii.gz')))
        n4_flirt_fcmnorm= str(output_dir.joinpath('n4_flirt_robex_fcm',
            input_file.name.replace('.nii.gz', '_fcmnorm.nii.gz')))
        fcm_normalize(input_file, 
                    mask_file,
                    n4_flirt_fcmnorm,
                    n4_flirt_fcmwmmask)

    # stop timer
    elapsed_time = time.time() - t
    if verbose:
        print(f'elapsed time: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))}')


def main():
    parser = argparse.ArgumentParser(description='Preprocessing pipeline for NAKO T1 brain MRI data.\n'\
                                                'N4 bias field correction\n'\
                                                'FLIRT MNI152 coregistration\n'\
                                                'ROBEX skull stripping\n'\
                                                'FCM WM intensity normalization')
    parser.add_argument('input_file', help='Input file (T1w brain MRI, .nii.gz)')
    parser.add_argument('output_dir', help='Output directory to store processed files.')
    parser.add_argument('--reference', help='MNI152-1mm reference .nii.gz file')
    parser.add_argument('--robex', help='ROBEX installation directory.')
    parser.add_argument('--split', help='Split bias field correction (0) from the followings steps (1). Process at once (-1).', type=int)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        print(Path(args.input_file).name)

    reference_file = '/mnt/qdata/tools/fsl/ref/MNI152_T1_1mm.nii.gz'
    if args.reference:
        reference_file = args.reference

    robex_dir = '/mnt/qdata/tools/robex'
    if args.robex:
        robex_dir = args.robex

    split = 0
    if args.split:
        split = args.split

    process_brain_t1(args.input_file,
                     args.output_dir,
                     reference_file=reference_file,
                     robex_dir=robex_dir,
                     split=split,
                     verbose=args.verbose)


if __name__ == '__main__':
    main()
