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
    
# returns the path/names of all zip files in a sequence folder as strings (e.g. /mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W_COMPOSED')
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
# replaces DICOM files in a specified directory by .nii.gz files; initial DICOM files are deleted (for composed Dixon files DICOM files have to be separated first, see sort_dcm_dir)

    dicom_dir = Path(dicom_dir) #'/mnt/share/nora/imgdata/UKB3001ABDS/')  
    dicom2nifti.convert_directory(str(dicom_dir), str(dicom_dir))
    dicom_files = get_dcm_names(str(dicom_dir))
    for file in dicom_files:
        os.remove(file)
    return



def sort_dcm_dir(dicom_dir):    
# separates dixon contrasts stored into four different folders named 'fat','water','in','opp', deletes original folder
    
    dicom_dir = Path(dicom_dir)
    dicom_files = get_dcm_names( str(dicom_dir) )
    contrasts = ['fat','water','in','opp']
    
    for contrast in contrasts:
        os.mkdir( dicom_dir.parent.joinpath(contrast) )
                
    # get echo times    
    echo_times = set({})
    for file in dicom_files:
        new_echo_time = dicom.read_file(file).EchoTime
        echo_times.add(new_echo_time)
    
    # copy files to different folders
        
    for file in dicom_files:
        dicomfile = dicom.read_file(file)
        #print(str(file))
        if 'DIXF' in dicomfile[0x00511019].value: # fat
            shutil.copy(file, str( dicom_dir.parent.joinpath(contrasts[0]) ))                     
        elif 'DIXW'in dicomfile[0x00511019].value: # water
            shutil.copy(file, str( dicom_dir.parent.joinpath(contrasts[1]) ))                   
        elif dicomfile.EchoTime == max(echo_times):  # in
            shutil.copy(file, str( dicom_dir.parent.joinpath(contrasts[2]) ))                     
        else: # op
            shutil.copy(file, str( dicom_dir.parent.joinpath(contrasts[3]) ))
            
    shutil.rmtree(dicom_dir)   

def main(zip_dir, output_dir):
# converts zipped NAKO DICOM data stored in a sequence folder (e.g.'/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W_COMPOSED') to .nii files in a defined output folder (such as '/mnt/data/rawdata/NAKO_195_nii/NAKO-195_MRT-Dateien/3D_GRE_TRA_W_COMPOSED')
# python dcm2nii_NAKO_wb_Dixon_zipped.py '/path/to/zip_dir' '/path/to/output_dir'


    zip_dir = Path(zip_dir) 
    output_dir = Path(output_dir)
    
    # get zip file path/names as string
    zip_files = get_zip_names(zip_dir)
    
    for file in zip_files:
        unzip(file, output_dir)   
    
    output_folders = list( output_dir.glob('*') )
    
    contrasts = ['fat','water','in','opp']
            
    for folder in output_folders:
        dcm_out_dir = list( folder.glob('*') )
        sort_dcm_dir(dcm_out_dir[0])
        
        for contrast in contrasts:
            Dixon_dir = folder.joinpath(contrast)
            conv_dicom_nii( str(Dixon_dir) )
            nii_name = list(Dixon_dir.glob('*.nii.gz' ) )
            shutil.move(nii_name[0], Dixon_dir.parent.joinpath(contrast + '.nii.gz') )
            shutil.rmtree(Dixon_dir) 
 
    return                          
                                  

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])