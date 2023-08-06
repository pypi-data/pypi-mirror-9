from __future__ import absolute_import

from argparse import ArgumentParser


def build_argument_parser(executable):
    """creates an argument parser from the given `executable` model.

    :param executable: CLI Model
    :type executable: clictk.model.Executable
    :return:
    """

    a = ArgumentParser()
    a.add_argument("--xml", action="store_true", dest="__xml__", help="show cli xml")

    for p in executable:
        o = []
        if p.flag: o.append("-%s" % p.flag)
        if p.longflag: o.append("--%s" % p.longflag)
        a.add_argument(
            *o,
            metavar=p.type.upper(),
            dest=p.name,
            action="store",
            help=p.description
        )

    return a