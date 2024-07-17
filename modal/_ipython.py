# Copyright Modal Labs 2022
import sys

ipy_outstream = None
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

    ipy_outstream = ipykernel.iostream.OutStream
except ImportError:
    pass
