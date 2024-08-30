#! /bin/bash
echo 'remove -> rebuild -> install [pycarlanet]'
pip uninstall pycarlanet -y && rm -rf ./dist/* && python setup.py bdist_wheel && pip install ./dist/*