import argparse
import SimpleITK as sitk
import skimage
import nibabel as ni

import matplotlib.pyplot as plt


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--pet', help='pet image .nii file')
    parser.add_argument('--label', help='label .nii file')
    parser.add_argument('--out', help='isocont label .nii file')
    args = parser.parse_args()
    path_pet = vars(args)['pet']
    path_label = vars(args)['label']
    path_out = vars(args)['out']

    path_pet = '/mnt/data/projects/PET/BClesions/tumour/0011_petsuv.nii'
    path_label = '/mnt/data/projects/PET/BClesions/tumour/0011_tumor.nii.gz'
    reader = sitk.ImageFileReader()
    reader.SetImageIO('NiftiImageIO')
    reader.SetFileName(path_pet)
    img_pet = reader.Execute()
    reader.SetFileName(path_label)
    img_label = reader.Execute()

    print(img_label.GetSize())
    plt.imshow(sitk.GetArrayFromImage(img_pet)[:,120,:])
    plt.show()

    # skimage.measure.label(input, neighbors=None, background=None, return_num=False, connectivity=None)

if __name__ == '__main__':
    main()