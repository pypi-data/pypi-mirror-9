"""cubicweb-datacat unit tests for hooks"""

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC

from utils import create_file


class DataProcessWorkflowHooksTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            ds = cnx.create_entity('Dataset', identifier=u'ds')
            cnx.commit()
            self.dataset_eid = ds.eid

    def _setup_and_start_dataprocess(self, cnx, process_etype, scriptcode):
        inputfile = create_file(cnx, 'data', resource_of=self.dataset_eid)
        script = cnx.create_entity('Script',
                                   name=u'%s script' % process_etype)
        create_file(cnx, scriptcode, reverse_implemented_by=script.eid)
        process = cnx.create_entity(process_etype,
                                    process_script=script)
        cnx.commit()
        process.cw_clear_all_caches()
        pstate = process.in_state[0]
        iprocess = process.cw_adapt_to('IDataProcess')
        self.assertEqual(process.in_state[0].name,
                         iprocess.state_name('initialized'))
        process.cw_set(process_input_file=inputfile)
        cnx.commit()
        process.cw_clear_all_caches()
        return process

    def test_data_process_autostart(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('Script', name=u'v')
            create_file(cnx, '1/0', reverse_implemented_by=script)
            process = cnx.create_entity('DataValidationProcess',
                                        process_script=script)
            cnx.commit()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_initialized')
            inputfile = create_file(cnx, 'data',
                                    resource_of=self.dataset_eid)
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_error')

    def test_data_process(self):
        with self.admin_access.repo_cnx() as cnx:
            for ptype in ('transformation', 'validation'):
                etype = 'Data' + ptype.capitalize() + 'Process'
                process = self._setup_and_start_dataprocess(cnx, etype, 'pass')
                self.set_description('test_data_%s_process: valid' % ptype)
                yield (self.assertEqual, process.in_state[0].name,
                       'wfs_dataprocess_completed')
                process.cw_delete()
                cnx.commit()
                self.set_description('test_data_%s_process: invalid' % ptype)
                process = self._setup_and_start_dataprocess(cnx, etype, '1/0')
                yield (self.assertEqual, process.in_state[0].name,
                       'wfs_dataprocess_error')

    def test_data_process_output(self):
        with self.admin_access.repo_cnx() as cnx:
            process = self._setup_and_start_dataprocess(
                cnx, 'DataTransformationProcess',
                open(self.datapath('cat.py')).read())
            script_eid = process.process_script[0].eid
            rset = cnx.execute(
                'Any X WHERE EXISTS(X produced_from O, X produced_by S)')
            self.assertEqual(len(rset), 1)
            stdout = rset.get_entity(0, 0)
            self.set_description('check output file content')
            self.assertEqual(stdout.read(), 'data\n')

    def test_data_validation_process_validated_by(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('Script', name=u'v')
            create_file(cnx, 'pass', reverse_implemented_by=script)
            process = cnx.create_entity('DataValidationProcess',
                                        process_script=script)
            cnx.commit()
            inputfile = create_file(cnx, 'data',
                                    resource_of=self.dataset_eid)
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_completed')
            validated = cnx.find('File', validated_by=script.eid).one()
            self.assertEqual(validated, inputfile)

    def test_data_process_dependency(self):
        """Check data processes dependency"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = cnx.create_entity('Script', name=u'v')
            create_file(cnx, 'pass', reverse_implemented_by=vscript)
            vprocess = cnx.create_entity('DataValidationProcess',
                                         process_script=vscript)
            tscript = cnx.create_entity('Script', name=u't')
            create_file(cnx,
                        ('import sys;'
                         'sys.stdout.write(open(sys.argv[1]).read())'),
                        reverse_implemented_by=tscript)
            tprocess = cnx.create_entity('DataTransformationProcess',
                                         process_depends_on=vprocess,
                                         process_script=tscript)
            cnx.commit()
            inputfile = create_file(cnx, 'data',
                                    resource_of=self.dataset_eid)
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_completed'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_completed')
            rset = cnx.find('File', produced_by=tscript)
            self.assertEqual(len(rset), 1, rset)
            output = rset.one()
            self.assertEqual(output.read(), inputfile.read())

    def test_data_process_dependency_validation_error(self):
        """Check data processes dependency: validation process error"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = cnx.create_entity('Script', name=u'v')
            create_file(cnx, '1/0', reverse_implemented_by=vscript)
            vprocess = cnx.create_entity('DataValidationProcess',
                                         process_script=vscript)
            tscript = cnx.create_entity('Script', name=u't')
            create_file(cnx, 'import sys; print open(sys.argv[1]).read()',
                        reverse_implemented_by=tscript)
            tprocess = cnx.create_entity('DataTransformationProcess',
                                         process_depends_on=vprocess,
                                         process_script=tscript)
            cnx.commit()
            inputfile = create_file(cnx, 'data',
                                    resource_of=self.dataset_eid)
            # Triggers "start" transition.
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_error'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_initialized')



class ResourceFeedHooksTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            ds = cnx.create_entity('Dataset', identifier=u'ds')
            cnx.commit()
            self.dataset_eid = ds.eid

    def test_resourcefeed_cwsource(self):
        with self.admin_access.repo_cnx() as cnx:
            resourcefeed = cnx.create_entity(
                'ResourceFeed', uri=u'a/b/c',
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            source = resourcefeed.resource_feed_source[0]
            self.set_description('check entity creation')
            yield self.assertEqual, source.url, resourcefeed.uri
            self.set_description('check entity update')
            resourcefeed.cw_set(uri=u'c/b/a')
            cnx.commit()
            source.cw_clear_all_caches()
            yield self.assertEqual, source.url, u'c/b/a'
            resourcefeed1 = cnx.create_entity(
                'ResourceFeed', uri=u'c/b/a',
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            self.assertEqual(resourcefeed1.resource_feed_source[0].eid,
                             source.eid)

    def test_linkto_dataset(self):
        with self.admin_access.repo_cnx() as cnx:
            inputfile = create_file(cnx, 'data')
            script = cnx.create_entity('Script', name=u'script')
            create_file(cnx, 'pass', reverse_implemented_by=script.eid)
            cnx.create_entity(
                'ResourceFeed', uri=u'a/b/c',
                resource_feed_of=self.dataset_eid,
                transformation_script=script)
            cnx.commit()
            # Build a transformation process "by hand".
            process = cnx.create_entity('DataTransformationProcess',
                                        process_input_file=inputfile,
                                        process_script=script)
            cnx.commit()
            iprocess = process.cw_adapt_to('IDataProcess')
            # Add `produced_by` relation.
            with cnx.security_enabled(write=False):
                outfile = iprocess.build_output(inputfile, 'plop')
                cnx.commit()
            rset = cnx.execute('Any X WHERE X resource_of D, D eid %s' %
                               self.dataset_eid)
            self.assertEqual(len(rset), 1, rset)
            outdata = rset.get_entity(0, 0).read()
            self.assertEqual(outdata, 'plop')



if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
