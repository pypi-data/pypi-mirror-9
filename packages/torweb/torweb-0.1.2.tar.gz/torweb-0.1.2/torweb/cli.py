# -*- coding: utf-8 -*-
import os
import sys
import logging
from torweb import make_application

class nul:
    write = staticmethod(lambda s: None)


def show_tables(app):
    def action():
        """show tables of all application databases"""
        for dbname, store in app.accost_application.db.items():
            print '[%s]'%dbname
            store.showTables()
        engine = getattr(app.accost_application.app, "engine")
        if not engine: return
        conn = engine.connect()
        for r in conn.execute("SHOW TABLES").fetchall():
            print r[0]

    return action


def show_create(app):
    def action():
        """show create table sql of all application databases"""
        for dbname, store in app.accost_application.db.items():
            print '[%s]'%dbname
            store.showCreate()
        engine = getattr(app.accost_application.app, "engine")
        if not engine: return
        conn = engine.connect()
        for r in conn.execute("SHOW TABLES").fetchall():
            for line in conn.execute("SHOW CREATE TABLE `%s`"%r[0]):
                print line[1]
                print

    return action


def dbshell(app):
    def action():
        """run mysql client use database configuration of the application"""
        db = app.accost_application.db
        if len(db) == 0:
            sys.exit('database not found')
        elif len(db) == 1:
            db.popitem()[1].runDBShell()
        else:
            print 'There are %d databases, please choose one of them:'%len(db.items())
            name = input(', '.join([dbname for dbname in db]))
            if not name in db:
                sys.exit('no such database')
            db[name].runDBShell()

    return action


def show_urls(app):
    def action():
        """display url structure"""
        for rule in app.accost_application.url_mapping.iter_rules():
            print "%-30s"%rule, rule.endpoint

    return action


def bshell(app):
    def action():
        from bpython import embed
        embed({"app": app})

    return action


# 以下为使用argparse重新写的命令行界面
def add_daemon_arguments(parser):
    parser.add_argument("--daemonize", default=False, action="store_true", dest="daemonize", help="run as a daemon")
    parser.add_argument("--pidfile", default="", metavar="PATH", dest="pidfile", help="pidfile to use if daemonized, only works when daemonized")
    parser.add_argument("--workdir", default=".", metavar="DIR", dest="workdir", help="only works when daemonized")
    parser.add_argument("--outlog", default=None, dest="outlog", help="only works when daemonized")
    parser.add_argument("--errlog", default=None, dest="errlog", help="only works when daemonized")
    parser.add_argument("--umask", default=022, type=int, dest="umask", help="only works when daemonized")
    parser.add_argument("--user", default=None, dest="user", help="only works when it is run by root user")


def add_host_arguments(parser):
    parser.add_argument("--host", default="0.0.0.0", metavar="HOST", dest="hostname", help="hostname to bind (default 0.0.0.0)")
    parser.add_argument("-p", "--port", default=7777, type=int, metavar="PORT", dest="port", help="server port (default 7777)")
    parser.add_argument("--server_name", default="0.0.0.0", metavar="NAME", dest="server_name")


class cmd_bshell(object):
    """bpython shell"""
    def __init__(self, parser):
        pass

    def __call__(self, args, app):
        from bpython import embed
        embed({"app": app})


class cmd_shell(object):
    """Start a new interactive python session."""
    def __init__(self, parser):
        parser.add_argument("--no-ipython", default=True, action="store_false", dest="ipython")

    def __call__(self, args, app):
        banner = 'Interactive Accost Shell'
        namespace = dict(app=app)
        if args.ipython:
            try:
                try:
                    from IPython.frontend.terminal.embed import InteractiveShellEmbed
                    sh = InteractiveShellEmbed(banner1=banner)
                except ImportError:
                    from IPython.Shell import IPShellEmbed
                    sh = IPShellEmbed(banner=banner)
            except ImportError:
                pass
            else:
                sh(local_ns=namespace)
                return
        from code import interact
        interact(banner, local=namespace)


class cmd_runserver(object):
    """Start a new development server."""
    def __init__(self, parser):
        add_host_arguments(parser)

    def __call__(self, args, app):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        from werkzeug.serving import run_simple
        run_simple(args.hostname, args.port, app, use_reloader=True, use_debugger=True,
                   use_evalex=True, threaded=False, processes=1)


class cmd_urls(object):
    """display url structure"""
    def __init__(self, parser):
        pass

    def __call__(self, args, app):
        for rule in sorted(app.accost_application.url_mapping.iter_rules(), key=lambda r: str(r)):
            print "%-30s"%rule, find_route(rule)


class cmd_dbshell(object):
    """run mysql client use database configuration of the application"""
    def __init__(self, parser):
        pass

    def __call__(self, args, app):
        db = app.accost_application.db
        if len(db) == 0:
            sys.exit('database not found')
        elif len(db) == 1:
            db.popitem()[1].runDBShell()
        else:
            print 'There are %d databases, please choose one of them:'%len(db.items())
            name = input(', '.join([dbname for dbname in db]))
            if not name in db:
                sys.exit('no such database')
            db[name].runDBShell()


class cmd_show_tables(object):
    """show tables of all application databases"""
    def __init__(self, parser):
        pass

    def __call__(self, args, app):
        for dbname, store in app.accost_application.db.items():
            print '[%s]'%dbname
            store.showTables()
        engine = getattr(app.accost_application.app, "engine")
        if not engine: return
        conn = engine.connect()
        for r in conn.execute("SHOW TABLES").fetchall():
            print r[0]


class cmd_show_create(object):
    """show create table sql of all application databases"""
    def __init__(self, parser):
        pass

    def __call__(self, args, app):
        for dbname, store in app.accost_application.db.items():
            print '[%s]'%dbname
            store.showCreate()
        engine = getattr(app.accost_application.app, "engine")
        if not engine: return
        conn = engine.connect()
        for r in conn.execute("SHOW TABLES").fetchall():
            for line in conn.execute("SHOW CREATE TABLE `%s`"%r[0]):
                print line[1]
                print


class Command(object):
    def __init__(self, app):
        self.app = app
        self.application = application = make_application(app)
        self._actions = [
                ('shell'    ,   cmd_shell),
                ('runserver',   cmd_runserver),
                ('bshell'   ,   cmd_bshell),
                ('urls'     ,   cmd_urls),
                ('showcreate',  cmd_show_create),
                ('showtables',  cmd_show_tables),
        ]
        import argparse
        self.parser = argparse.ArgumentParser(description='Command Line Operations', add_help=True)
        self.subparsers = self.parser.add_subparsers(help='Sub Command Help')

    def subcmd_help(self, args, app):
        cmd = args.cmd[0]
        if cmd in self.subparsers.choices:
            self.subparsers.choices[cmd].print_help()
        else:
            print "invalid command: %s"%cmd

    def run(self):
        for name, action in self._actions:
            self.register(action, name)
        p = self.subparsers.add_parser("help", add_help=False, help="show command help document")
        p.add_argument("cmd", nargs=1, metavar="COMMAND")
        p.set_defaults(func=self.subcmd_help)
        args = self.parser.parse_args()
        if hasattr(args, "func"):
            args.func(args, self.application)

    def register(self, cls, name=None):
        name = name if name is not None else cls.__class__.__name__
        subparser = self.subparsers.add_parser(name, add_help=True, help=cls.__doc__)
        obj = cls(subparser)
        subparser.set_defaults(func=obj)
