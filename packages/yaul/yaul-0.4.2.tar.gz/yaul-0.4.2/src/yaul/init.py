## Revamped daemon implementation based on python-daemon
#
# Usage #1 - turning a Python function into a service:
#
# serv = InitService('/path/to/lockfile', myfunc, fork=True)
# serv.run_cmdline()
#
# Usage #2 - turning another script into a service:
#
# serv = InitService('/path/to/lockfile', '/path/to/script', prog_name='script_alias')
# serv.run_cmdline()
#
# =======
#
# $ python my_script.py -h
# usage: my_script.py [-h] {start,stop,restart,reload,status}
#
# positional arguments:
#   {start,stop,restart,reload,status}
#                         service action to take
# 
# optional arguments:
#   -h, --help            show this help message and exit


import argparse, contextlib, daemon, os, psutil, subprocess, sys, time

class InitService(object):
    def __init__(self, lockfile,
                 executable, args=[], prog_name=None,
                 verbose=False, fork=False,
                 cwd=None, env=None):
        self.lockfile = lockfile
        self.fork = fork
        self.cwd = cwd
        self.env = env

        self.prog_name = prog_name

        self.executable_str = None
        self.executable_py = None
        if hasattr(executable, '__call__'):
            # If callable, assume you were given a Python function
            self.executable_py = executable
            if self.prog_name:
                raise ValueError("Cannot specify prog_name when running a Python function")
        else:
            self.executable_str = str(executable)

        self.exec_args = args

        self.verbose_output = open(os.devnull, 'w')
        if self.verbose_output:
            if hasattr(verbose, 'write') and hasattr(verbose.write, '__call__'):
                self.verbose_output = verbose
            else:
                self.verbose_output = sys.stdout

    def _pid_from_name(self):
        if self.executable_py:
            return None # Name can't be used here
        name = self.prog_name or self.executable_str
        for proc in psutil.process_iter():
            if proc.cmdline() and proc.cmdline()[0] == name:
                return proc.pid
        return None
                
    @property
    def pid(self):
        returnpid = None
        
        if not os.path.exists(self.lockfile):
            return None
        try:
            with open(self.lockfile) as lock:
                pid = lock.read().strip()
            returnpid = int(pid)
        except Exception as e:
            # Error reading pid
            self.pid = None
            namepid = self._pid_from_name()
            if namepid:
                self.pid = namepid
            return namepid

        if returnpid not in psutil.pids():
            # No such process
            self.pid = None
            namepid = self._pid_from_name()
            self.pid = namepid
            return namepid

        return returnpid

    @pid.setter
    def pid(self, val):
        if not val:
            try:
                os.unlink(self.lockfile)
            except FileNotFoundError as e:
                pass
            finally:
                return
        with open(self.lockfile, 'w') as lock:
            lock.write("%s" % val)
                

    def run_cmdline(self, argv=[],
                    description="pyinit service manager"):
        parser = argparse.ArgumentParser()
        parser.add_argument('action', type=str, help="service action to take",
                            choices=['start', 'stop', 'restart', 'reload', 'status'])
        args = parser.parse_args(argv[1:] or sys.argv[1:])
        
        self.run_action(args.action)

    def run_action(self, action):
        action_map = {
            'start': self._start,
            'stop': self._stop,
            'restart': self._restart,
            'reload': self._reload,
            'status': self._status,
            }
        action_map[action]()
        
        
    def _start(self):
        self.pre_start()
        self.verbose_output.write('Starting service...\n')
        if self.pid:
            print('PID %s exists; process already running (clear %s if this is wrong)\n' % (self.pid, self.lockfile))
            return
        
        context = contextlib.ExitStack()
        if self.fork:
            context = daemon.DaemonContext(files_preserve=[self.verbose_output])
        
        if self.executable_str:
            # Use Popen to run the string command
            self.verbose_output.write("String command: %s\n" % self.executable_str)
            self.verbose_output.write("Run to look like command: %s\n" % self.prog_name)
            cmd = [self.executable_str] + self.exec_args
            executable = None
            if self.prog_name:
                cmd[0] = self.prog_name
                executable = self.executable_str

            proc = subprocess.Popen(cmd, executable=executable)
            self.pid = proc.pid
            self.verbose_output.write('Service started. %s\n' % self.pid)
        else:
            # Use daemon context to run the Python command
            self.verbose_output.write('Running %s(%s).\n' % (self.executable_py, self.exec_args))
            with context:
                print(os.getpid())
                self.pid = os.getpid()
                self.executable_py(*self.exec_args)
        self.post_start()
            
        
    def _stop(self):
        self.pre_stop()
        self.verbose_output.write('Stopping service...\n')
        pid = self.pid
        if not pid:
            self.verbose_output.write('Unknown PID; is the service running?\n')
            return
        proc = psutil.Process(self.pid)
        proc.terminate()
        self.verbose_output.write('Term signal sent.\n')
        self.post_stop()
        
    def _restart(self):
        self.verbose_output.write('Restarting service...\n')
        self._stop()
        time.sleep(1)
        self._start()

    def _reload(self):
        self.verbose_output.write('Reloading service...\n')
        self.reload()

    def _status(self):
        self.verbose_output.write('Status-ing service...\n')
        stat = None
        if self.pid:
            proc = psutil.Process(self.pid)
            stat = proc.status()
        else:
            stat = 'stopped'
        self.verbose_output.write('%s (pid: %s)\n' % (stat, self.pid))
        self.status(stat, self.pid)
        

    # User hooks
    def pre_start(self):
        pass
    def post_start(self):
        pass
    def pre_stop(self):
        pass
    def post_stop(self):
        pass
    def status(self, stmsg, pid):
        pass
    def reload(self):
        pass
