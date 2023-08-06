# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Configuration tool
# :Creato:    gio 18 apr 2013 18:43:18 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from argparse import ArgumentParser
from binascii import hexlify
from datetime import date
from os import urandom
from os.path import abspath, dirname, exists, join
from urllib.request import urlopen

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import transaction

from pyramid.paster import get_appsettings, setup_logging

from sol.models import Base, Club, DBSession, Player, Rate, Rating, bio
from sol.models.utils import normalize


def create_config(args):
    "Dump/update a configuration file suitable for production"

    import sol

    if exists(args.config):
        print('The config file "%s" already exists!' % args.config)
        return update_config(args)

    alembicdir = join(dirname(dirname(sol.__file__)), 'alembic')
    secret = hexlify(urandom(20)).decode('ascii')
    password = input('Choose a password for the "admin" user: ')
    if not password:
        password = hexlify(urandom(5)).decode('ascii')
        random_password = True
    else:
        random_password = False

    with open(join(dirname(__file__), "config.tpl"), encoding='utf-8') as f:
        configuration = f.read()

    with open(args.config, 'w', encoding='utf-8') as f:
        f.write(configuration.format(secret=secret, password=password,
                                     alembicdir=alembicdir))

    print('The configuration file "%s" has been successfully created' % args.config)
    print('The password for the admin user is "%s"%s' % (
        password, ", you should change it!" if random_password else ""))


def update_config(args):
    "Update an existing configuration file"

    import re
    import sol

    if not exists(args.config):
        print('The config file "%s" does not exists!' % args.config)
        return None

    alembicdir = join(dirname(dirname(sol.__file__)), 'alembic')

    with open(args.config, 'r', encoding='utf-8') as f:
        configuration = f.read()

    alembicdir_re = re.compile(r'script_location\s*=\s*(.+)\s*$')

    lines = configuration.splitlines()
    for pos, line in enumerate(lines):
        match = alembicdir_re.match(line)
        if match:
            if match.group(1) == alembicdir:
                print('The config file "%s" is already up-to-date!' % args.config)
                return None

            lines[pos] = 'script_location = ' + alembicdir
            break

    with open(args.config, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        f.write('\n')

    print('The configuration file "%s" has been successfully updated' % args.config)


def initialize_db(args):
    "Initialize the database structure"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')

    if engine.has_table('tourneys'):
        print('Database "%s" already exist.'
              ' You may want to execute "upgrade-db" instead...' % engine.url)
        return None

    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    print('The database "%s" has been successfully initialized' % engine.url)

    from alembic.config import Config
    from alembic import command

    cfg = Config(args.config, ini_section="app:main")
    command.stamp(cfg, "head")


def upgrade_db(args):
    "Upgrade the database structure"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    from alembic.config import Config
    from alembic import command

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    cfg = Config(args.config, ini_section="app:main")
    command.upgrade(cfg, "head")

    print('The database "%s" has been successfully upgraded' % engine.url)


def restore_all(args):
    "Load historic data into the database, player's portraits and club's emblems as well"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    sasess = DBSession()
    pdir = settings['sol.portraits_dir']
    edir = settings['sol.emblems_dir']

    if args.url.startswith('file://') or exists(args.url):
        if not args.url.startswith('file://'):
            args.url = abspath(args.url)
        backup_url = args.url
    else:
        backup_url = args.url + 'bio/backup'
        if not args.all:
            backup_url += '?only_played_tourneys=1'

    print("Loading backup from %s..." % backup_url)

    with transaction.manager:
        tourneys, skipped = bio.restore(sasess, pdir, edir, url=backup_url)

    print("Done, %d new/updated tourneys, %d skipped/already present." % (len(tourneys),
                                                                          skipped))


def backup_all(args):
    "Save a backup of the database, player's portraits and club's emblems as well"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    sasess = DBSession()
    pdir = settings['sol.portraits_dir']
    edir = settings['sol.emblems_dir']

    print("Saving backup to %s..." % args.location)

    with transaction.manager:
        bio.backup(sasess, pdir, edir,
                   args.location, args.keep_only_if_changed)

    print("Done.")


def player_unique_hash(firstname, lastname, nickname):
    from hashlib import md5
    from time import time

    hash = md5()
    hash.update(firstname.encode('ascii', 'ignore'))
    hash.update(lastname.encode('ascii', 'ignore'))
    hash.update(nickname.encode('ascii', 'ignore'))
    hash.update(str(time()).encode('ascii', 'ignore'))
    return hash.hexdigest()[:15]


def _evaluator(fmap, formula):
    from math import exp

    def evaluator(record, fmap=fmap, formula=formula):
        locs = {}
        for fname in fmap.values():
            if fname in fmap:
                try:
                    locs[fname] = float(record[fname])
                except:
                    pass
        return eval(formula, {'exp': exp}, locs)

    test = {fname: '1' for fname in fmap.values()}
    try:
        evaluator(test)
    except:
        return None
    else:
        return evaluator


def load_historical_rating(args):
    "Load historic rating into the database from a CSV text file"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    fmap = dict(firstname='firstname',
                lastname='lastname',
                nickname='nickname')
    for item in args.map:
        if '=' in item:
            internal, external = item.split('=')
            internal = internal.strip()
            external = external.strip()
        else:
            internal = external = item.strip()
        fmap[internal] = external

    refdate = date(*map(int, args.date.split('-')))

    try:
        int(args.deviation)
    except ValueError:
        deviation = _evaluator(fmap, args.deviation)
        if deviation is None:
            print('The formula "%s" to compute the deviation is invalid!' % args.deviation)
            return 128
    else:
        deviation = lambda dummy, rd=int(args.deviation): rd

    try:
        float(args.volatility)
    except ValueError:
        volatility = _evaluator(fmap, args.volatility)
        if volatility is None:
            print('The formula "%s" to compute the volatility is invalid!' % args.volatility)
            return 128
    else:
        volatility = lambda dummy, rd=args.volatility: rd

    if args.rate is not None:
        rate = _evaluator(fmap, args.rate)
        if rate is None:
            print('The formula "%s" to compute the rate is invalid!' % args.rate)
            return 128
    else:
        rate = lambda record: record[fmap['rate']]

    if not args.dry_run:
        setup_logging(args.config)

    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    sasess = DBSession()

    if not args.dry_run:
        if sasess.query(Rating).filter_by(description=args.description).first():
            print('Rating "%s" already exists!' % args.description)
            return 128

    if args.url.startswith('file://') or exists(args.url):
        if not args.url.startswith('file://'):
            args.url = "file://" + abspath(args.url)

    print("Loading ratings from %s..." % args.url)

    separator = '\t' if args.tsv else ','

    new = set()
    done = set()
    rates = []
    with transaction.manager, urlopen(args.url) as csvfile:
        data = csvfile.read().decode(args.encoding)
        lines = data.splitlines()
        columns = [c.strip() for c in lines.pop(0).split(separator)]
        for c in fmap.values():
            if not c in columns:
                print('Column "%s" not found!' % c)
                return 128

        for record in (dict(zip(columns, row.split(separator))) for row in lines):
            firstname = normalize(record[fmap['firstname']].strip())
            lastname = normalize(record[fmap['lastname']].strip())
            nickname = record[fmap['nickname']].strip()

            if (firstname, lastname, nickname) in done:
                continue

            done.add((firstname, lastname, nickname))

            try:
                player, merged_into = Player.find(sasess, lastname, firstname, nickname)
            except MultipleResultsFound:
                nickname = player_unique_hash(firstname, lastname, nickname)

            if player is None:
                player = Player(firstname=firstname, lastname=lastname, nickname=nickname)
                new.add(player)
                if 'sex' in fmap:
                    sex = record[fmap['sex']].strip().upper()
                    if sex in 'FM':
                        player.sex = sex
                if 'club' in fmap:
                    clubdesc = normalize(record[fmap['club']].strip())
                    if clubdesc:
                        try:
                            club = sasess.query(Club).filter_by(description=clubdesc).one()
                        except NoResultFound:
                            club = Club(description=clubdesc)

                        player.club = club

            rates.append(Rate(date=refdate, player=player,
                              rate=int(rate(record)),
                              deviation=int(deviation(record)),
                              volatility=volatility(record)))

        if args.dry_run:
            for rate in rates:
                print("%s%s (%s): rate=%d deviation=%s volatility=%s" % (
                    "NEW " if rate.player in new else "",
                    rate.player, rate.player.club,
                    rate.rate, rate.deviation, rate.volatility))
            # Force a rollback
            raise SystemExit
        else:
            rating = Rating(description=args.description,
                            level=args.level,
                            inherit=args.inherit,
                            rates=rates)
            sasess.add(rating)

            print("Done, %d new rates." % len(rates))


def _sound(which, ogg):
    from shutil import copyfile

    if not exists(ogg):
        print('Specified sound file "%s" does not exist!' % ogg)
        return 128
    if not ogg.endswith('.ogg'):
        print('The sound file must be a OGG and have ".ogg" as extension!')
        return 128

    target = join(dirname(dirname(abspath(__file__))), 'static', 'sounds',
                  which+'.ogg')
    print('Copying "%s" to "%s"...' % (ogg, target))
    copyfile(ogg, target)


def start_sound(args):
    "Replace the start sound"

    return _sound('start', args.sound)


def stop_sound(args):
    "Replace the stop sound"

    return _sound('stop', args.sound)


def prealarm_sound(args):
    "Replace the prealarm sound"

    return _sound('prealarm', args.sound)


def main():
    import sys

    parser = ArgumentParser(description="SoL command line admin utility",
                            epilog=('You can get individual commands help'
                                    ' with "soladmin sub-command -h".'))
    subparsers = parser.add_subparsers()

    subp = subparsers.add_parser('create-config',
                                 help=create_config.__doc__)
    subp.add_argument('config', help="Name of the new configuration file")
    subp.set_defaults(func=create_config)

    subp = subparsers.add_parser('update-config',
                                 help=update_config.__doc__)
    subp.add_argument('config', help="Name of the existing configuration file")
    subp.set_defaults(func=update_config)

    subp = subparsers.add_parser('initialize-db',
                                 help=initialize_db.__doc__)
    subp.add_argument('config', help="Name of the configuration file")
    subp.set_defaults(func=initialize_db)

    subp = subparsers.add_parser('upgrade-db',
                                 help=upgrade_db.__doc__)
    subp.add_argument('config', help="Name of the configuration file")
    subp.set_defaults(func=upgrade_db)

    subp = subparsers.add_parser('restore',
                                 help=restore_all.__doc__)
    subp.add_argument('-a', '--all', default=False, action="store_true",
                      help="By default only played tourneys are transfered,"
                      " i.e. only those with at least one played match. This"
                      " flag restores all tourneys.")
    subp.add_argument('config', help="Name of the configuration file")
    subp.add_argument('url', default="http://sol3.arstecnica.it/",
                      nargs="?",
                      help='URL from where historic data will be loaded'
                      ' if different from "http://sol3.arstecnica.it/".'
                      ' It may also be a file:// URI or a local file path'
                      ' name.')
    subp.set_defaults(func=restore_all)

    subp = subparsers.add_parser('backup',
                                 help=backup_all.__doc__)
    subp.add_argument('-k', '--keep-only-if-changed', default=False,
                      action="store_true",
                      help="If given, and the location argument is a"
                      " directory containing other backup archives,"
                      " keep the new backup only if it is different"
                      " from the previous one.")
    subp.add_argument('config', help="Name of the configuration file")
    subp.add_argument('location', nargs="?", default='.',
                      help='Local file name where the backup will be written.'
                      ' If it actually points to an existing directory (its'
                      ' default value is ".", the current working directory)'
                      ' the file name will be generated from the current time'
                      ' and with a ".zip" extension.')
    subp.set_defaults(func=backup_all)

    subp = subparsers.add_parser('load-historical-rating',
                                 help=load_historical_rating.__doc__)
    subp.add_argument('--date', default='1900-01-01',
                      help="Bogus rates date, by default 1900-01-01")
    subp.add_argument('--deviation', default='100',
                      help="Value of the deviation, by default 100,"
                      " or a formula to compute it from other fields")
    subp.add_argument('--volatility', default='0.006',
                      help="Value of the volatility, by default 0.006,"
                      " or a formula to compute it from other fields")
    subp.add_argument('--rate', default=None,
                      help="Formula to compute the player's rate, if needed")
    subp.add_argument('--description',
                      help='Description of the historical rating')
    subp.add_argument('--level', choices='0,1,2,3,4'.split(','), default="0",
                      help="Rating level, 0 by default: 0=historical, 1=international,"
                      " 2=national, 3=regional, 4=courtyard")
    subp.add_argument('--inherit', default=False, action="store_true",
                      help="Whether player's rate will be inherited from other"
                      " ratings at the same level or better, False by default")
    subp.add_argument('--map', action='append', default=[],
                        help="Specify a map between internal (SoL) field name and"
                        " external one")
    subp.add_argument('--encoding', default='utf-8',
                      help="Encoding of the CSV file, by default UTF-8")
    subp.add_argument('--tsv', default=False, action="store_true",
                      help="Fields are separated by a TAB, not by a comma")
    subp.add_argument('--dry-run', default=False, action="store_true",
                      help="Just show the result, do not actually insert data")
    subp.add_argument('config', help="Name of the configuration file")
    subp.add_argument('url',
                      help="URL from where historic CSV data will be loaded."
                      " It may also be a file:// URI")
    subp.set_defaults(func=load_historical_rating)

    subp = subparsers.add_parser('start-sound',
                                 help=start_sound.__doc__)
    subp.add_argument('sound', help="Name of the new OGG sound file")
    subp.set_defaults(func=start_sound)

    subp = subparsers.add_parser('stop-sound',
                                 help=stop_sound.__doc__)
    subp.add_argument('sound', help="Name of the new OGG sound file")
    subp.set_defaults(func=stop_sound)

    subp = subparsers.add_parser('prealarm-sound',
                                 help=prealarm_sound.__doc__)
    subp.add_argument('sound', help="Name of the new OGG sound file")
    subp.set_defaults(func=prealarm_sound)

    args = parser.parse_args()
    sys.exit(args.func(args) if hasattr(args, 'func') else 0)


if __name__ == '__main__':
    main()
