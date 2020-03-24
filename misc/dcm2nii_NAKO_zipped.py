import os
import pydicom as dicom
from pathlib import Path
import sys
import dicom2nifti
import SimpleITK as sitk
import shutil
import glob
from zipfile import ZipFile


def get_zip_names(zip_dir):
    
# lists the path/names of all zip files in a sequence folder (e.g. ''/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W')
    zip_dir = Path(zip_dir)
    file_names = list( zip_dir.glob('*.zip') ) 
    file_names = [str(file) for file in file_names]

    return file_names

def unzip(zip_file, output_dir):

# unzips a zip file to a temporary dicom directory in the outputdir

    with ZipFile(zip_file, 'r') as zipObj:
        zipObj.extractall(output_dir)
        
def get_dcm_names(dicom_dir):
    
# returns the path/names of all DICOM files in a folder as strings

    dicom_dir = Path(dicom_dir)
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(str(dicom_dir))
    
    return dicom_names
    

def conv_dicom_nii(dicom_dir):
# replaces DICOM files in a specified directory by .nii.gz files; initial DICOM files are deleted

    dicom_dir = Path(dicom_dir) #'/mnt/share/nora/imgdata/UKB3001ABDS/')  
    dicom2nifti.convert_directory(str(dicom_dir), str(dicom_dir))
    dicom_files = get_dcm_names(str(dicom_dir))
    for file in dicom_files:
        os.remove(file)
    return
             

def main(zip_dir, output_dir):
    
# converts zipped NAKO DICOM data stored in a sequence folder (e.g.'/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W') to .nii files in a defined output folder (such as '/mnt/data/rawdata/NAKO_195_nii/NAKO-195_MRT-Dateien/3D_GRE_TRA_W')
# python dcm2nii_NAKO_zipped.py '/path/to/zip_dir' '/path/to/output_dir'

   
    zip_dir = Path(zip_dir) 
    output_dir = Path(output_dir) 
                
    # get DICOM file names
    zip_files = get_zip_names( str(zip_dir) )       
  
     # first unzip all files to the output directory
    
    for file in zip_files:
        unzip(file, output_dir)
                 
    # then convert dicoms to nii
    output_folders = list( output_dir.glob('*') )  
    
    for folder in output_folders:
        dcm_out_dir = list( folder.glob('*') ) 
        conv_dicom_nii( str(dcm_out_dir[0]))
        nii_path = list(dcm_out_dir[0].glob('*.nii.gz' ) )
        for path in nii_path:
            shutil.move(path, folder.joinpath(path.name))
        shutil.rmtree(dcm_out_dir[0])
                    
    return         
                                  

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])