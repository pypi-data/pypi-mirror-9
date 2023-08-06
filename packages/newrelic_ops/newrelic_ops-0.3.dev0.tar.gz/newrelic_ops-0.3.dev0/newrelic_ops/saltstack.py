import subprocess
import urllib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install(sys_update=True, daemon_start=False, nix_shell='/bin/bash'):
    info = {
        'sys_update': '-U' if sys_update else '',
        'daemon_start': '-X' if not daemon_start else '',
        'nix_shell': nix_shell,
        'bootstrap_url': 'https://bootstrap.saltstack.com',
    }
    try:
        import salt.config
        logger.info("saltstack is already installed!")
    except:
        subprocess.call([info.get('nix_shell'),
                         urllib.urlretrieve(info.get('bootstrap_url'))[0],
                         info.get('sys_update'), info.get('daemon_start')])


if __name__ == '__main__':
    install()
