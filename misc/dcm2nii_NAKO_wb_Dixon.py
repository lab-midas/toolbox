import os
import pydicom as dicom
from pathlib import Path
import sys
import dicom2nifti
import SimpleITK as sitk
import shutil
import glob


def get_dcm_names(dicom_dir):
    
# lists the path/names of all DICOM files in a folder

    dicom_dir = Path(dicom_dir)
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(str(dicom_dir))
    #dicom_names = list( dicom_dir.glob('*.dcm') )  # may have to be adapted if DICOM files do not end in .dcm
    #dicom_names = [str(file) for file in dicom_names]
    return dicom_names


def conv_dicom_nii(dicom_dir):
# replaces DICOM files in a specified directory by .nii.gz files; initial DICOM files are deleted

    dicom_dir = Path(dicom_dir) #'/mnt/share/nora/imgdata/UKB3001ABDS/')  
    dicom2nifti.convert_directory(str(dicom_dir), str(dicom_dir))
    dicom_files = get_dcm_names(str(dicom_dir))
    for file in dicom_files:
        os.system('rm {a}'.format(a = file))
    return
             

def main(dicom_dir, output_dir):
    
# accesses folder with DICOM files of 4 Dixon contrasts (in, op, fat, water), separates files of contrasts and stores them into different folders as specified and subsequently converts to .nii, can be called form command line as:
# python sort_dcm.py '/path/to/dicom_dir' '/path/to/output_dir'

    #dicom_dir = '/home/ragatis1/Dixon/Dataset1/'
    #output_dir = '/home/ragatis1/Dixon_sorted/Dataset1/'

    dicom_dir = Path(dicom_dir) #'/mnt/share/nora/imgdata/UKB3001ABDS/')
    output_dir = Path(output_dir) #'/home/raheppt1/data_samples/compose/composed.nii')
    
            
    # get DICOM file names
    dicom_files = get_dcm_names( str(dicom_dir) )
        
    # sort DICOM files according to contrast and save in separte folders
    contrasts = ['fat','water','in','opp']
    
    for contrast in contrasts:
        os.mkdir( str(output_dir) + '/' + contrast )
    
    # get echo times
    
    echo_times = set({})
    for file in dicom_files:
        new_echo_time = dicom.read_file(file).EchoTime
        echo_times.add(new_echo_time)
    
    # copy files to different folders
        
    for file in dicom_files:
        dicomfile = dicom.read_file(file)        
        if 'DIXF' in dicomfile[0x00511019].value: # fat
            os.system( 'cp {a} {b}'.format(a = file, b = str(output_dir) + '/' + contrasts[0]))            
        elif 'DIXW'in dicomfile[0x00511019].value: # water
            os.system( 'cp {a} {b}'.format(a = file, b = str(output_dir) + '/' + contrasts[1]))            
        elif dicomfile.EchoTime == max(echo_times):  # in
            os.system( 'cp {a} {b}'.format(a = file, b = str(output_dir) + '/' + contrasts[2]))            
        else: # op
            os.system( 'cp {a} {b}'.format(a = file, b = str(output_dir) + '/' + contrasts[3]))
            
    for contrast in contrasts:
        nii_dir = Path(str(output_dir) + '/' + contrast)
        conv_dicom_nii( str(nii_dir) )
        nii_name = list(nii_dir.glob('*.nii.gz' ) )
        shutil.move(str(nii_name[0]), str(nii_dir.parent) + '/' + contrast + '.nii.gz')
        os.system('rm -r {a}'.format(a = str(nii_dir)))
            
    return                 
                                  

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])