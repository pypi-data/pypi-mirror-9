export PYTHONPATH=.
nosetests --exe -v -s --nologcapture --with-coverage --cover-package=spirol --cover-erase --cover-html-dir=~/.coverage --cover-branches --with-id --id-file=.test-ids --with-xunit tests
