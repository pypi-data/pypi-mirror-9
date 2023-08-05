release:
	mkrelease -d ajung@svn.zopyx.com:/var/www/sdist-pp .

.PHONY: docs
docs:
	cd docs; make html

upload-docs:
	python setup.py upload_docs --upload-dir docs/build/html
