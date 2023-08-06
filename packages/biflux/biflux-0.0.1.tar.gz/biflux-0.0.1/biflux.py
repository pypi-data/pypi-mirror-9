# coding=utf-8
"""
This module allows one to compile a BiFluX update using BiFluX and GHC,
as well as to perform both forward and backward transformations using a
compiled update.
"""

import subprocess

class Compiler:
    """
    A compiler to produce a bidirectional transformation from an update
    file, a source DTD, and a view DTD.
    """

    def __init__(self, bifluxex, ghcex, source_dtd, view_dtd, update,
                 transformation_src, output):
        self.bifluxex = bifluxex
        self.ghcex = ghcex
        self.source_dtd = source_dtd
        self.view_dtd = view_dtd
        self.update = update
        self.transformation_src = transformation_src
        self.output = output
        self.transformation = None

    def compile(self):
        """
        Compiles the transformation to an executable
        """
        self.__generate()
        self.__hs_to_exec()

    def get_transformation(self):
        """
        Returns a Transformation object produced by the compiler. If the
        transformation has not yet been compiled, it is compiled first.
        """
        if self.transformation is None:
            self.compile()
        return self.transformation

    def __generate(self):
        """
        Uses BiFluX to generate a bidirectional transformation in Haskell
        """
        subprocess.call([self.bifluxex,
                         '--sdtd={0}'.format(self.source_dtd),
                         '--vdtd={0}'.format(self.view_dtd),
                         '--bx={0}'.format(self.update),
                         '--bxhs={0}'.format(self.transformation_src)])

    def __hs_to_exec(self):
        """
        Compiles the transformation using ghc
        """
        subprocess.call([self.ghcex, '-o', self.output,
                         self.transformation_src])
        self.transformation = Transformation(self.output)

class Transformation:
    """
    A bidirectional transformation with BiFluX
    """

    def __init__(self, transformation):
        self.transformation = transformation

    def get(self, source, view):
        """
        See fwd
        """
        self.fwd(source, view)

    def put(self, source, view, source_upd):
        """
        See bwd
        """
        self.bwd(source, view, source_upd)

    def fwd(self, source, view):
        """
        Applies a forward transformation on a source, and produces a view
        """
        return subprocess.call([self.transformation,
                                '-f', '-s', source,
                                '-o', view])

    def bwd(self, source, view, source_upd):
        """
        Updates the source 'source' with the view 'view' according to a
        transformation, and writes the output to 'source_upd'
        """
        return subprocess.call([self.transformation,
                               '-b', '-s', source,
                               '-t', view,
                               '-o', source_upd])

