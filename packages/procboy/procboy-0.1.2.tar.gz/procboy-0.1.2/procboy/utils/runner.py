#!/usr/bin/env python
import argparse
from procboy.boy import *

def manager(e=None, f=None):
    processes = []
    CHILDREN = []
    loop = asyncio.get_event_loop()

    procfile = get_procfile(f=f)
    procenv = get_procfile_env(e=e)

    print("Setting environment variables from: {0}:".format(procenv))
    inip = InifilePrepend('./{}'.format(procenv))
    inip.run()
    ini = Inifile('./{}'.format(procenv))
    # TODO: default environment variables
    os.environ.setdefault('PYTHONUNBUFFERED', 'True')
    ini.run()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), functools.partial(ask_exit, signame))
    try:
        pfs = ProcfileStartup('./{}'.format(procfile))
        pfs.run()

        pf = Procfile('./{}'.format(procfile))
        if not hasattr(pf, 'commands'):
            return
        max_name_len = max([len(name) for name,command in pf.commands.items()])
        for name,command in pf.commands.items():
            print("Starting {}: {}".format(name, ' '.join(command)))
            data = dict(name=name,
                    color=get_random_color(),
                    max_name_len=max_name_len,)
            instance = get_protocol(data)
            generator = loop.subprocess_exec(instance, *command)
            processes.append([name, generator])
            loop.run_until_complete(generator)
        loop.run_forever()
    finally:
        psp = PsParser()
        for pid in PIDS:
            proc = psp.get_pid(pid)
            if proc:
                CHILDREN += proc.child_pids()
        for name, proc in processes:
            print("Closing",name)
            result = proc.close()
        if loop.is_running():
            loop.stop()
        loop.close()
        """ ensure no zombie processes left due eg. remote pdb sessions """
        for pid in PIDS + CHILDREN:
            try:
                os.killpg(pid, signal.SIGTERM)
            except Exception as e:
                pass
            try:
                os.kill(pid, signal.SIGQUIT)
            except Exception as e:
                pass

        pfe = ProcfileEnd('./{}'.format(procfile))
        pfe.run()

def main(e=None, f=None):
    manager(e=e, f=f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='procboy')
    parser.add_argument('-e', help='procenv', required=False)
    parser.add_argument('-f', help='procfile', required=False)
    args = parser.parse_args()
    main(e=args.e if args else None,
            f=args.f if args else None,)
