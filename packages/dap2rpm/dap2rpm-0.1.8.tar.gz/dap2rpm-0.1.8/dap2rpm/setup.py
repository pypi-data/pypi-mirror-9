import subprocess

from dap2rpm import exceptions

def _run_or_raise(what):
    error = False

    try:
        proc = subprocess.Popen(what, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        out = proc.communicate()
        if proc.returncode != 0:
            error = out
    except subprocess.CalledProcessError as e:
        error = str(e)

    if error != 0:
        raise exceptions.DAPSetupError('Running rpmdev-setuptree failed (is it installed?): \n'
            + error)

    return out


def setup():
    _run_or_raise(['rpmdev-setuptree'])
    _run_or_raise(['which', 'rpmdev-packager'])
