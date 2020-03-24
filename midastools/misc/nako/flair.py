import tempfile
import re
import shutil
from pathlib import Path

import dicom2nifti
from zipfile import ZipFile

def test(zip_f):
    """ Converts zipped dicom directory (with one series) into nii file.
        Nifti file is name <sequence_name>_<subject_id>.nii.gz

    Arguments:
        zip_f {str} -- Path to zip file (Path obj./string)  

    Returns:
        str -- subject_id
    """

    seq_name = 'FLAIR_2D_TRA' 
    work_dir = Path('/mnt/data/rawdata/NAKO_195/NAKO-195_MRT-Dateien/FLAIR_2D_TRA')
    out_dir = Path('/home/raheppt1')

    for f in work_dir.glob('*.zip'):
        print(f)
        break
    zip_f = str(zip_f)

    # Get subject id from filename.
    m = re.match('.*([0-9]{6}).*', f.name)
    subj_id = m.group(1)
    # Create tmp directory and unzip dicom files into tmp.
    tmp = tempfile.TemporaryDirectory()
    with ZipFile(str(f), 'r') as zip_f:
        zip_f.extractall(tmp.name)
    # Convert dicom files to nifti.
    dicom2nifti.convert_directory(tmp.name, tmp.name)
    # Move and rename nii file.
    nii_file_src = next(Path(tmp.name).glob('*.nii.gz'))
    nii_file_dest = out_dir.joinpath(f'{seq_name}_{subj_id}.nii.gz')
    shutil.move(str(nii_file_src), str(nii_file_dest))
    # Cleanup tmp
    tmp.cleanup()

    return f

