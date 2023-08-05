## Instructions for distributing Epicenter to PyPI
Create a user on PyPI (https://pypi.python.org/pypi) if you don't have one. Get the user added as a maintainer to the Epicenter package.

Put the following into `~/.pypirc`

```    
[distutils]
index-servers=
    pypi
    pypitest

[pypitest]
repository = https://testpypi.python.org/pypi
username = <your username>
password = <password>

[pypi]
repository = https://pypi.python.org/pypi
username = <your username>
password = <password>
```

### Development Process

1. Make changes and fix bugs!
2. Ensure that Epicenter is registered with PyPI. This is already done with the official PyPI website, but the test website is periodically wiped clean, so you will eventually have to recreate the account and package on this site if you want to test. It's not necessary to use the username/password in `publish-flow.sh`, but it doesn't hurt to do so (especially as we are using `twine` from PyPA, which does not send the username and password in the clear).
3. Bump the version as appropriate.
4. Run the script `./publish-package.sh`. If you want to just upload it to the pypi test servers, then add the argument `test`.
5. Ensure things are working (you should be on a new python virtual environment) by running the command `pip install epicenter`. If you're downloading from the testpypi server, then the command is `pip install -i https://testpypi.python.org/pypi epicenter`.

#### Note
The Forio PyPI account (author account) is currently associated with the e-mail address wglass@forio.com.