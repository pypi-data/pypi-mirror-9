hmac_cli
========

Simple CLI for encrypting data with a private key, using HMAC

::

    $ hmac --help
    Usage: hmac [OPTIONS] INPUT_FILE

      Encrypt data in INPUT_FILE using HMAC

      with provided secret cryptographic key

    Options:
      --key TEXT                      encryption key. Will prompt for if not
                                      provided.
      --algorithm [md5|sha1|sha224|sha256|sha384|sha512]
                                      algorithm to use
      --help                          Show this message and exit.

    $ hmac --key foo README.rst
    515902266c1a02e60452d152855aa3b46ed5b006

    $ echo "Hello" | hmac --key foo -
    aabbe57c6a0ba953cd907071004a1db16fe78891

    $ hmac -
    Key: ******
    Repeat for confirmation: ******
    Here is some text
    ^D
    c7ab7eed09fff2d0fcf258dfde8222d264013c4f
