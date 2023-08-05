Release Checklist
=================

 * double-check version updated, sadly in a few places:
    * Makefile
    * setup.py
    * txtorcon/__init__.py

 * run all tests, on all configurations
    * "tox"

 * "make pep8" should run cleanly (ideally)

 * update docs/releases.rst to reflect upcoming reality
    * blindly make links to the signatures
    * update heading, date

 * "make dist" and "make dist-sig" (if on signing machine)
    * creates:
      dist/txtorcon-X.Y.Z.tar.gz.asc
      dist/txtorcon-X.Y.Z-py2-none-any.whl.asc
    * add the signatures to "signatues/"
    * add ALL FOUR files to dist/ (OR fix twine commands)

 * (if not on signing machine) do "make dist"
   * scp dist/txtorcon-X.Y.Z.tar.gz dist/txtorcon-X.Y.Z-py2-none-any.whl signingmachine:
   * sign both, with .asc detached signatures (see Makefile for command)
   * copy signatures back to build machine, in dist/
   * double-check that they validate

 * generate sha256sum for each:
      sha256sum dist/txtorcon-X.Y.Z.tar.gz dist/txtorcon-X.Y.Z-py2-none-any.whl

 * copy signature files to <root of dist>/signatures and commit them
   along with the above changes for versions, etc.

 * draft email to tor-dev (and probably twisted-python):
    * example: https://lists.torproject.org/pipermail/tor-dev/2014-January/006111.html
    * example: https://lists.torproject.org/pipermail/tor-dev/2014-June/007006.html
    * copy-paste release notes, un-rst-format them
    * include above sha256sums
    * clear-sign the announcement
    * gpg --armor --clearsign -u meejah@meejah.ca path/to/release-announcement-X-Y-Z
    * Example boilerplate:

            I'm [adjective] to announce txtorcon 0.10.0. This adds
            several amazing features, including levitation. Full list
            of improvements:

               * take from releases.rst
               * ...but un-rST them

            You can download the release from PyPI or GitHub (or of
            course "pip install txtorcon"):

               https://pypi.python.org/pypi/txtorcon/0.10.0
               https://github.com/meejah/txtorcon/releases/tag/v0.10.0

            Releases are also available from the hidden service:

               http://timaq4ygg2iegci7.onion/txtorcon-0.12.0.tar.gz
               http://timaq4ygg2iegci7.onion/txtorcon-0.12.0.tar.gz.asc

            sha256sum reports:

               910ff3216035de0a779cfc167c0545266ff1f26687b163fc4655f298aca52d74  txtorcon-0.10.0-py2-none-any.whl
               c93f3d0f21d53c6b4c1521fc8d9dc2c9aff4a9f60497becea207d1738fa78279  txtorcon-0.10.0.tar.gz

            thanks,
            meejah

 * copy release announcement to signing machine, update code

 * create signed tag
    * git tag -s -u meejah@meejah.ca -F path/to/release-announcement-X-Y-Z vX.Y.Z

 * copy dist/* files + signatures to hidden-service machine
 * copy them to the HTML build directory! (docs/_build/html/)

 * git pull and build docs there
    * FIXME: why aren't all the dist files copied as part of doc build (only .tar.gz)

 * download both distributions + signatures from hidden-service
    * verify sigs
    * verify sha256sums versus announcement text
    * verify tag (git tag -v v0.9.2) on machine other than signing-machine

 * upload release
    * to PyPI: "make release" (which uses twine so this isn't the same step as "sign the release")
       * make sure BOTH the .tar.gz and .tar.gz.asc (ditto for .whl) are in the dist/ directory first!!)
       * ls dist/txtorcon-${VERSION}*
       * note this depends on a ~/.pypirc file with [server-login] section containing "username:" and "password:"
    * to github: use web-upload interface to upload the 4 files (both dists, both signature)

 * make announcement
    * post to tor-dev@ the clear-signed release announcement
    * post to twisted-python@ the clear-signed release announcement
    * tell #tor-dev??
