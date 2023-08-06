#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright 2012 Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from res import version, factory_args_parse, DEBUG, do, get_do_params, get_infos, template_dir

import os
import zlib
import codecs
import base64

DEFAULT_TEMPLATE = [
    b'eNqNVlGP2kYQfvevmDiK0kpnG67Ki8+g0uOqoqQQHSTRPS72YK+y7Lq7S4Ci+++ZtYFiAyq8wHpm',
    b'Z75v5psxyZvh5HH28vkJCrsUfS95EwTeoyq3mueFhftO9x6eVUYnBZ+5LJBrBX8zy5mBRNeGclmd',
    b'f8+XjIswVcu+533iKUqDGaxkhhpsgTAoWUpfe8sdfEVtuJJwH3bgF+fg703+rw/eVq1gybYglYWV',
    b'QQrADSy4QMBNiqUFLoEylYIzmSKsuS2qJPsQofeyD6DmlpEvI++STotTL2DW8wCIui3jKFqv1yGr',
    b'QIZK55GonUz0afT4NJ4+BQTU875IgcaAxn9WXBO/+RZYSTBSNidwgq1BaWC5RrJZ5WCuNbdc5ndg',
    b'1MKumUYv48ZqPl/ZRn0OoIjoqQNViEnwB1MYTX34YzAdTe+8b6PZX5MvM/g2eH4ejGejpylMnuFx',
    b'Mh6OZqPJmE5/wmD8Ah9H4+EdIFWHkuCm1A47AeSucpiF3hSxkXyhajCmxJQveEqMZL5iOUKufqCW',
    b'RARK1EtuXO8MQcs8wZfckgTc+YxO6AUB6SGp5UXFhqRAltU/q6OxW6qc3ZbY8y1ubJQa4/fh6BDO',
    b'1QZ2/53dhwpUCraNYS5U+v2haVwIxWwMAhe2ZSlZlhGDGH4rNw8Ny5pntqDnnc6p5RW8BoyAp9SO',
    b'3dVsDcOS6ZzLoBqkGD404rbCOtrtsErawPB/MYZu59rdFIW4COccTU2we99pM3e5AyZ4LmNqmEX9',
    b'cGPJ5kpTrwleuSFpC57B2+FweKkGVy8HmmV8ZVr2E4asxa4Cm2GqdKW3mPaDxGbkVAmlnTBWeDlk',
    b'XDgltwLvb9FEX7yURJVKT1QruPxO7qLnVxZTIFq/rWIoNC56/m4HdKq21+urv5+CqB6D+jBX2fZ0',
    b'JDB19PoNiAkDyZYUnsuMZsvvJxFreRTd/qgyUvRu07Z7V822Earane7bwLvX5v2M/4BUMGN6vpMW',
    b'pWB7Cm+Jg7sTVjoiGpvDA3oluDeFI/b/Pg5yElGaM3AoM4fvEqKqwIRIINPxXNnCb8eg9hwq5t1K',
    b'+EqRXUKe9d47/6BNKDgj9L55vdGnW0p21sNjH2nToIFbStpu9Qn7VJgD+ZAvaY2f9bzdd1pH/nm4',
    b'C177XbirchCVQ5vqRdPGTfNdIybLCX5n8C8p4lpSN1rHVDSDGBzDturiAh/RXclw5fF1OZ7736jQ',
    b'yrU8mafDEH9VwjL6x+D+KtST6yakvKjtq/iSqF4gpAX3mv0Jk+7IWw=='
]


def main():
    parser = factory_args_parse()

    # preparando para iniciar
    nm = parser.parse_args()
    if nm.path is not None:
        process_generator(nm)
    elif nm.version is True:
        process_version()
    else:
        parser.print_help()


def process_version():
    print('''%(description)s
Version: %(version)s
Homepage: %(home)s
   ''' % get_infos())


def read_template(templatefile):
    if templatefile:
        template_path = os.path.join(template_dir, nm.template)
        if os.path.exists(template_path) is True:
            return codecs.open(template_path, 'r', 'utf-8').read()
        else:
            return codecs.open(nm.template, 'r', 'utf-8').read()
    else:
        return zlib.decompress(
            base64.decodestring(
                b''.join(DEFAULT_TEMPLATE)
            )
        )


def process_generator(nm):
    if nm.outfile is None:
        filename = '.'.join([
            os.path.dirname(nm.path),
            'html'
        ])
        filepath = os.path.abspath(os.path.join(nm.path, '..'))
        nm.outfile = codecs.open(os.path.join(filepath, filename), 'w', 'utf-8')
    else:
        nm.outfile = codecs.open(nm.outfile, 'w', 'utf-8')

    try:
        nm.template = read_template(nm.template)
    except Exception as e:
        print(e)
    else:
        if DEBUG is True:
            print('Path: %s' % nm.path)
            print('Template: %s' % nm.template)
            print('HTML output: %s' % nm.outfile)

        do(**get_do_params(nm))

        # preparando para parar
        # nm.template.close()
        nm.outfile.close()


if __name__ == '__main__':
    main()
