import os
import shutil
from StringIO import StringIO

from springboard.tests import SpringboardTestCase
from springboard.tools.commands import (
    CloneRepoTool, CreateIndexTool, CreateMappingTool, SyncDataTool,
    BootstrapTool)


class SpringboardToolTestCase(SpringboardTestCase):

    def mk_workspace_name(self, workspace):
        return os.path.basename(workspace.working_dir)

    def mk_workspace_config(self, workspace):
        repo_name = self.mk_workspace_name(self.workspace)
        return {
            'repositories': {
                repo_name: self.workspace.working_dir,
            }
        }


class TestCloneRepoTool(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_clone_repo(self):
        self.addCleanup(lambda: shutil.rmtree(self.working_dir))
        tool = CloneRepoTool()
        tool.stdout = StringIO()
        tool.run(
            config=self.mk_workspace_config(self.workspace),
            verbose=True,
            clobber=False,
            repo_dir='%s/test_clone_repo' % (self.working_dir,),
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.startswith('Cloning'))
        self.assertTrue(output.endswith('test_clone_repo.\n'))

        tool.run(
            config=self.mk_workspace_config(self.workspace),
            verbose=True,
            clobber=False,
            repo_dir='%s/test_clone_repo' % (self.working_dir,),
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('already exists, skipping.\n'))

        tool.run(
            config=self.mk_workspace_config(self.workspace),
            verbose=True,
            clobber=True,
            repo_dir='%s/test_clone_repo' % (self.working_dir,),
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('Clobbering existing repository.\n'))


class TestCreateIndex(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.repo = self.workspace.repo

    def test_create_index(self):
        tool = CreateIndexTool()
        tool.stdout = StringIO()
        tool.run(
            config=self.mk_workspace_config(self.workspace),
            verbose=True,
            clobber=False,
            repo_dir=self.workspace.working_dir,
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('Index already exists, skipping.\n'))

        tool.run(
            config=self.mk_workspace_config(self.workspace),
            verbose=True,
            clobber=True,
            repo_dir=self.workspace.working_dir,
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(
            output.endswith('Clobbering existing index.\nIndex created.\n'))


class TestCreateMapping(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        CreateIndexTool().create_index(self.workspace.working_dir)

    def test_create_mapping(self):
        tool = CreateMappingTool()
        tool.stdout = StringIO()

        config = self.mk_workspace_config(self.workspace)
        config['models'] = {
            'elasticgit.tests.base.TestPerson': {
                'properties': {
                    'name': {
                        'index': 'not_analyzed',
                        'type': 'string',
                    }
                }
            }
        }

        tool.run(config=config,
                 verbose=True,
                 clobber=False,
                 repo_dir=self.workspace.working_dir,
                 repo_name=self.mk_workspace_name(self.workspace))
        self.assertEqual(
            tool.stdout.getvalue(),
            'Creating mapping for elasticgit.tests.base.TestPerson.\n'
            'Mapping created.\n')


class TestSyncData(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        CreateIndexTool().create_index(self.workspace.working_dir)

    def test_sync_data(self):
        tool = SyncDataTool()
        tool.stdout = StringIO()

        config = self.mk_workspace_config(self.workspace)
        config['models'] = {
            'elasticgit.tests.base.TestPerson': {
                'properties': {
                    'name': {
                        'index': 'not_analyzed',
                        'type': 'string',
                    }
                }
            }
        }

        tool.run(config=config,
                 verbose=True,
                 clobber=False,
                 repo_dir=self.workspace.working_dir,
                 repo_name=self.mk_workspace_name(self.workspace))
        self.assertEqual(
            tool.stdout.getvalue(),
            'Syncing data for elasticgit.tests.base.TestPerson.\n'
            'Data synced.\n')


class TestBootstrapTool(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_bootstrap(self):
        tool = BootstrapTool()
        tool.stdout = StringIO()

        config = self.mk_workspace_config(self.workspace)
        config['models'] = {
            'elasticgit.tests.base.TestPerson': {
                'properties': {
                    'name': {
                        'index': 'not_analyzed',
                        'type': 'string',
                    }
                }
            }
        }

        tool.run(config=config,
                 verbose=True,
                 clobber=False,
                 repo_dir=self.working_dir)

        lines = tool.stdout.getvalue().split('\n')
        self.assertTrue(lines[0].startswith('Cloning'))
        self.assertTrue(
            lines[0].endswith(
                '%s.' % (self.mk_workspace_name(self.workspace))))
        self.assertEqual(lines[1], 'Destination already exists, skipping.')
        self.assertEqual(lines[2], 'Creating index for master.')
        self.assertEqual(lines[3], 'Index already exists, skipping.')
