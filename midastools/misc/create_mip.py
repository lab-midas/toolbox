import SimpleITK as sitk
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    print("NIFI-image information")

    parser = argparse.ArgumentParser()
    parser.add_argument('--nii', help='image .nii file')
    args = parser.parse_args()

    nii_file = vars(args)['nii']
    print(nii_file)
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

    mip_img = sitk.MaximumProjection(img, 1)
    print(mip_img.GetSize())

    plt.imshow(sitk.GetArrayFromImage(mip_img)[:, 0, :])
    plt.show()

if __name__ == '__main__':
    main()