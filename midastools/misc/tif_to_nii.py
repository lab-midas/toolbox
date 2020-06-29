from tifffile import imread # requires the package 'imagecodecs'
import SimpleITK as sitk
import sys



def load_dcm_data(dirpath):
    """ Reads dicom directory into sitk image object.
    Args:
        dirpath: dicom directory path
    Returns: sitk image
    """
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dirpath)
    reader.SetFileNames(dicom_names)
    return reader.Execute()



def main(tif_path, dcm_path, out_path):

    """ reads .tif (Mevis labelmap format) file and exports the respective .nii.gz file
    requires the original DICOM data set
    tif_path: e.g. /path/labelmask.tif
    dcm_path: e.g. /path/dcm/
    out_path: e.g. /path/labelmask.nii.gz
     """
    labelmask = imread(tif_path)
    dcm_img = load_dcm_data(dcm_path)
    mask_img = sitk.GetImageFromArray(labelmask)
    mask_img.CopyInformation(dcm_img)
    sitk.WriteImage(mask_img, out_path)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])