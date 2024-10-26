#! /bin/bash
echo 'remove -> rebuild -> install [pycarlanet]'
pip uninstall pycarlanet -y && rm -rf ./dist/* && python -m build ./ && pip install --no-deps ./dist/*.whl