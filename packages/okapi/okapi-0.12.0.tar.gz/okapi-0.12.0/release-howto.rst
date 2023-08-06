Release Howto
=============

To make a release, please follow these steps:

1. Test the code
2. Increase the version number in okapi/__init__.py

vim okapi/__init__.py

3. In CHANGES.rst create a section for the new release with the main changes

vim CHANGES.rst

4. Commit these changes

git commit

5. Create a git tag with the version

git tag VERSION_STRING

6. Push everything to Github

git push --tags

7. Create the release on PyPI:

python setup.py sdist register upload
