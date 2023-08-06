"""cubicweb-datacat unit tests for server objects"""

import tempfile

from cubicweb.devtools.testlib import CubicWebTC

from utils import create_file


class ResourceFeedParserTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            ds = cnx.create_entity('Dataset', identifier=u'ds')
            cnx.commit()
            self.dataset_eid = ds.eid

    def pull_data(self, cwsource):
        """Pull data from a CWSource associated with a ResourceFeed"""
        dfsource = self.repo.sources_by_eid[cwsource.eid]
        with self.repo.internal_cnx() as icnx:
            stats = dfsource.pull_data(icnx, force=True, raise_on_error=True)
            icnx.commit()
        return stats

    def test_base(self):
        uri = u'file://' + self.datapath('resource.dat')
        with self.admin_access.repo_cnx() as cnx:
            resourcefeed = cnx.create_entity(
                'ResourceFeed', uri=uri,
                data_format=u'text/csv',
                resource_feed_of=self.dataset_eid)
            cnx.commit()
        cwsource = resourcefeed.resource_feed_source[0]
        stats = self.pull_data(cwsource)
        yield self.assertEqual, len(stats['created']), 1
        feid = stats['created'].pop()
        with self.admin_access.repo_cnx() as cnx:
            f = cnx.entity_from_eid(feid)
            self.assertEqual(f.data_name, 'resource.dat')
            self.assertEqual(f.data_format, 'text/csv')
        self.set_description('second pull, no update of sha1')
        stats = self.pull_data(cwsource)
        yield self.assertEqual, len(stats['created']), 0

    def test_with_processes(self):
        uri = u'file://' + self.datapath('resource.dat')
        with self.admin_access.repo_cnx() as cnx:
            # Validation script.
            vscript_eid = cnx.create_entity(
                'Script', name=u'validation script',
                accepted_format=u'text/csv').eid
            create_file(cnx, 'pass', reverse_implemented_by=vscript_eid)
            # Transformation script.
            tscript_eid = cnx.create_entity(
                'Script', name=u'transformation script',
                accepted_format=u'text/csv').eid
            create_file(cnx, open(self.datapath('cat.py')).read(),
                        data_name=u'cat.py',
                        reverse_implemented_by=tscript_eid)
            # Create resource feed.
            resourcefeed = cnx.create_entity(
                'ResourceFeed', uri=uri,
                data_format=u'text/csv',
                resource_feed_of=self.dataset_eid,
                validation_script=vscript_eid,
                transformation_script=tscript_eid)
            cnx.commit()
        cwsource = resourcefeed.resource_feed_source[0]
        stats = self.pull_data(cwsource)
        assert len(stats['created']) == 1
        feid = stats['created'].pop()
        with self.admin_access.repo_cnx() as cnx:
            rset = cnx.find('DataTransformationProcess',
                            process_for_resourcefeed=resourcefeed.eid)
            process = rset.one()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_completed')
            # There should be one result.
            output = cnx.find('File', produced_from=feid,
                              produced_by=tscript_eid).one()
            self.assertEqual([r.eid for r in output.resource_of],
                             [self.dataset_eid])

    def test_file_update(self):
        """Update a file between two datafeed pulls"""
        with tempfile.NamedTemporaryFile() as tmpf:
            tmpf.write('coucou')
            tmpf.flush()
            with self.admin_access.repo_cnx() as cnx:
                vscript_eid = cnx.create_entity(
                    'Script', name=u'validation script').eid
                create_file(cnx, 'pass',
                            reverse_implemented_by=vscript_eid)
                # Transformation script and process.
                tscript_eid = cnx.create_entity(
                    'Script', name=u'transformation script').eid
                create_file(cnx, open(self.datapath('reverse.py')).read(),
                            data_name=u'reverse',
                            reverse_implemented_by=tscript_eid)
                resourcefeed = cnx.create_entity(
                    'ResourceFeed', uri=u'file://' + tmpf.name,
                    validation_script=vscript_eid,
                    transformation_script=tscript_eid,
                    resource_feed_of=self.dataset_eid)
                cnx.commit()
            cwsource = resourcefeed.resource_feed_source[0]
            stats = self.pull_data(cwsource)
            self.assertEqual(len(stats['created']), 1, stats)
            feid = stats['created'].pop()
            self.set_description('first pull')
            expected = {'content': 'uocuoc\n', 'validated_by': [feid],
                        'produced_by': 1}
            yield (self._check_datafeed_output, feid, vscript_eid,
                   tscript_eid, expected)
            # Change input file.
            tmpf.write('\nau revoir')
            tmpf.flush()
            stats = self.pull_data(cwsource)
            self.assertEqual(len(stats['created']), 1)
            feid_ = stats['created'].pop()
            self.set_description('second pull: change input')
            expected = {'content': 'riover ua\nuocuoc\n',
                        'validated_by': [feid, feid_],
                        'produced_by': 2}
            yield (self._check_datafeed_output, feid_, vscript_eid,
                   tscript_eid, expected)
            # Pull one more time, without changing the source.
            self.set_description('third pull: no change')
            stats = self.pull_data(cwsource)
            for k, v in stats.iteritems():
                self.assertFalse(v, '%s: %r' % (k, v))
            # `expected` has not changed.
            yield (self._check_datafeed_output, feid_, vscript_eid,
                   tscript_eid, expected)

    def _check_datafeed_output(self, feid, vscript_eid, tscript_eid, expected):
        with self.admin_access.repo_cnx() as cnx:
            output = cnx.find('File', produced_from=feid).one()
            if 'content' in expected:
                self.assertEqual(output.read(), expected['content'])
            if 'validated_by' in expected:
                validated = expected['validated_by']
                rset = cnx.find('File', validated_by=vscript_eid)
                self.assertEqual(len(rset), len(validated), rset)
                self.assertCountEqual([x[0] for x in rset.rows], validated)
            if 'produced_by' in expected:
                nproduced = expected['produced_by']
                rset = cnx.find('File', produced_by=tscript_eid)
                self.assertEqual(len(rset), nproduced, rset)

    def test_multiple_resourcefeed_same_url(self):
        uri = u'file://' + self.datapath('resource.dat')
        with self.admin_access.repo_cnx() as cnx:
            # Transformation scripts.
            tscript = cnx.create_entity(
                'Script', name=u'transformation script',
                accepted_format=u'text/plain')
            create_file(cnx, 'print "coucou"',
                        reverse_implemented_by=tscript)
            tscript_eid = cnx.create_entity(
                'Script', name=u'transformation script',
                accepted_format=u'text/csv').eid
            create_file(cnx, open(self.datapath('cat.py')).read(),
                        data_name=u'cat.py',
                        reverse_implemented_by=tscript_eid)
            # Resource feeds.
            resource1 = cnx.create_entity(
                'ResourceFeed', uri=uri,
                data_format=u'text/csv',
                resource_feed_of=self.dataset_eid,
                transformation_script=tscript_eid)
            cnx.commit()
            cwsource = resource1.resource_feed_source[0]
            resource2 = cnx.create_entity(
                'ResourceFeed', uri=uri,
                data_format=u'text/plain',
                resource_feed_of=self.dataset_eid,
                transformation_script=tscript)
            cnx.commit()
            assert resource2.resource_feed_source[0] == cwsource
            assert len(cwsource.reverse_resource_feed_source), 2
            self.set_description('check MIME type compatibility')
            yield self._check_value_error, cwsource
            self.set_description('check transformations')
            tscript.cw_set(accepted_format=u'text/csv')
            resource2.cw_set(data_format=u'text/csv')
            cnx.commit()
            stats = self.pull_data(cwsource)
            yield self._check_transformations, cnx, stats

    def _check_value_error(self, cwsource):
        with self.assertRaises(ValueError) as cm:
            self.pull_data(cwsource)
        self.assertIn('MIME types of resource feeds attached',
                      str(cm.exception))

    def _check_transformations(self, cnx, stats):
        # Check both data processes have completed.
        rset = cnx.execute(
            'DataTransformationProcess X WHERE X in_state ST,'
            ' ST name "wfs_dataprocess_completed"')
        self.assertEqual(len(rset), 2)
        # Check resources and produced files.
        self.assertEqual(
            cnx.execute('Any COUNT(X)WHERE X resource_of D')[0][0], 3)
        self.assertEqual(len(stats['created']), 1, stats)
        feid = stats['created'].pop()
        rset = cnx.find('File', produced_from=feid)
        self.assertEqual(len(rset), 2, rset)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
