# -*- coding: utf-8 -*-

'''
Invoke cli when package is invoked as a module.
-----------------------------------------------
python -m wanderer
'''


if __name__ == '__main__':
    from .cli import main
    main()
