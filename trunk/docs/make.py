"Makefile for Sphinx documentation, adapted to python"
import os
from astdoc.make_helper import SphinxMaker
if __name__ == "__main__":
    SphinxMaker.execute(root_dir=os.path.join(__file__,os.pardir))
