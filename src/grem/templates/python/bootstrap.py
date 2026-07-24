"""Declare the default Python project for evaluation by grem.

grem evaluates this trusted module to discover the ``ROOT`` Moniker tree, then
generates that tree by copying declared files from the adjacent ``content/``
directory. Declaration method bodies are never executed.
"""

from grem.scaffold import Moniker, file, folder


NAME = "python"
VERSION = "0.10.0"


class Empty(Moniker):
    pass


class Models(Moniker):
    @folder
    def requirements(self) -> Empty:
        ...

    @folder
    def data(self) -> Empty:
        ...

    @folder
    def domain(self) -> Empty:
        ...

    @folder
    def behavior(self) -> Empty:
        ...


class Harness(Moniker):
    @file("README.md")
    def readme(self):
        ...

    @file("instructions.md")
    def instructions(self):
        ...

    @file("diff.md")
    def diff(self):
        ...

    @file("sync.md")
    def sync(self):
        ...

    @file("upgrade.md")
    def upgrade(self):
        ...


class Adr(Moniker):
    @file("prompt.md")
    def prompt(self):
        ...


class Hmd(Moniker):
    @file("prompt.md")
    def prompt(self):
        ...


class Lenses(Moniker):
    @file("prompt.md")
    def prompt(self):
        ...


class Slides(Moniker):
    @file("prompt.md")
    def prompt(self):
        ...


class DocStyles(Moniker):
    @folder
    def adr(self) -> Adr:
        ...

    @folder
    def hmd(self) -> Hmd:
        ...

    @folder
    def lenses(self) -> Lenses:
        ...

    @folder
    def slides(self) -> Slides:
        ...


class Styles(Moniker):
    @folder
    def doc(self) -> DocStyles:
        ...


class Grem(Moniker):
    @file("config.yaml")
    def config(self):
        ...

    @folder
    def harness(self) -> Harness:
        ...

    @folder
    def styles(self) -> Styles:
        ...


class Proposals(Moniker):
    @file("README.md")
    def readme(self):
        ...

    @file("TEMPLATE.md")
    def template(self):
        ...


class Documentation(Moniker):
    @folder
    def models(self) -> Models:
        ...

    @folder
    def wiki(self) -> Empty:
        ...

    @folder
    def issues(self) -> Empty:
        ...

    @folder
    def proposals(self) -> Proposals:
        ...

    @folder
    def memory(self) -> Empty:
        ...

class Source(Moniker):
    @folder
    def myproject(self) -> Empty:
        ...


class Project(Moniker):
    @folder(".grem")
    def grem(self) -> Grem:
        ...

    @folder
    def src(self) -> Source:
        ...

    @folder
    def tests(self) -> Empty:
        ...

    @folder
    def doc(self) -> Documentation:
        ...

    @file("CLAUDE.md")
    def claude(self):
        ...

    @file("AGENTS.md")
    def agents(self):
        ...

    @file("pyproject.toml")
    def pyproject(self):
        ...

    @file("README.md")
    def readme(self):
        ...


ROOT = Project
