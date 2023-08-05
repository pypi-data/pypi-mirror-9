from . import Sh

if __name__ == '__main__':
    Sh('ls') | ['grep', 'blt'] | 'wc "-l"' > 'tango'
    Sh('ls') > 'polka'
    print (Sh('cat', '*py') | 'wc').returncode

    Sh('wc').stdin('polka').returncode

    s = Sh('ls') | ['grep', 'blt'] | 'wc "-l"'
    print s, s.returncode