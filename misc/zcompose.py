import SimpleITK as sitk
from pathlib import Path
import numpy as np


def sort_imgs(imgs):

    for i in range(len(imgs)):
        im = imgs[i]
        last_slice = im.GetSize()[2] - 1
        start_z = im.TransformIndexToPhysicalPoint([0, 0, 0])[2]
        end_z = im.TransformIndexToPhysicalPoint([0, 0, last_slice])[2]

        if end_z < start_z:
            imgs[i] = sitk.Flip(imgs[i], flipAxes=(False, False, True))

    def get_min_z(im):
        last_slice = im.GetSize()[2]-1
        start_z = im.TransformIndexToPhysicalPoint([0, 0, 0])[2]
        end_z = im.TransformIndexToPhysicalPoint([0, 0, last_slice])[2]
        return min([start_z, end_z])

    imgs = sorted(imgs, key=get_min_z)
    return imgs

def compose_imgs(imgs):
    """
    Composes nii files along the z-axis.
    Assumptions: XY-shape and spacing has to be the same for all images.

    Args:
        imgs: List of sitk image objects.

    Returns: Composed (sitk) image.

    """

    print([im.GetOrigin() for im in imgs])
    for i in range(1, len(imgs)):
        # Get the coordinates of the last slice (max. z-coord.) of the previous image.
        idx_last_slice = imgs[i-1].GetSize()[2] - 1
        z_last_slice = imgs[i-1].TransformIndexToPhysicalPoint([0, 0, idx_last_slice])
        # Get the corresponding slice index of the following image.
        idx_slice = imgs[i].TransformPhysicalPointToIndex(z_last_slice)[2]
        delta_slices = idx_slice + 1
        # Crop both images.
        crop_a = int(delta_slices/2)
        crop_b = delta_slices - crop_a
        imgs[i] = imgs[i][:, :, crop_a:]
        imgs[i-1] = imgs[i-1][:, :, :(idx_last_slice + 1 - crop_b)]
        # Alternative:
        # Start with the next slice. Crop the other slices of the following image.
        # imgs[i] = imgs[i][:, :, (idx_slice+1):]
        # todo mean in overlay areas

    # Get numpy arrays for the (cropped) images
    img_arrays = []
    for i in range(0, len(imgs)):
        img_arrays.append(sitk.GetArrayFromImage(imgs[i]).transpose([2, 1, 0]))
    # Concatenate arrays to one common array.
    img_array = np.concatenate(img_arrays, axis=2)
    # Convert array back to sitk image and copy meta information vom imgs[0].
    img_composed = sitk.GetImageFromArray(img_array.transpose([2, 1, 0]))
    img_composed.SetDirection(imgs[0].GetDirection())
    img_composed.SetOrigin(imgs[0].GetOrigin())
    img_composed.SetSpacing(imgs[0].GetSpacing())

    return img_composed


def main():
    #work_dir = Path('/home/raheppt1/data_samples/compose')
    #path_composed = Path('/home/raheppt1/data_samples/compose/composed.nii')
    #nii_files = list(work_dir.glob('F*nii*'))

    work_dir = Path('/mnt/share/nora/imgdata/UKB3001ABDS')
    path_composed = Path('/home/raheppt1/data_samples/compose/composed.nii')
    subj_dir = work_dir.glob('**/Dixon_BH*')
    sequence = 'opp'

    for dir in subj_dir:
        nii_files = list(dir.glob(sequence+'_s*nii*'))
        path_composed = dir.joinpath(sequence+'_composed.nii')
        print(path_composed)

        # Read nii files.
        imgs = [sitk.ReadImage(str(file)) for file in nii_files]
        info = [(img.GetSize(), img.GetSpacing()) for img in imgs]

        # Sort images along the z-axis.
        imgs = sort_imgs(imgs)

        # Compose images.
        img_composed = compose_imgs(imgs)

        last_slice = img_composed.GetSize()[2] - 1
        start_z = img_composed.TransformIndexToPhysicalPoint([0, 0, 0])[2]
        end_z = img_composed.TransformIndexToPhysicalPoint([0, 0, last_slice])[2]
        #print('start ', start_z)
        #print('end ', end_z)
        #img_composed = compose_imgs(imgs)
        # Write composed image to nii file.
        sitk.WriteImage(img_composed, str(path_composed))
        print(f'Composed image size {img_composed.GetSize()}')
    return


if __name__ == '__main__':
    main()