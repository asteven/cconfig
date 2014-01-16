# dumped from cdist.test.object

    # FIXME: actually testing fsproperty.DirectoryDictProperty here, move to their own test case
    def test_explorers_assign_dict(self):
        expected = {'first': 'foo', 'second': 'bar'}
        # when set, written to file
        self.cdist_object.explorers = expected
        object_explorer_path = os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path)
        self.assertTrue(os.path.isdir(object_explorer_path))
        # when accessed, read from file
        self.assertEqual(self.cdist_object.explorers, expected)
        # remove dynamically created folder
        self.cdist_object.explorers = {}
        os.rmdir(os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path))

    # FIXME: actually testing fsproperty.DirectoryDictProperty here, move to their own test case
    def test_explorers_assign_key_value(self):
        expected = {'first': 'foo', 'second': 'bar'}
        object_explorer_path = os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path)
        for key,value in expected.items():
            # when set, written to file
            self.cdist_object.explorers[key] = value
            self.assertTrue(os.path.isfile(os.path.join(object_explorer_path, key)))
        # when accessed, read from file
        self.assertEqual(self.cdist_object.explorers, expected)
        # remove dynamically created folder
        self.cdist_object.explorers = {}
        os.rmdir(os.path.join(self.cdist_object.base_path, self.cdist_object.explorer_path))

    def test_requirements(self):
        expected = []
        self.assertEqual(list(self.cdist_object.requirements), expected)

    def test_changed(self):
        self.assertFalse(self.cdist_object.changed)

    def test_changed_after_changing(self):
        self.cdist_object.changed = True
        self.assertTrue(self.cdist_object.changed)

    def test_state(self):
        self.assertEqual(self.cdist_object.state, '')

    def test_state_prepared(self):
        self.cdist_object.state = core.CdistObject.STATE_PREPARED
        self.assertEqual(self.cdist_object.state, core.CdistObject.STATE_PREPARED)

    def test_state_running(self):
        self.cdist_object.state = core.CdistObject.STATE_RUNNING
        self.assertEqual(self.cdist_object.state, core.CdistObject.STATE_RUNNING)

    def test_state_done(self):
        self.cdist_object.state = core.CdistObject.STATE_DONE
        self.assertEqual(self.cdist_object.state, core.CdistObject.STATE_DONE)

    def test_source(self):
        self.assertEqual(list(self.cdist_object.source), [])

    def test_source_after_changing(self):
        self.cdist_object.source = ['/path/to/manifest']
        self.assertEqual(list(self.cdist_object.source), ['/path/to/manifest'])

    def test_code_local(self):
        import cconfig
        import pprint
        pprint.pprint(self.cdist_object)
        pprint.pprint(cconfig.Cconfig.__repr__(self.cdist_object))
        self.assertIsNone(self.cdist_object.code_local)

    def test_code_local_after_changing(self):
        self.cdist_object.code_local = 'Hello World'
        self.assertEqual(self.cdist_object.code_local, 'Hello World')

    def test_code_remote(self):
        self.assertEqual(self.cdist_object.code_remote, '')

    def test_code_remote_after_changing(self):
        self.cdist_object.code_remote = 'Hello World'
        self.assertEqual(self.cdist_object.code_remote, 'Hello World')
