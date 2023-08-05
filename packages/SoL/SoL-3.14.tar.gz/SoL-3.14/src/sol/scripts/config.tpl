# -*- mode: conf; coding: utf-8 -*-
# SoL production configuration

[app:main]
use = egg:sol

####################
# Desktop settings #
####################

desktop.title = SoL
desktop.debug = false
desktop.domain = sol-client

available_languages = it fr en en_US

mako.directories = sol:views

pyramid.reload_templates = false
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en
pyramid.includes =
    pyramid_tm
    metapensiero.sqlalchemy.proxy.pyramid

session.secret = {secret}
# Sessions maximum age in seconds, None means unlimited
session.timeout = None
session.reissue_time = None

##############################
# Database kind and location #
##############################

sqlalchemy.url = sqlite:///%(here)s/SoL.sqlite

######################
# SoL Authentication #
######################

sol.admin.user = admin
sol.admin.password = {password}
#sol.guest.user = guest
#sol.guest.password = guest

# Directories containing players portraits and clubs emblems
sol.portraits_dir = %(here)s/portraits
sol.emblems_dir = %(here)s/emblems

# Directory used for automatic backups, "None" to disable
sol.backups_dir = %(here)s/backups

###########
# Alembic #
###########

# Path to migration scripts
script_location = {alembicdir}

# Template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# Max length of characters to apply to the
# "slug" field
#truncate_slug_length = 40

# Set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = 6996

#########################
# Logging configuration #
#########################

[loggers]
keys = root, sol, sqlalchemy

[handlers]
keys = file

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = file

[logger_sol]
level = WARN
handlers =
qualname = sol

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
# "level = INFO" logs SQL queries.
# "level = DEBUG" logs SQL queries and results.
# "level = WARN" logs neither.  (Recommended for production systems.)

[handler_file]
class = FileHandler
args = ('sol.log', 'a', 'utf-8')
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s] %(message)s
