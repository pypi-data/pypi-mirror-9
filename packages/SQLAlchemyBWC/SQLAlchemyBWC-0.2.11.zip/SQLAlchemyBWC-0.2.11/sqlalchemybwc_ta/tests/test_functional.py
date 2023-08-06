from blazeutils.strings import randchars
from blazeweb.globals import ag, settings
from blazeweb.tasks import run_tasks
from blazeweb.testing import TestApp
import datetime as dt
from nose.plugins.skip import SkipTest
from nose.tools import eq_
import sqlalchemy as sa
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemybwc import db

from sqlalchemybwc_ta.application import make_wsgi
from sqlalchemybwc_ta.model.orm import Car

class TestTemplates(object):

    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)
        Car.delete_all()
        Car.add(**{
            'make': u'chevy',
            'model': u'cav',
            'year': 2010
        })

    def test_index(self):
        r = self.ta.get('/')
        assert 'Index Page' in r

    def test_one_db_session(self):
        c = Car.first()
        assert c.make
        self.ta.get('/')
        try:
            assert c.make
            assert False, 'expected DetachedInstanceError'
        except DetachedInstanceError:
            pass

    def test_split_db_sessions(self):
        raise SkipTest
        """ something weird happens when this test runs in that
        test_model.py:TestFKs.test_fk_prevent_parent_update() fails
        when running against PGSQL (at least)
        """
        wsgiapp = make_wsgi('SplitSessionsTest')
        ta = TestApp(wsgiapp)
        run_tasks('clear-db')
        run_tasks('init-db:~test')
        r = ta.get('/')
        assert 'Index Page' in r

        c = Car.first()
        assert c.make
        ta.get('/')
        assert c.make

    def test_session_clear_beaker(self):
        # make beaker create a session table. Use the alternate profile to have
        #   a database file, instead of in-memory, where it will get wiped before
        #   we can check results
        wsgiapp = make_wsgi('BeakerSessionTest')
        ta = TestApp(wsgiapp)
        ta.get('/beaker-test')

        sessions_table = sa.Table(
            'beaker_cache',
            sa.MetaData(settings.beaker.url),
            autoload=True
        )
        sessions_table.delete().execute()
        for i in range(10):
            sessions_table.insert().values(
                namespace=randchars(20),
                created=dt.datetime.now(),
                accessed=(
                    dt.datetime.now() -
                    dt.timedelta(seconds=60*5*i)
                ),
                data='55'
            ).execute()
            
        eq_(
            db.sess.execute(
                sa.sql.select([sa.sql.func.count('*')], from_obj='beaker_cache')
            ).fetchone(),
            (10, )
        )

        # re-run the app to clear sessions    
        wsgiapp = make_wsgi('BeakerSessionTest')

        eq_(
            db.sess.execute(
                sa.sql.select([sa.sql.func.count('*')], from_obj='beaker_cache')
            ).fetchone(),
            (6, )
        )

        run_tasks('clear-db')
        run_tasks('init-db:~test')
