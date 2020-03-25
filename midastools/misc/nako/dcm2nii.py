# -*- coding: utf-8 -*-
"""Example Google style docstrings.

Dicom to nifti conversion for NAKO zipped imaging studies.

Example:
    Example usage::
        $ python dcm2nii /srcdir /destdir :dixon -v 

Todo:
    * ...

"""

import multiprocessing
import os
import sys
import time
import re
import tempfile
import pydicom as dicom
from pathlib import Path
import sys
import dicom2nifti
import dicom2nifti.settings
import SimpleITK as sitk
import shutil
import argparse
from zipfile import ZipFile
from joblib import Parallel, delayed


def unzip(zip_file, output_dir):
    """ Unzips a zip file to a temporary dicom directory in the outputdir
    
    Args:
        zip_file (str/Path): zip file to extract
        output_dir (str/Path): destination
    """

    with ZipFile(str(zip_file), 'r') as zipObj:
        zipObj.extractall(str(output_dir))


def get_dcm_names(dicom_dir):
    """ Returns the path/names of all DICOM files in a folder as strings
    
    Args:
        dicom_dir (str/Path) : dicom directory
    
    Returns:
        list with dicom files
    """

    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(str(dicom_dir))
    
    return dicom_names
    

def conv_dicom_nii(dicom_dir, nifti_dir):
    """ Convert dicom directory to nifti file.

    Replaces DICOM files in a specified directory by .nii.gz files; 
    initial DICOM files are deleted.
    
    Args:
        dicom_dir (str/Path): dicom directory
    """
    dicom2nifti.settings.disable_validate_slice_increment()
    dicom2nifti.convert_directory(str(dicom_dir), str(nifti_dir))
    dicom_files = get_dcm_names(dicom_dir)
    for f in dicom_files:
        os.remove(f)
             

def sort_dcm_dir(dicom_dir):
    """ Seperate dixon contrasts.
    
    Separates dixon contrasts stored into four different folders named 
    'fat','water','in','opp', deletes original folder.
    
    Args:
        dicom_dir (str/Path): directory with dcm files
    """ 

    dicom_dir = Path(dicom_dir)
    dicom_files = get_dcm_names(dicom_dir)
    contrasts = ['fat','water','in','opp']
    
    for contrast in contrasts:
        dicom_dir.parent.joinpath(contrast).mkdir()
                
    # get echo times    
    echo_times = set(())
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


def dcm2nii_zipped(zip_file, output_dir, 
                   add_id=False,
                   single_dir=False,
                   verbose=False):
    """ Covert single sequence zip to nifti.
    
    Converts zipped NAKO DICOM data stored in a sequence folder 
    (e.g.'/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W') 
    to .nii files in a defined output folder 
    (such as '/mnt/data/rawdata/NAKO_195_nii/NAKO-195_MRT-Dateien/3D_GRE_TRA_W')
    
    Args:
        zip_file (str/Path): zip file to extract
        output_dir (str/Path): output directory for nifti files
        add_id (bool): add subject id (parsed from zip filename) as praefix
        single_dir (bool): save nifti files in a single directory (no subdirs)
        verbose (bool): activate prints
    """

    f = Path(zip_file)
    output_dir = Path(output_dir)
        
    # create temp directory
    tmp = tempfile.TemporaryDirectory()
    # get subject id
    subj_id = re.match('.*([0-9](6)).*', f.name).group(1) 

    if verbose:
        print('unzipping: ', f)

    # unzip to temp directory
    try:
        unzip(f, tmp.name)
    except:
        print(f'zip error (subj_id)', file=sys.stderr)
        return

    if verbose:
        print('converting ... ')

    # create folder with subject id
    dest_dir = output_dir.joinpath(subj_id)
    dest_dir.mkdir(exist_ok=True)

    try:
        # convert dicom files in tmpdir to nii file 
        dcm_dir = next(Path(tmp.name).glob('*'))
        dcm_dir = next(dcm_dir.glob('*'))
        conv_dicom_nii(dcm_dir, dest_dir)

        # rename nifti file
        nii_path = next(dest_dir.glob('*.nii.gz'))

        if single_dir:
            # use id praefix, if all files are saved in one directory
            subj_str = (subj_id + '_')
            shutil.move(nii_path, output_dir.joinpath(f'(subj_str)(nii_path.name)'))
            shutil.rmtree(dest_dir)
        else:
            # if add_id = True use subj_id as filename praefix
            subj_str = (subj_id  + '_') if add_id else ''
            shutil.move(nii_path, dest_dir.joinpath(f'(subj_str)(nii_path.name)'))

    except:
        print(f'conversion error (subj_id)', file=sys.stderr)
        shutil.rmtree(dest_dir)

    finally:
        # delete tmp directory
        tmp.cleanup()


def dcm2nii_zipped_dixon(zip_file, output_dir,
                         add_id=False,
                         single_dir=False,
                         verbose=False):
    """ Covert dixon sequence zip (with four contrasts) to nifti.

    Converts zipped NAKO DICOM data stored in a sequence folder 
    (e.g.'/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/3D_GRE_TRA_W_COMPOSED') 
    to .nii files in a defined output folder 
    (such as '/mnt/data/rawdata/NAKO_195_nii/NAKO-195_MRT-Dateien/3D_GRE_TRA_W_COMPOSED').
    
    Args:
        zip_file (str/Path): zip file to extract
        output_dir (str/Path): output directory for nifti files
        add_id (bool): add subject id (parsed from zip filename) as praefix
        single_dir (bool): save nifti files in a single directory (no subdirs)
        verbose (bool): activate prints
    """

    f = Path(zip_file)
    output_dir = Path(output_dir)

    # create temp directory
    tmp = tempfile.TemporaryDirectory()
    # get subject id
    subj_id = re.match('.*([0-9](6)).*', f.name).group(1)
    
    if verbose:
        print('unzipping: ', f)

    # unzip to temp directory
    try:
        unzip(f, tmp.name)  
    except:
        print(f'zip error (subj_id)', file=sys.stderr)
        return
   
    # create folder with subject id, if single_dir = False
    dest_dir = output_dir.joinpath(subj_id)
    dest_dir.mkdir(exist_ok=True)

    contrasts = ['fat','water','in','opp']
            
    if verbose:
        print('converting ...')

    try:
        # sort dcm directory
        dcm_dir = next(Path(tmp.name).glob('*'))
        sort_dcm_dir(next(dcm_dir.glob('*')))
        
        for contrast in contrasts:
            # create subfolder foreach contrast, if single_dir = False
            contrast_dest_dir = dest_dir.joinpath(contrast)
            contrast_dest_dir.mkdir(exist_ok=True)
            dixon_dir = dcm_dir.joinpath(contrast)
            conv_dicom_nii(dixon_dir, contrast_dest_dir)

            # rename nifti file
            nii_path = next(contrast_dest_dir.glob('*.nii.gz'))
                    
            if single_dir:
                # use id praefix, if all files are saved in one directory
                subj_str = (subj_id + '_')
                shutil.move(nii_path, output_dir.joinpath(f'(subj_str)(contrast).nii.gz'))
            else:
                # if add_id = True use subj_id as filename praefix
                subj_str = (subj_id + '_') if add_id else ''
                shutil.move(nii_path, contrast_dest_dir.joinpath(f'(subj_str)(contrast).nii.gz'))

        if single_dir:
            shutil.rmtree(dest_dir)

    except:
        print(f'conversion error (subj_id)', file=sys.stderr)
        shutil.rmtree(dest_dir)

    finally:
        # delete tmp directory
        tmp.cleanup()
        return

if __name__ == '__main__':
    """
    python dcm2nii_NAKO_wb_Dixon_zipped.py '/path/to/zip_dir' '/path/to/output_dir' (:dixon) (-v) (:cores)
    """
    num_cores = multiprocessing.cpu_count()

    parser = argparse.ArgumentParser(description='Convert dicom directories into nifti files.')
    parser.add_argument('zip_dir', help='Path to directory with zipped files.')
    parser.add_argument('out_dir', help='Output directory to store niftis.')
    parser.add_argument(':dixon', action='store_true',
                        help='Dicom directories includes different dixon contrasts.')
    parser.add_argument(':id', action='store_true')
    parser.add_argument(':cores', type=int, choices=range(1, num_cores+1))
    parser.add_argument('-v', ':verbose', action='store_true')
    parser.add_argument('-s', ':singledir', action='store_true', help='Store all nifti files in one directory (no sub-dirs).')
    args = parser.parse_args()
   
    zip_dir = Path(args.zip_dir)
    out_dir = Path(args.out_dir)
    
    def process_file(f):
        if args.dixon:
            dcm2nii_zipped_dixon(f, out_dir, args.id,
                                 args.singledir, args.verbose)
        else:
            dcm2nii_zipped(f, out_dir, args.id, 
                            args.singledir, args.verbose)

    # single process version
    #t = time.time()
    #for f in zip_dir.glob('*.zip'):
    #    process_file(f)
    #elapsed_time = time.time() - t

    file_list = list(zip_dir.glob('*.zip'))

    # multiprocessing 
    num_cores = 10
    if args.cores:
        num_cores = args.cores
    print(f'using (num_cores) CPU cores')

    t = time.time()
    results = Parallel(n_jobs=num_cores)(
        delayed(process_file)(f) for f in file_list)
    elapsed_time = time.time() - t

    print(f'elapsed time: (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))')
