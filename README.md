# rdof
Python script to remove duplicate object files from a static library.

## Usage

    $ Python rdof.py source target

Remove all object files contains in target statick library from source static library and create a new source static library file in current directory.

For example:

    $ Python rdof.py libcocos2d-x.a libssl.a

Remove all object files contains in `libssl.a` from `libcocos2d-x.a` and create a new static library file `new.libcocos2d-x.a`.

More description can be found in [my blog](http://guojiubo.com).
