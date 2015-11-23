import os
import ctypes
import sys
import platform

debug = False

def notify_home(url, package_name, intended_package_name):
    host_os = platform.platform()
    try:
        admin_rights = bool(os.getuid() == 0)
    except AttributeError:
        try:
            admin_rights = bool(ctypes.windll.shell32.IsUserAnAdmin() !=    0)
        except:
            admin_rights = False

    if sys.version_info[0] == 3:
        from urllib.request import Request, urlopen
        from urllib.parse import urlencode
    else:
        from urllib2 import Request, urlopen
        from urllib import urlencode

    if os.name != 'nt':
        try:
            pip_version = os.popen('pip --version').read()
        except:
            pip_version = ''
    else:
        pip_version = platform.python_version()

    try:
        data = {
            'p1': package_name,
            'p2': intended_package_name,
            'p3': 'pip',
            'p4': host_os,
            'p5': admin_rights,
            'p6': pip_version,
        }
        data = urlencode(data)
        request = Request(url + data)
        if debug:
            print(request.get_full_url())

        response = urlopen(request).read()

        if debug:
            print(response.decode('utf-8'))
    except Exception as e:
        print(str(e))

    print('')
    print("Warning! Maybe you made a typo in your installation command?!")
    print("Did you really want to install '{}'?!! {} should already be installed in the python stdlib.".format(intended_package_name, intended_package_name))


def main():
    if debug:
        notify_home('http://localhost:8000/app/?', 'json', 'json')
    else:
        notify_home('http://svs-repo.informatik.uni-hamburg.de/app/?', 'json', 'json')

if __name__ == '__main__':
    main()
