"""cubicweb-datacat unit tests for entities"""

from cubicweb.devtools.testlib import CubicWebTC

from utils import create_file


class IDataProcessTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            ds = cnx.create_entity('Dataset', identifier=u'ds')
            s = cnx.create_entity('Script', name=u's')
            create_file(cnx, 'pass', reverse_implemented_by=s)
            cnx.commit()
            self.dataset_eid = ds.eid
            self.script_eid = s.eid

    def _create_process(self, cnx, etype, **kwargs):
        kwargs.setdefault('process_script', self.script_eid)
        return cnx.create_entity(etype, **kwargs)

    def test_process_type(self):
        with self.admin_access.repo_cnx() as cnx:
            for etype, ptype in [('DataTransformationProcess', 'transformation'),
                                 ('DataValidationProcess', 'validation')]:
                p = self._create_process(cnx, etype)
                cnx.commit()
                self.assertEqual(p.cw_adapt_to('IDataProcess').process_type,
                                 ptype)

    def test_state_name(self):
        with self.admin_access.repo_cnx() as cnx:
            p = self._create_process(cnx, 'DataValidationProcess')
            cnx.commit()
            idataprocess = p.cw_adapt_to('IDataProcess')
            self.assertEqual(idataprocess.state_name('error'),
                             'wfs_dataprocess_error')
            with self.assertRaises(ValueError) as cm:
                idataprocess.state_name('blah')
            self.assertIn('invalid state name', str(cm.exception))

    def test_tr_name(self):
        with self.admin_access.repo_cnx() as cnx:
            p = self._create_process(cnx, 'DataTransformationProcess')
            cnx.commit()
            idataprocess = p.cw_adapt_to('IDataProcess')
            self.assertEqual(idataprocess.tr_name('start'),
                             'wft_dataprocess_start')
            with self.assertRaises(ValueError) as cm:
                idataprocess.tr_name('blah')
            self.assertIn('invalid transition name', str(cm.exception))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

