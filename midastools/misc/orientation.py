import argparse
import numpy as np
import nibabel as nib
from pathlib import Path
from nibabel.orientations import ornt_transform, axcodes2ornt, inv_ornt_aff, apply_orientation, io_orientation, aff2axcodes


def reorient_nii_file(input_file,
                    output_file,
                    target_orientation = ('L', 'A', 'S')):
    input_file = Path(input_file)
    output_file = Path(output_file)
    print('reorient nifti files ...')
    print(f'{input_file.name} -> {output_file.name}')
    img = nib.load(str(input_file))
    new_img = reorient_nii(img, target_orientation)
    nib.save(new_img, str(output_file))

def reorient_nii(img,
                 target_orientation = ('L', 'A', 'S')):
    new_ornt = axcodes2ornt(target_orientation)
    vox_array = img.get_fdata()
    affine = img.affine
    orig_ornt = io_orientation(img.affine)
    ornt_trans = ornt_transform(orig_ornt, new_ornt)
    orig_shape = vox_array.shape
    new_vox_array = apply_orientation(vox_array, ornt_trans)
    aff_trans = inv_ornt_aff(ornt_trans, orig_shape)
    new_affine = np.dot(affine, aff_trans)
    print(f'{aff2axcodes(affine)} -> {aff2axcodes(new_affine)}')
    new_img = nib.Nifti1Image(new_vox_array, new_affine, img.header)
    return new_img

def main():
    # reorient nifti files to LAS coordinate system
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input nii file", required=True)
    parser.add_argument('-o', '--output',  help="output nii file", required=True)
    parser.add_argument('-t', '--orientation', help="target orientation", required=True)
    args = parser.parse_args()

    args.orientation = tuple([c for c in args.orientation])
    reorient_nii_file(args.input, args.output, args.orientation)

if __name__ == '__main__':
    main()