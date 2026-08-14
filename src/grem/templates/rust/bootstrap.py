"""Declare the default Rust project for evaluation by grem.

grem evaluates this trusted module to discover the ``ROOT`` Moniker tree, then
generates that tree by copying declared files from the adjacent ``content/``
directory. Declaration method bodies are never executed.
"""

from grem.scaffold import Moniker, file, folder


NAME = "rust"
VERSION = "0.1.0"


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


class SkillGrem(Moniker):
    @file("SKILL.md")
    def skill(self):
        ...


class Skills(Moniker):
    @folder
    def grem(self) -> SkillGrem:
        ...


class ClaudeConfig(Moniker):
    @folder
    def skills(self) -> Skills:
        ...


class GremIssues(Moniker):
    @folder
    def archive(self) -> Empty:
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

    @folder
    def issues(self) -> GremIssues:
        ...


class Proposals(Moniker):
    @file("README.md")
    def readme(self):
        ...

    @file("TEMPLATE.md")
    def template(self):
        ...


class Wiki(Moniker):
    @file("README.md")
    def readme(self):
        ...

    @file("hyper-markdown.hmd")
    def hyper_markdown(self):
        ...

    @file("kanban.hmd")
    def kanban(self):
        ...


class Issues(Moniker):
    @file("kanban.yaml")
    def kanban(self):
        ...


class Documentation(Moniker):
    @file("stack.md")
    def stack(self):
        ...

    @folder
    def models(self) -> Models:
        ...

    @folder
    def wiki(self) -> Wiki:
        ...

    @folder
    def issues(self) -> Issues:
        ...

    @folder
    def proposals(self) -> Proposals:
        ...

    @folder
    def memory(self) -> Empty:
        ...


class Source(Moniker):
    @file("lib.rs")
    def lib(self):
        ...

    @file("main.rs")
    def main(self):
        ...


class Tests(Moniker):
    @file("cli.rs")
    def cli(self):
        ...


class Project(Moniker):
    @folder(".claude")
    def claude_config(self) -> ClaudeConfig:
        ...

    @folder(".grem")
    def grem(self) -> Grem:
        ...

    @folder
    def src(self) -> Source:
        ...

    @folder
    def tests(self) -> Tests:
        ...

    @folder
    def doc(self) -> Documentation:
        ...

    @file(".gitignore")
    def gitignore(self):
        ...

    @file(".gremignore")
    def gremignore(self):
        ...

    @file("CLAUDE.md")
    def claude(self):
        ...

    @file("AGENTS.md")
    def agents(self):
        ...

    @file("Cargo.toml")
    def cargo(self):
        ...

    @file("rust-toolchain.toml")
    def toolchain(self):
        ...

    @file("README.md")
    def readme(self):
        ...


ROOT = Project
