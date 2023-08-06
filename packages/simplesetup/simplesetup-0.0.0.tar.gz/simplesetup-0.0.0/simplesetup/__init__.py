# Copyright (c) 2015. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import inspect

FRAME = inspect.getouterframes(inspect.currentframe())[1]

def _get_caller_module():
    """Use inspection to get the module that *uses* simplesetup so
    that we can refer to its README.md and so on. (Rather than
    looking for that within simplesetup.)
    """
    return inspect.getmodule(FRAME[0])

def _get_caller_dir():
    caller_file = _get_caller_module().__file__
    return os.path.dirname(caller_file)

def _get_caller_name():
    return _get_caller_module().__name__

def _parse_readme():
    readme_filename = os.path.join(_get_caller_dir(), 'README.md')
    with open(readme_filename, 'r') as f:
        readme = f.read()

    try:
        import pypandoc
        readme = pypandoc.convert(readme, to='rst', format='md')
    except:
        print('Conversion of long_description from MD to '
              'reStructuredText failed...')
        pass

def _parse_pip_requirements():
    try:
        from pip.req import parse_requirements
        parsed_reqs = parse_requirements('requirements.txt')
        return [str(req.req) for req in parsed_reqs]
    except ImportError:
        print("Please install pip before proceeding")

import setuptools

def setup(name, version, description, author, author_email,
          status='Development Status :: 3 - Alpha',
          environment='Environment :: Console',
          os='Operating System :: OS Independent',
          license='License :: OSI Approved :: Apache Software License',
          language='Programming Language :: Python',
          topic='Topic :: Scientific/Engineering :: Bio-Informatics',
          audience='Intended Audience :: Science/Research',
          only_if_main=True,
          url_prefix='https://github.com/hammerlab/',
          license_url=('http://www.apache.org/licenses/'
                       'LICENSE-2.0.html')):
    module = inspect.getmodule(FRAME[0])
    caller_name = module.__name__
    classifiers = [status, environment, os, license, language,
                   topic, audience]
    if ((only_if_main and caller_name == '__main__') or
            not only_if_main):
        setuptools.setup(
            name=name,
            version=version,
            description=description,
            author=author,
            author_email=author_email,
            url='%s%s' % (url_prefix, name),
            license=license_url,
            classifiers=classifiers,
            install_requires=_parse_pip_requirements(),
            long_description=_parse_readme(),
            packages=[name],
        )
