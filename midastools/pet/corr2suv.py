import numpy as np
import pydicom
import sys
import argparse
import SimpleITK as sitk

def conv_time(time_str):
    return (float(time_str[:2]) * 3600 + float(time_str[2:4]) * 60 + float(time_str[4:13]))

class Pet:

    def load_pet_param(self):
        ds = pydicom.dcmread(self.dcm_pet_names[0])
        self.total_dose = ds.RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose
        self.start_time = ds.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartTime
        self.half_life = ds.RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife
        self.acq_time = ds.AcquisitionTime
        self.weight = ds.PatientWeight
        self.time_diff = conv_time(self.acq_time) - conv_time(self.start_time)
        self.act_dose = self.total_dose * 0.5 ** (self.time_diff / self.half_life)
        self.suv_factor = 1000 * self.weight / self.act_dose

    def get_pet_image_suv(self):
        return self.image_suv

    def get_pet_image(self):
        return self.image_pet

    def calc_suv_image(self):
        self.image_suv = self.image_pet*self.suv_factor
        return self.image_suv

    def load_dcm_files(self, dcm_files):
        """
        Use explicitly given dicom-filepaths to load the pet image
        and to extract pet dicom tags.
        :param dcm_files: list with dicom-filepaths
        :return:
        """
        self.dcm_pet_names = dcm_files
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(self.dcm_pet_names)
        self.image_pet = reader.Execute()
        self.load_pet_param()

    def load_nii(self, nii_path, dcm_header_path):
        """
        Use nii file and single dicom header to load the image data
        and to extract pet dicom tags.
        :param nii_path: path to nii file with pet (corr) image data
        :param dcm_header_path:  single dicom file with
        :return:
        """
        self.dcm_pet_names = [dcm_header_path]
        reader = sitk.ImageFileReader()
        reader.SetImageIO('NiftiImageIO')
        reader.SetFileName(nii_path)
        self.image_pet = reader.Execute()
        self.load_pet_param()

    def load_dcm_dir(self, dcm_dir, dcm_series_id):
        """
        Use dicom directory / series id to load the image data and
        to extract pet dicom tags.
        :param dcm_dir: dicom directory
        :param dcm_series_id: series id
        :return:
        """
        reader = sitk.ImageSeriesReader()
        # Reading PET DICOM dir
        if not dcm_series_id:
            self.dcm_pet_names = reader.GetGDCMSeriesFileNames(dcm_dir)
        else:
            self.dcm_pet_names = reader.GetGDCMSeriesFileNames(dcm_dir, dcm_series_id)
        reader.SetFileNames(self.dcm_pet_names)
        self.image_pet = reader.Execute()
        self.load_pet_param()

    def __init__(self, dcm_dir='', dcm_series_id='',
                 nii_path='', dcm_header_path=''):

        # pet parameters
        self.total_dose = -1
        self.start_time = -1
        self.half_life = -1
        self.acq_time = -1
        self.weight = -1
        self.time_diff = -1
        self.act_dose = -1
        self.suv_factor = -1

        self.dcm_pet_names = []
        self.image_pet = []
        self.image_suv = []

        if dcm_dir:
            self.load_dcm_dir(dcm_dir, dcm_series_id)

        if nii_path and dcm_header_path:
            self.load_nii(nii_path, dcm_header_path)


def main():
    print('Convert PET corr. to PET SUV')
    parser = argparse.ArgumentParser()
    parser.add_argument('--nii', help='pet image .nii file', required=True)
    parser.add_argument('--header', help='single .dcm file with pet dicom tags', required=True)
    parser.add_argument('--out', help='.nii output file', required=True)
    parser.add_argument('--dtype', help='output file dtype', default='float32', choices=['float32', 'float16'])

    args = parser.parse_args()
    nii_file = args.nii
    dcm_header = args.header
    out_file = args.out

    if args.dtype == 'float32':
       args.dtype = np.float32
    elif args.dtype == 'float16':
       args.dtype = np.float16

    if nii_file and dcm_header and out_file:
        img = sitk.ReadImage(nii_file)
        print('size', img.GetSize())
        print(nii_file, dcm_header, out_file)
        pet_obj = Pet(nii_path=nii_file, dcm_header_path=dcm_header)
        image_pet_suv = pet_obj.calc_suv_image().astype(args.dtype)
        sitk.WriteImage(image_pet_suv, out_file)

if __name__ == '__main__':
    main()
