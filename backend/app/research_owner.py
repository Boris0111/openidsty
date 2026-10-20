"""Local interactive owner setup/reset. Never accept a password in arguments or env."""
import argparse
import getpass
import sys
from sqlalchemy import text
from .research_auth import HASHER, utc_now
from .research_db import writer_engine


def set_owner(connection, password, *, reset=False):
    if not isinstance(password, str) or not 12 <= len(password) or len(password.encode()) > 1024:
        raise ValueError('Password must have at least 12 characters and at most 1024 UTF-8 bytes')
    encoded = HASHER.hash(password)
    connection.execute(text('SELECT pg_advisory_xact_lock(8604141)'))
    owner = connection.execute(text('SELECT credential_version FROM research.admin_owner WHERE singleton FOR UPDATE')).scalar_one_or_none()
    if (owner is not None) != reset:
        raise ValueError('Use reset for an existing owner, or setup for a new installation')
    if reset:
        connection.execute(text('''UPDATE research.admin_owner SET password_hash=:hash,
            credential_version=credential_version+1,changed_at=:now WHERE singleton'''), {'hash': encoded, 'now': utc_now()})
        connection.execute(text('UPDATE research.admin_sessions SET revoked_at=:now WHERE revoked_at IS NULL'), {'now': utc_now()})
        connection.execute(text('DELETE FROM research.login_attempts'))
    else:
        connection.execute(text('INSERT INTO research.admin_owner(singleton,password_hash,credential_version) VALUES(true,:hash,1)'), {'hash': encoded})
    connection.execute(text('''INSERT INTO research.audit_log(actor,operation,detail)
        VALUES ('local-cli',:operation,'{}')'''), {'operation': 'owner-reset' if reset else 'owner-setup'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup', 'reset'])
    args = parser.parse_args()
    if not sys.stdin.isatty():
        raise SystemExit('Run in an interactive terminal; passwords are never read from pipes or environment')
    password = getpass.getpass('Owner password (at least 12 characters): ')
    if password != getpass.getpass('Repeat password: '):
        raise SystemExit('Passwords do not match; owner unchanged')
    try:
        with writer_engine().begin() as connection:
            set_owner(connection, password, reset=args.action == 'reset')
    except ValueError as error:
        raise SystemExit(str(error)) from None
    print('Owner credential saved; no password or hash displayed')


if __name__ == '__main__':
    main()
