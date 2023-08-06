ImgHash
=======

Hash images based on pixel content.  Unlinke perceptual hashes that are used to find similar images
this library's purpose is to detect exact copies.

Definition
----------

    sha256( width + height + pixels )

Where:

* width = width encoded as uint 32
* height = width encoded as uint 32
* pixels = all pixels in RGBA as uint8


Implementations
---------------

* JS
* Python 2.x
