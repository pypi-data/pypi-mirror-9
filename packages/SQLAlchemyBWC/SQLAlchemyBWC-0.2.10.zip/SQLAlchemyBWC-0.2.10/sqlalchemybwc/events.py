from blazeweb.events import signal
from blazeweb.globals import settings
from blazeweb.tasks import run_tasks


def setup_db_structure(sender):
    if settings.components.sqlalchemy.pre_test_init_tasks:
        run_tasks(settings.components.sqlalchemy.pre_test_init_tasks)
signal('blazeweb.pre_test_init').connect(setup_db_structure)


def clear_old_beaker_sessions(sender):
    # clear up old beaker sessions, if needed
    if (
        settings.beaker.enabled and 
        settings.beaker.auto_clear_sessions and
        settings.beaker.type == 'ext:database'
    ):
        import datetime as dt
        import sqlalchemy as sa
        table_name = getattr(settings.beaker, 'table_name', 'beaker_cache')
        try:
            sessions_table = sa.Table(
                table_name,
                sa.MetaData(settings.beaker.url),
                autoload=True
            )
            count = sessions_table.delete(
                sessions_table.c.accessed < (
                    dt.datetime.now() -
                    dt.timedelta(seconds=settings.beaker.timeout)
                )
            ).execute()
        except sa.exc.NoSuchTableError:
            # depending on the database, a table may not be present (yet)
            #   so, no sessions to cleanup
            pass
signal('blazeweb.auto_actions.initialized').connect(clear_old_beaker_sessions)
