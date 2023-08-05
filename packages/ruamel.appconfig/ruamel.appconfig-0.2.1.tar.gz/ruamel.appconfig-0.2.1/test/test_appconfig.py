
import os
import sys
import pytest
import ConfigParser

from ruamel.appconfig import AppConfig
import ruamel.yaml

@pytest.fixture
def prog_name(monkeypatch, tmpdir):
    """set up a temporary directory for the """
    tmpdir.mkdir('.config')
    tmp_name = str(tmpdir)
    monkeypatch.setenv('HOME', tmp_name)
    return tmp_name

def to_stdout(*args):
    sys.stdout.write(' '.join(args))

class TestAppConfig:

    def test_add_config(self, prog_name, capsys):
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('--delete', '-d', default='bla',
                            help='Hallo (default: %(default)s)')
        ac = AppConfig(
            'testa',
            filename=AppConfig.check,
            parser=parser,  # sets --config option
            warning=to_stdout,
        )
        ac.set_defaults()
        with pytest.raises(SystemExit):
            parser.parse_args(['-h'])
        out, err = capsys.readouterr()
        assert """\
  --config FILE         set FILE as configuration file
                        [~/.config/testa/testa.yaml]
""" in out
        assert '/tmp/' in os.environ['HOME']

    def test_no_overwrite_config(self, prog_name, capsys):
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('--config', help='Hallo')
        parser.add_argument('--delete', '-d', default='bla',
                            help='Hallo (default: %(default)s)')
        ac = AppConfig(
            'testa',
            filename=AppConfig.check,
            parser=parser,  # sets --config option
            warning=to_stdout,
        )
        ac.set_defaults()
        with pytest.raises(SystemExit):
            parser.parse_args(['-h'])
        out, err = capsys.readouterr()
        assert """\
  --config CONFIG       Hallo
""" in out
        assert """\
  --delete DELETE, -d DELETE
                        Hallo (default: bla)
""" in out
        #print 'pos', prog_name, os.environ['HOME']
        assert '/tmp/' in os.environ['HOME']

    def test_read_default(self, prog_name, capsys):
        """save something to config and read it back"""
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('--delete', '-d', default='bla',
                            help='Hallo (default: %(default)s)')
        ac = AppConfig(
            'testa',
            filename=AppConfig.check,
            parser=parser,  # sets --config option
            warning=to_stdout,
        )
        ac._config['global'] = {}
        ac._config['global']['delete'] = 'me'
        ac._config.write()
        # read it in once more
        ac1 = AppConfig(
            'testa',
            filename=AppConfig.check,
            parser=parser,  # sets --config option
            warning=to_stdout,
        )
        ac1.set_defaults()
        with pytest.raises(SystemExit):
            parser.parse_args(['-h'])
        out, err = capsys.readouterr()
        assert """\
  --delete DELETE, -d DELETE
                        Hallo (default: me)
""" in out
        #print 'pos', prog_name, os.environ['HOME']
        assert '/tmp/' in os.environ['HOME']


    def test_global_save_default(self, prog_name, capsys):
        """save something to default and read it back"""
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('--delete', '-d', default='bla',
                            help='Hallo (default: %(default)s)')
        parser.add_argument('--owner', default='itsme',
                            help='Hallo (default: %(default)s)')
        parser.add_argument('--force', action='store_true',
                            help='Hallo (default: %(default)s)')
        ac = AppConfig(
            'testa',
            filename=AppConfig.check,
            parser=parser,  # sets --config option
            warning=to_stdout,
            add_save=True,
        )
        ac.set_defaults()
        args = ac.parse_args(['--delete', 'two', '--save-defaults'])
        out, err = capsys.readouterr()
        print out
        if err:
            print 'err:', err
            assert False
        #cp = ConfigParser.SafeConfigParser()
        #cp.read(ac.get_file_name())
        #assert cp.getboolean('global', 'force') == False
        #assert cp.get('global', 'delete') == 'two'
        #assert cp.get('global', 'owner') == 'itsme'
        cp = ruamel.yaml.load(open(ac.get_file_name()),
                              Loader=ruamel.yaml.RoundTripLoader)
        assert cp['global']['force'] is False
        assert cp['global']['delete'] == 'two'
        assert cp['global']['owner'] == 'itsme'

    def test_sub_save_default(self, prog_name, capsys):
        """save something to subparser default and read it back"""
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('--force', action='store_true',
                            help='Hallo (default: %(default)s)')
        subparsers = parser.add_subparsers()
        subparsers.add_parser('one')
        sp = subparsers.add_parser('two')
        sp.add_argument('--delete', '-d', default='bla',
                            help='Hallo (default: %(default)s)')
        ac = AppConfig(
            'testa',
            filename=AppConfig.check,
            parser=parser,  # sets --config option
            warning=to_stdout,
            add_save=True,
        )
        ac.set_defaults()
        with pytest.raises(SystemExit):
            parser.parse_args(['two', '-h'])
        out, err = capsys.readouterr()
        assert '--save-defaults' in out.splitlines()[-1]
        #a = parser.parse_args(['two', '--delete', 'three', '--save-defaults'])
        args = ac.parse_args(['--force', 'two', '--delete', 'three', '--save-defaults'])
        assert args.save_defaults
        #out, err = capsys.readouterr()
        #cp = ConfigParser.SafeConfigParser()
        #cp.read(ac.get_file_name())
        #assert cp.getboolean('global', 'force') == True
        #assert cp.get('two', 'delete') == 'three'
        cp = ruamel.yaml.load(open(ac.get_file_name()),
                              Loader=ruamel.yaml.RoundTripLoader)
        assert cp['global']['force'] is True
        assert cp['two']['delete'] == 'three'

    def test_two_level_subparsers(self, capsys):
        """double level currently not handled for loading and saving"""
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('--verbose', action='store_true',
                            help='set to be verbose (default: %(default)s)')
        subparsers = parser.add_subparsers()
        sp = subparsers.add_parser('one')
        sp.add_argument('--arg-one')
        subparsers_one = sp.add_subparsers()
        sp1a = subparsers_one.add_parser('oneone')
        sp1b = subparsers_one.add_parser('onetwo')
        sp1a.add_argument('--arg-oneone')
        sp.add_argument('filenames')
        sp = subparsers.add_parser('two')
        sp.add_argument('--arg-two')
        with pytest.raises(SystemExit):
            args = parser.parse_args(['one', 'oneone', '-h'])
        #out, err = capsys.readouterr()
        #print out
        #print args
        #assert False


