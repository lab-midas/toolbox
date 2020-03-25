from pathlib import Path
import shutil
import subprocess


def add_to_project(path_to_nii,
                   project='INBOX',
                   subject_id='dummy_dummy_0000',
                   date='20200101',
                   study_id='studydummy'):
    """Add nifti file to nora project.

    First, the nifti has to be copied into the study directory: 
    /mnt/share/nora/imgdata/<project>/<subject_id>/<study_id>_<date>/<nifti filename>
    Afterwards, it can be added using the nora command line tool.
    
    Args:
        path_to_nii (str/Path): .nii/.nii.gz file 
        project (str, optional): nora project name. Defaults to 'INBOX'.
        subject_id (str, optional): name_givename_patientid. Defaults to 'dummy_dummy_0000'.
        date (str, optional): study date (YYYYMMDD). Defaults to '20200101'.
        study_id (str, optional): study id. Defaults to 'studydummy'.
    """

    src_path = Path(path_to_nii)
    prj_path = Path(f'/mnt/share/nora/imgdata/{project}/')
    study_path = prj_path.joinpath(subject_id)
    study_path.mkdir(exist_ok=True)
    study_path = study_path.joinpath(f'{study_id}_{date}')
    study_path.mkdir(exist_ok=True)
    dest_path = study_path.joinpath(src_path.name)

    # Copy nii file to nora imgdata directory.
    shutil.copy(src_path, dest_path)

    # Add nii file to nora project.
    out = subprocess.Popen(['nora', '-p', project, '--add', dest_path],
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    print(stdout)
