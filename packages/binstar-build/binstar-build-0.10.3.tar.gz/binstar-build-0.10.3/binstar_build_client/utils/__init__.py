

import os
def get_conda_root_prefix():
    conda_ext = 'conda.exe' if os.name == 'nt' else 'conda'

    for entry in os.environ.get('PATH').split(os.pathsep):
        if conda_ext in os.listdir(entry):
            conda_exe_path = os.path.realpath(os.path.join(entry, 'conda'))
            bin_dir = os.path.dirname(conda_exe_path)
            return os.path.dirname(bin_dir)

