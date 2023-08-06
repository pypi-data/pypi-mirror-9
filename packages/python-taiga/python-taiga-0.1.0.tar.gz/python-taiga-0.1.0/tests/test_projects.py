from datetime import datetime
from taiga.requestmaker import RequestMaker
from taiga.models import User, Point, UserStoryStatus, Severity, Project, Projects
import unittest
from mock import patch
from taiga import TaigaAPI
from .tools import create_mock_json
from .tools import MockResponse


class TestProjects(unittest.TestCase):

    @patch('taiga.requestmaker.RequestMaker.get')
    def test_single_project_parsing(self, mock_requestmaker_get):
        mock_requestmaker_get.return_value = MockResponse(200,
            create_mock_json('tests/resources/project_details_success.json'))
        api = TaigaAPI(token='f4k3')
        project = api.projects.get(1)
        self.assertEqual(project.description, 'test 1 on real taiga')
        self.assertEqual(len(project.users), 1)
        self.assertTrue(isinstance(project.points[0], Point))
        self.assertTrue(isinstance(project.us_statuses[0], UserStoryStatus))
        self.assertTrue(isinstance(project.severities[0], Severity))

    @patch('taiga.requestmaker.RequestMaker.get')
    def test_list_projects_parsing(self, mock_requestmaker_get):
        mock_requestmaker_get.return_value = MockResponse(200,
            create_mock_json('tests/resources/projects_list_success.json'))
        api = TaigaAPI(token='f4k3')
        projects = api.projects.list()
        self.assertEqual(projects[0].description, 'test 1 on real taiga')
        self.assertEqual(len(projects), 1)
        self.assertEqual(len(projects[0].users), 1)
        self.assertTrue(isinstance(projects[0].users[0], User))

    @patch('taiga.requestmaker.RequestMaker.post')
    def test_star(self, mock_requestmaker_post):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        self.assertEqual(project.star().id, 1)
        mock_requestmaker_post.assert_called_with(
            '/{endpoint}/{id}/star',
            endpoint='projects', id=1
        )

    @patch('taiga.requestmaker.RequestMaker.post')
    def test_unstar(self, mock_requestmaker_post):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        self.assertEqual(project.unstar().id, 1)
        mock_requestmaker_post.assert_called_with(
            '/{endpoint}/{id}/unstar',
            endpoint='projects', id=1
        )

    @patch('taiga.models.base.ListResource._new_resource')
    def test_create_project(self, mock_new_resource):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        mock_new_resource.return_value = Project(rm)
        sv = Projects(rm).create('PR 1', 'PR desc 1')
        mock_new_resource.assert_called_with(
            payload={'name': 'PR 1', 'description': 'PR desc 1'}
        )

    @patch('taiga.models.IssueStatuses.create')
    def test_add_issue_status(self, mock_new_issue_status):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_issue_status('Issue 1')
        mock_new_issue_status.assert_called_with(1, 'Issue 1')

    @patch('taiga.models.IssueStatuses.list')
    def test_list_issue_statuses(self, mock_list_issue_statuses):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_issue_statuses()
        mock_list_issue_statuses.assert_called_with(project=1)

    @patch('taiga.models.Priorities.create')
    def test_add_priority(self, mock_new_priority):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_priority('Priority 1')
        mock_new_priority.assert_called_with(1, 'Priority 1')

    @patch('taiga.models.Priorities.list')
    def test_list_priorities(self, mock_list_priorities):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_priorities()
        mock_list_priorities.assert_called_with(project=1)

    @patch('taiga.models.Severities.create')
    def test_add_severity(self, mock_new_severity):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_severity('Severity 1')
        mock_new_severity.assert_called_with(1, 'Severity 1')

    @patch('taiga.models.Severities.list')
    def test_list_severities(self, mock_list_severities):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_severities()
        mock_list_severities.assert_called_with(project=1)

    @patch('taiga.models.models.IssueTypes.create')
    def test_add_issue_type(self, mock_new_issue_type):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_issue_type('Severity 1')
        mock_new_issue_type.assert_called_with(1, 'Severity 1')

    @patch('taiga.models.models.IssueTypes.list')
    def test_list_issue_types(self, mock_list_issue_types):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_issue_types()
        mock_list_issue_types.assert_called_with(project=1)

    @patch('taiga.models.UserStoryStatuses.create')
    def test_add_us_status(self, mock_new_us_status):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_user_story_status('US status 1')
        mock_new_us_status.assert_called_with(1, 'US status 1')

    @patch('taiga.models.UserStoryStatuses.list')
    def test_list_us_statuses(self, mock_list_us_statuses):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_user_story_statuses()
        mock_list_us_statuses.assert_called_with(project=1)

    @patch('taiga.models.TaskStatuses.create')
    def test_add_task_status(self, mock_new_task_status):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_task_status('Task status 1')
        mock_new_task_status.assert_called_with(1, 'Task status 1')

    @patch('taiga.models.TaskStatuses.list')
    def test_list_task_statuses(self, mock_list_task_statuses):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_task_statuses()
        mock_list_task_statuses.assert_called_with(project=1)

    @patch('taiga.models.Points.create')
    def test_add_point(self, mock_new_point):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_point('Point 1', 1.5)
        mock_new_point.assert_called_with(1, 'Point 1', 1.5)

    @patch('taiga.models.Points.list')
    def test_list_points(self, mock_list_points):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_points()
        mock_list_points.assert_called_with(project=1)

    @patch('taiga.models.Milestones.create')
    def test_add_milestone(self, mock_new_milestone):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        time1 = datetime.now()
        time2 = datetime.now()
        project.add_milestone('Milestone 1', time1, time2)
        mock_new_milestone.assert_called_with(1, 'Milestone 1', time1, time2)

    @patch('taiga.models.Milestones.list')
    def test_list_milestones(self, mock_list_milestones):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_milestones()
        mock_list_milestones.assert_called_with(project=1)

    @patch('taiga.models.Issues.create')
    def test_add_issue(self, mock_new_issue):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_issue('Issue 1', 1, 2, 3, 4)
        mock_new_issue.assert_called_with(1, 'Issue 1', 1, 2, 3, 4)

    @patch('taiga.models.Issues.list')
    def test_list_issues(self, mock_list_issues):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_issues()
        mock_list_issues.assert_called_with(project=1)

    @patch('taiga.models.UserStories.create')
    def test_add_userstory(self, mock_new_userstory):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_user_story('US 1')
        mock_new_userstory.assert_called_with(1, 'US 1')

    @patch('taiga.models.UserStories.list')
    def test_list_userstories(self, mock_list_userstories):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_user_stories()
        mock_list_userstories.assert_called_with(project=1)

    @patch('taiga.models.WikiPages.create')
    def test_add_wikipage(self, mock_new_wikipage):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_wikipage('WP 1', 'Content')
        mock_new_wikipage.assert_called_with(1, 'WP 1', 'Content')

    @patch('taiga.models.WikiPages.list')
    def test_list_wikipages(self, mock_list_wikipages):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_wikipages()
        mock_list_wikipages.assert_called_with(project=1)

    @patch('taiga.models.WikiLinks.create')
    def test_add_wikilink(self, mock_new_wikilink):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.add_wikilink('WL 1', 'href')
        mock_new_wikilink.assert_called_with(1, 'WL 1', 'href')

    @patch('taiga.models.WikiLinks.list')
    def test_list_wikilinks(self, mock_list_wikilinks):
        rm = RequestMaker('/api/v1', 'fakehost', 'faketoken')
        project = Project(rm, id=1)
        project.list_wikilinks()
        mock_list_wikilinks.assert_called_with(project=1)
