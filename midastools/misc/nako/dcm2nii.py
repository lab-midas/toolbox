import os
import re
import pydicom as dicom
from pathlib import Path
import sys
import dicom2nifti
import dicom2nifti.settings
import SimpleITK as sitk
import shutil
import argparse
from zipfile import ZipFile


def unzip(zip_file, output_dir):
    """ Unzips a zip file to a temporary dicom directory in the outputdir
    
    Arguments:
        zip_file {str/Path} -- zip file to extract
        output_dir {str/Path} -- destination
    """

    with ZipFile(str(zip_file), 'r') as zipObj:
        zipObj.extractall(str(output_dir))


def get_dcm_names(dicom_dir):
    """ Returns the path/names of all DICOM files in a folder as strings
    
    Arguments:
        dicom_dir {str/Path} -- dicom directory
    
    Returns:
        list with dicom files
    """

    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(str(dicom_dir))
    
    return dicom_names
    

def conv_dicom_nii(dicom_dir):
    """ Replaces DICOM files in a specified directory by .nii.gz files; 
        initial DICOM files are deleted.
    
    Arguments:
        dicom_dir {str/Path} -- dicom directory
    """
    dicom2nifti.settings.disable_validate_slice_increment()
    dicom2nifti.convert_directory(str(dicom_dir), str(dicom_dir))
    dicom_files = get_dcm_names(dicom_dir)
    for f in dicom_files:
        os.remove(f)
             

def sort_dcm_dir(dicom_dir):
    """ Separates dixon contrasts stored into four different folders named 
        'fat','water','in','opp', deletes original folder.
    
    Arguments:
        dicom_dir {str/Path} -- directory with dcm files
    """ 

    dicom_dir = Path(str(dicom_dir))
    dicom_files = get_dcm_names(dicom_dir)
    contrasts = ['fat','water','in','opp']
    
    for contrast in contrasts:
        dicom_dir.parent.joinpath(contrast).mkdir()
                
    # get echo times    
    echo_times = set({})
    for f in dicom_files:
        new_echo_time = dicom.read_file(f).EchoTime
        echo_times.add(new_echo_time)
    
    # copy files to different folders
    for f in dicom_files:
        dicomfile = dicom.read_file(f)
        #print(str(file))
        if 'DIXF' in dicomfile[0x00511019].value: # fat
            shutil.copy(f, str(dicom_dir.parent.joinpath(contrasts[0])))                     
        elif 'DIXW'in dicomfile[0x00511019].value: # water
            shutil.copy(f, str(dicom_dir.parent.joinpath(contrasts[1])))                   
        elif dicomfile.EchoTime == max(echo_times):  # in
            shutil.copy(f, str(dicom_dir.parent.joinpath(contrasts[2])))                     
        else: # op
            shutil.copy(f, str(dicom_dir.parent.joinpath(contrasts[3])))
            
    shutil.rmtree(dicom_dir)   


def dcm2nii_zipped(zip_dir, output_dir, 
                   add_id=False,
                   verbose=False):
    """ Converts zipped NAKO DICOM data stored in a sequence folder 
        (e.g.'/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W') 
        to .nii files in a defined output folder 
        (such as '/mnt/data/rawdata/NAKO_195_nii/NAKO-195_MRT-Dateien/3D_GRE_TRA_W')
    
    Arguments:
        zip_dir {str/Path} -- directory with zipped dicom dirs
        output_dir {str/Path} -- output directory for nifti files
        add_id {bool} -- add subject id (parsed from folder name) as praefix
    """

    zip_dir = Path(str(zip_dir))
    output_dir = Path(str(output_dir))

    # unzip all zip files to output_dir
    for f in zip_dir.glob('*.zip'):
        if verbose:
            print('unzipping: ', f)
        unzip(f, output_dir)

    # then convert dicoms to nii
    for folder in output_dir.glob('*'):
        if verbose:
            print('converting: ', folder)
        work_dir = next(folder.glob('*'))
        conv_dicom_nii(work_dir)
        for path in work_dir.glob('*.nii.gz' ):
            # add subject id (parsed from directory name) as file praefix
            subj_id = re.match('.*([0-9]{6}).*', folder.name).group(1) 
            subj_id = (subj_id  + '_') if add_id else ''
            shutil.move(path, folder.joinpath(f'{subj_id}{path.name}'))
        shutil.rmtree(work_dir)


def dcm2nii_zipped_dixon(zip_dir, output_dir, 
                         add_id=False,
                         verbose=False):
    """ Converts zipped NAKO DICOM data stored in a sequence folder 
        (e.g.'/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W_COMPOSED') 
        to .nii files in a defined output folder 
        (such as '/mnt/data/rawdata/NAKO_195_nii/NAKO-195_MRT-Dateien/3D_GRE_TRA_W_COMPOSED').
    
    Arguments:
        zip_dir {str/Path} -- directory with zipped dicom dirs
        output_dir {str/Path} -- output directory for nifti files
        add_id {bool} -- add subject id (parsed from folder name) as praefix
    """

    zip_dir = Path(str(zip_dir)) 
    output_dir = Path(str(output_dir))
    
    # unzip all zip files to output_dir
    for f in zip_dir.glob('*.zip'):
        if verbose:
            print('unzipping: ', f)
        unzip(f, output_dir)   
   
    contrasts = ['fat','water','in','opp']
            
    for folder in output_dir.glob('*'):
        if verbose:
            print('converting: ', folder)

        sort_dcm_dir(next(folder.glob('*')))
        
        for contrast in contrasts:
            dixon_dir = folder.joinpath(contrast)
            conv_dicom_nii(dixon_dir)
            nii_name = next(dixon_dir.glob('*.nii.gz' ))
            # add subject id (parsed from directory name) as file praefix
            subj_id = re.match('.*([0-9]{6}).*', folder.name).group(1)
            subj_id = (subj_id  + '_') if add_id else ''
            shutil.move(nii_name, dixon_dir.parent.joinpath(f'{subj_id}{contrast}.nii.gz') )
            shutil.rmtree(dixon_dir) 


if __name__ == '__main__':
    """
    python dcm2nii_NAKO_wb_Dixon_zipped.py '/path/to/zip_dir' '/path/to/output_dir' (--dixon) (-v)
    """
    parser = argparse.ArgumentParser(description='Convert dicom directories into nifti files.')
    parser.add_argument('zip_dir', help='Path to directory with zipped files.')
    parser.add_argument('out_dir', help='Output directory to store niftis.')
    parser.add_argument('--dixon', action='store_true',
                        help='Dicom directories includes different dixon contrasts.')
    parser.add_argument('--id', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
   
    if args.dixon:
        dcm2nii_zipped_dixon(args.zip_dir, args.out_dir, args.id, args.verbose)
    else:
        dcm2nii_zipped(args.zip_dir, args.out_dir, args.id, args.verbose)
