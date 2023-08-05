android-asset-resizer
=====================

The Android asset resizer can be used to generate drawable assets from a larger
source image, like an iOS ``@2x`` asset or an ``xhdpi`` drawable.

The script will generate the expected ``mdpi``, ``hdpi``, ``xhdpi`` and
``xxhdpi`` assets from the source image.

If you like this library and it's saved you some time, please consider
supporting further development with a `Gittip donation`_!

Requirements
------------

- PIL (tested with version ``1.1.7``, may work with earlier versions)

Installing
----------

::

    $ pip install android-asset-resizer

If you'd like to use the pillow imaging library instead of PIL you can install
the script with this command:

::

    $ pip install --no-deps android-asset-resizer && pip install pillow

Examples
--------

You can easily generate Android assets from your ``@2x`` iOS assets:

::

    $ aaresize assets/icon@2x.png

Running this command will generate the following assets:

::

    - res
      - drawable-mdpi
        - icon.png
      - drawable-hdpi
        - icon.png
      - drawable-xhdpi
        - icon.png
      - drawable-xxhdpi
        - icon.png

These assets were created from the original ``@2x`` asset where the icon in
the ``drawable-xhdpi`` folder is just a copy of the original.

You can also resize an entire directory of images:

::

    $ aaresize assets/*@2x.png

An Android ``xhdpi`` asset is roughly equivalent to an ``@2x`` asset, so you
can easily resize those too:

::

    $ aaresize res/drawable-xhdpi/*.png

If you have a large ``drawable-xxhdpi`` asset you can use the ``--density``
flag to generate the smaller assets:

::

    $ aaresize res/drawable-xxhdpi/*.png --density=xxhdpi

You can also easily add a prefix to your new assets:

::

    $ aaresize assets/*@2x.png --prefix=ic_

Use the ``--ldpi`` flag to generate low density assets:

::

    $ aaresize res/drawable-xhdpi/*.png --ldpi

Use the ``--exclude`` flag to specify a list of files that should not be
resized:

::

    $ aaresize res/drawable-xhdpi/*.png --exclude=ic_launcher.png,ic_status.png

You can also import the ``AssetResizer`` class and incorporate it into your
own scripts:

::

    from PIL import Image
    from android_asset_resizer.resizer import AssetResizer

    # Create our resizer
    resizer = AssetResizer(out_dir, source_density='xhdpi',
        prefix='ic_', image_filter=Image.ANTIALIAS)

    # Make our resource directories
    resizer.mkres()

    # Resize an image
    resizer.resize(path)

Publishing
----------

::

    # Register with pypi (only done once)
    $ python setup.py register

    # Upload a new source distribution to pypi
    $ python setup.py sdist upload

Bug reports
-----------

If you encounter any issues, please open a new issue on the project's
`GitHub page`_.

License
-------

See the LICENSE_ file.

.. _Gittip donation: https://www.gittip.com/twaddington/
.. _LICENSE: https://github.com/twaddington/android-asset-resizer/blob/master/LICENSE 
.. _GitHub page: https://github.com/twaddington/android-asset-resizer
