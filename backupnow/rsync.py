import subprocess
import re
import sys

try:
    try:
        import tkMessageBox as messagebox
    except ModuleNotFoundError:
        # Python 3
        try:
            from tkinter import messagebox
        except ModuleNotFoundError:
            raise Exception("The rsync module requires the python3-tk"
                            " package to be installed such as via:\n"
                            "  sudo apt-get install python3-tk")
            exit(1)
except NameError as ex:
    if "ModuleNotFoundError" in str(ex):
        # There is no ModuleNotFoundError in Python 2, so trying to
        # use it will raise a NameError.
        raise Exception("You are using Python 2"
                        " but the rsync module requires Python 3.")
    else:
        raise ex


class RSync:
    _TOTAL_SIZE_FLAG = 'total size is '
    
    def __init__(self):
        self._reset()
    
    def _reset(self):
        self.progress = 0.0  # The progress from 0.0 to 1.0
        self.totalSize = sys.float_info.max

    def changed(self, progress, message=None, error=None):
        print("Your program should overload this function."
              " It accepts a value from 0.0 to 1.0, and optionally,"
              " a message and an error:\n"
              "changed({}, message=\"{}\", error=\"{}\")"
              "".format(progress, message, error))
    
    def run(self, src, dst, exclude_from=None, include_from=None,
            exclude=None, include=None):
        '''
        dst -- This is the backup destination. The folder name of src
               (but not the full path) will be added under dst.
        '''

        print('Dry run:')

        cmd = 'rsync -az --stats --dry-run ' + src + ' ' + dst

        proc = subprocess.Popen(cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        output, err = proc.communicate()
        # if output is not None:
        #     print("dry_run output: '''{}'''"
        #           "".format(output.decode('utf-8')))
        if err is not None:
            print("dry_run error: '''{}'''"
                  "".format(err.decode('utf-8')))

        mn = re.findall(r'Number of files: (\d+)', output.decode('utf-8'))
        total_files = int(mn[0])

        print('Number of files: ' + str(total_files))

        print('Real rsync:')

        cmd = 'rsync -avz  --progress ' + src + ' ' + dst
        proc = subprocess.Popen(cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._reset()
        while True:
            output = proc.stdout.readline().decode('utf-8')
            error = proc.stderr.readline().decode('utf-8')
            sizeFlagI = -1
            
            if (error is not None) and (len(error) > 0):
                if 'skipping non-regular file' in error:
                    pass
                else:
                    self.changed(
                        None,
                        error="{}".format(error.strip())
                    )
                    return False

            if output is None:
                return False
            
            sizeFlagI = output.find(RSync._TOTAL_SIZE_FLAG)
            if sizeFlagI >= 0:
                sizeStartI = sizeFlagI + len(RSync._TOTAL_SIZE_FLAG)
                sizeEndI = output.find(" ", sizeStartI)
                if sizeEndI >= 0:
                    sizeStr = output[sizeStartI:sizeEndI].strip()
                    sizeStr = sizeStr.replace(",", "")
                    self.totalSize = float(int(sizeStr))
                    print("self.totalSize: {}"
                          "".format(self.totalSize))
            elif output.startswith("sent"):
                continue
            elif 'to-check' in output:
                m = re.findall(r'to-check=(\d+)/(\d+)', output)
                # progress = (100 * (int(m[0][1]) - int(m[0][0]))) / total_files
                self.progress = ((int(m[0][1]) - int(m[0][0]))) / total_files
                self.changed(progress)
                # sys.stdout.write('\rDone: ' + str(self.progress) + '%')
                # sys.stdout.flush()
                if int(m[0][0]) == 0:
                    break
            elif 'sending incremental file list' in output:
                self.progress = 0.0
            elif len(output.strip()) == 0:
                code = proc.returncode
                if proc.returncode is None:
                    code = proc.poll()
                if code is not None:
                    if code == 0:
                        # ^ 0 is good
                        return True
                    else:
                        return False
                else:
                    print("There was no return code but output was blank.")
                    break
                # if None, the process hasn't terminated yet.
            else:
                print("unknown output: '''{}'''".format(output))            
            
        return True
