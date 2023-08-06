'''
Created on Feb 12, 2013

@author: Christian M Brodbeck
'''
from itertools import izip
import os

from mne.label import _get_annot_fname
from mne.utils import get_subjects_dir
from nibabel.freesurfer import read_annot, write_annot


def fix_annot_names(subject, parc, clean_subject=None, clean_parc=None,
                    hemi='both', subjects_dir=None):
    """Fix for Freesurfer's mri_surf2surf corrupting label names in annot files

    Notes
    -----
    Requires nibabel > 1.3.0 for annot file I/O
    """
    # process args
    subjects_dir = get_subjects_dir(subjects_dir)
    if clean_subject is None:
        clean_subject = subject
    if clean_parc is None:
        clean_parc = parc

    fpaths, hemis = _get_annot_fname(None, subject, hemi, parc, subjects_dir)
    clean_fpaths, _ = _get_annot_fname(None, clean_subject, hemi, clean_parc,
                                       subjects_dir)

    for fpath, clean_fpath, hemi in izip(fpaths, clean_fpaths, hemis):
        labels, ctab, names = read_annot(fpath)
        _, _, clean_names = read_annot(clean_fpath)
        if all(n == nc for n, nc in izip(names, clean_names)):
            continue

        if len(clean_names) != len(names):
            err = ("Different names in %s annot files: %s vs. "
                   "%s" % (hemi, str(names), str(clean_names)))
            raise ValueError(err)

        for clean_name, name in izip(clean_names, names):
            if not name.startswith(clean_name):
                err = "%s does not start with %s" % (str(name), clean_name)
                raise ValueError(err)

        write_annot(fpath, labels, ctab, clean_names)


def is_fake_mri(mri_dir):
    """Check whether a directory is a fake MRI subject directory

    Parameters
    ----------
    mri_dir : str(path)
        Path to a directory.

    Returns
    -------
    True is `mri_dir` is a fake MRI directory.

    """
    items = os.listdir(mri_dir)
    # need to contain:
    nc = [c for c in ['bem', 'surf'] if c not in items]
    # does not contain:
    c = [c for c in ['mri', 'src', 'stats'] if c in items]
    if c or nc:
        return False
    else:
        return True
