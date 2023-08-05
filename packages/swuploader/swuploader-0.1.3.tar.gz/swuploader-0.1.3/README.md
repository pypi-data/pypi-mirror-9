Shapeways Uploader
==================

Shapeways API bulk uploader.

## Install
### pip
```bash
pip install swuploader
```
### Git
```bash
git clone git://github.com/brettlangdon/swuploader.git
cd ./swuploader
python setup.py install
```

## Usage
```
Usage:
  swuploader (-h | --help)
  swuploader (-v | --version)
  swuploader auth [--server=<server>] <consumer_key> <consumer_secret> <output>
  swuploader upload [--models=<models>] [--out=<out>] [--server=<server>] <auth_tokens>

Options:
  -h --help                      Show this help text
  -v --version                   Show version information
  -m <models> --models=<models>  Set the directory for where model ini's are available [default: ./]
  -o <out> --out=<out>           Set the directory where the model ini's are moved to after upload [default: ./]
  -s <server> --server=<server>  Set different api server url if desired.
```

### Setup App

Before you can use `swuploader` you must have an application setup on
shapeways.com this can be setup/registered at
https://developers.shapeways.com/manage-apps/create.
You will also need to note your `consumer key` and `consumer secret` from your
app's settings page.

### Authenticate
Once you have an application setup with shapeways.com you must authenticate with
the api server before you can start to upload models, to do so run the
following:

```bash
swuploader auth <consumer_key> <consumer_secret> ./auth.json
```

This will give you a url to use for authentication, once you follow that url and
authorize with your application you will be given a `verifier code` to enter to
complete the authentication process.

As a result of running this command you will have a file `auth.json` which will
contain required keys/tokens/secrets necessary for all subsequent requests.

### Upload
Finally you are ready to upload. In order to upload you need a folder which
contains the model files that you want to upload (see
http://www.shapeways.com/tutorials/supported-applications for a list of
supported file types).

For each model file you must supply an additional `.ini` file containing
information about the model which is being uploaded. For example:
```ini
name=Sphere
file=./sphere.stl
```

For supported properties please see:
http://developers.shapeways.com/docs?li=dh_docs#POST_-models-v1 for the list of
accepted paramaters.

*note* for materials, please provide them in the format
`material.<material_id>=<markup>`.

Your directory structure should look similar to:

```bash
$ ls -1
auth.json
model.obj
model.ini
sphere.ini
sphere.stl
```

Once you have your model files and `.ini` files ready you can run `swuploader`
like so:

```bash
swuploader upload ./auth.json
```

`swuploader` will then read all the `.ini` files in the current directory and
upload the model file assigned to the `file` attribute along with the other
provided properties in the `.ini` file.


## License
```
The MIT License (MIT) Copyright (c) 2014 Brett Langdon <brett@blangdon.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
