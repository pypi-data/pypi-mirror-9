from datetime import datetime

import mock

from springboard.tests.base import SpringboardTestCase


class TestEvents(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.app = self.mk_app(self.workspace, settings={
            'ga.profile_id': 'UA-some-id',
        })

    @mock.patch('unicore.google.tasks.pageview.delay')
    def test_ga_pageviews(self, mock_task):
        [category] = self.mk_categories(self.workspace, count=1)
        [page] = self.mk_pages(self.workspace, count=1,
                               primary_category=category.uuid,
                               created_at=datetime.now().isoformat())
        self.workspace.save(page, 'Add page')
        self.workspace.refresh_index()

        self.app.get('/', status=200, extra_environ={
            'HTTP_HOST': 'some.site.com',
            'REMOTE_ADDR': '192.0.0.1',
        })
        mock_task.assert_called_once()
        ((profile_id, gen_client_id, data), _) = mock_task.call_args_list[0]
        self.assertEqual(profile_id, 'UA-some-id')
        self.assertEqual(data['path'], '/')
        self.assertEqual(data['uip'], '192.0.0.1')
        self.assertEqual(data['dh'], 'some.site.com')
        self.assertEqual(data['dr'], '')

        page_url = '/page/%s/' % page.uuid
        headers = {
            'User-agent': 'Mozilla/5.0',
        }
        self.app.get(page_url, status=200, headers=headers, extra_environ={
            'HTTP_REFERER': '/',
            'HTTP_HOST': 'some.site.com',
            'REMOTE_ADDR': '192.0.0.1',
        })
        ((profile_id, client_id, data), _) = mock_task.call_args_list[1]

        self.assertEqual(profile_id, 'UA-some-id')
        self.assertEqual(data['path'], page_url)
        self.assertEqual(data['dr'], '/')
        self.assertEqual(data['uip'], '192.0.0.1')
        self.assertEqual(data['dh'], 'some.site.com')
        self.assertEqual(data['user_agent'], 'Mozilla/5.0')

        # # ensure cid is the same across calls
        self.assertEqual(gen_client_id, client_id)
