import subprocess


def run_command(command, logfile=None, print_output=False):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if logfile is not None:
        logfile.write('%s\n' % command)
        logfile.write(stdout)
        logfile.write(stderr)
        logfile.flush()

    if print_output:
        print 'command: %s' % command
        if stderr != '':
            print 'stderr: %s' % stderr
        if stdout != '':
            print 'stdout: %s' % stdout

    return str(stdout.rstrip()), str(stderr.rstrip())
