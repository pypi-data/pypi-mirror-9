#!/usr/bin/env python
from procboy.boy import *

def manager():
    processes = []
    CHILDREN = []
    loop = asyncio.get_event_loop()
    inip = InifilePrepend('./.env')
    inip.run()
    ini = Inifile('./.env')
    print("Setting environment variables from: {0}:".format('.env'))
    # TODO: default environment variables
    os.environ.setdefault('PYTHONUNBUFFERED', 'True')
    ini.run()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), functools.partial(ask_exit, signame))
    try:
        pfs = ProcfileStartup('./Procfile')
        for name,command in pfs.commands.items():
            subprocess.call(command)

        pf = Procfile('./Procfile')
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

        pfe = ProcfileEnd('./Procfile')
        for name,command in pfe.commands.items():
            subprocess.call(command)

def main():
    manager()

if __name__ == '__main__':
    main()
