set PATH=%PATH%;%VIRTUAL_ENV%\Scripts
pip install -U -e .[test,build]
nosetests --with-xunit --with-cov --cov=testfixtures
python setup.py sdist
