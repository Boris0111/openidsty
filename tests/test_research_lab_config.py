"""Compose never builds and every service runs the one commit-tagged image the script injects."""
import copy
import os
from pathlib import Path
import sys
import unittest
from unittest import mock
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import research_lab as lab

TAG = '0123456789ab'


def config(tag=TAG):
    """The shape `docker compose config --format json` gives for compose.research.yaml."""
    def url(user):
        return f'postgresql+psycopg://{user}:x@db:5432/industry_research'

    def app(user='industry', **extra):
        return {'image': f'industryflow-research-api:{tag}', **extra,
                'environment': {'DATABASE_URL': url(user), 'RESEARCH_READ_DATABASE_URL': url('research_reader_login'),
                                'RESEARCH_WRITE_DATABASE_URL': url('research_writer_login')}}

    def port(host, target):
        return [{'host_ip': '127.0.0.1', 'published': str(host), 'target': target}]
    return {'name': 'industryflow-research', 'services': {
        'db': {'image': 'postgres:16.15-trixie', 'volumes': [
            {'type': 'volume', 'source': 'pg-data'},
            {'type': 'bind', 'source': str(lab.ROOT / 'docker/research-init.sql'), 'read_only': True}]},
        'initialize': app(), 'api': app('research_reader_login', ports=port(8010, 8000)),
        'prefect': app(profiles=['scheduler'], ports=port(4201, 4200), restart='unless-stopped'),
        'deploy': app(profiles=['scheduler']),
        'worker': app('research_writer_login', profiles=['scheduler'], restart='unless-stopped'),
        'ingestion': app('research_writer_login', profiles=['tools']),
        'web': {'image': f'industryflow-research-web:{tag}', 'ports': port(3010, 3010)},
        'reader': {'image': f'industryflow-research-api:{tag}', 'profiles': ['reader'], 'read_only': True,
                   'cap_drop': ['ALL'], 'environment': {'READER_ALLOWED_HOSTS': '127.0.0.1:3015'},
                   'ports': port(3015, 8000)}},
        'volumes': {'pg-data': {'name': 'industryflow-research_pg-data'}},
        'networks': {'app': {'name': 'industryflow-research_app'}}}


class TagTests(unittest.TestCase):
    def test_valid_config_reports_the_tag(self):
        summary = lab.validate_config(config(), TAG)
        self.assertEqual(summary['tag'], TAG)
        self.assertEqual(summary['images'], ['industryflow-research-api:' + TAG, 'industryflow-research-web:' + TAG,
                                             'postgres:16.15-trixie'])

    def test_malformed_tags_are_refused(self):
        for tag in ('dev', 'latest', '', None, '0123456789AB', '0123456789a', '0123456789abc', '01234567-9ab'):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, '12 lowercase hex'):
                lab.validate_config(config(tag or 'dev'), tag)

    def test_service_tags_must_agree(self):
        for service in ('initialize', 'api', 'worker', 'web', 'reader'):
            broken = config()
            image = broken['services'][service]['image']
            broken['services'][service]['image'] = image.rsplit(':', 1)[0] + ':ba9876543210'
            with self.subTest(service=service), self.assertRaises(ValueError):
                lab.validate_config(broken, TAG)

    def test_build_is_refused(self):
        for service in ('api', 'web', 'db'):
            broken = config()
            broken['services'][service]['build'] = {'context': '.', 'dockerfile': 'backend/Dockerfile'}
            with self.subTest(service=service), self.assertRaisesRegex(ValueError, 'must not build'):
                lab.validate_config(broken, TAG)

    def test_pre_ledger_images_are_accepted_for_routine_actions(self):
        self.assertEqual(lab.validate_config(config(lab.PRE_LEDGER), lab.PRE_LEDGER)['tag'], lab.PRE_LEDGER)

    def test_existing_rules_still_apply(self):
        broken = config()
        broken['services']['api']['ports'][0]['host_ip'] = '0.0.0.0'
        with self.assertRaisesRegex(ValueError, 'port'):
            lab.validate_config(broken, TAG)
        broken = copy.deepcopy(config())
        broken['services']['worker']['environment']['DATABASE_URL'] = 'postgresql+psycopg://industry:x@db:5432/industry_research'
        with self.assertRaisesRegex(ValueError, 'privilege'):
            lab.validate_config(broken, TAG)


class ComposeEnvironmentTests(unittest.TestCase):
    def test_host_research_variables_never_reach_compose(self):
        host = {'RESEARCH_IMAGE_TAG': 'ffffffffffff', 'RESEARCH_POSTGRES_PASSWORD': 'host', 'COMPOSE_PROFILES': 'scheduler',
                'PATH': os.environ.get('PATH', '')}
        with mock.patch.dict(os.environ, host, clear=True), mock.patch.object(lab, 'run', return_value=b'') as run:
            lab.compose('config', tag=TAG)
        env = run.call_args.kwargs['env']
        self.assertEqual(env['RESEARCH_IMAGE_TAG'], TAG)
        self.assertEqual([k for k in env if k.startswith('RESEARCH_')], ['RESEARCH_IMAGE_TAG'])
        self.assertNotIn('COMPOSE_PROFILES', env)
        self.assertEqual(run.call_args.args[0][:3], ['docker', 'compose', '--project-name'])

    def test_compose_requires_a_valid_tag(self):
        with mock.patch.object(lab, 'run') as run:
            for tag in ('dev', 'latest', ''):
                with self.subTest(tag=tag), self.assertRaises(ValueError):
                    lab.compose('ps', tag=tag)
            with self.assertRaises(TypeError):
                lab.compose('ps')
        run.assert_not_called()


class CommittedComposeTests(unittest.TestCase):
    def test_no_build_and_tag_variable_everywhere(self):
        for name, script in (('compose.research.yaml', 'research_lab.py'), ('compose.research-drill.yaml', 'research_drill.py')):
            services = yaml.safe_load((ROOT / name).read_text(encoding='utf-8'))['services']
            for service, definition in services.items():
                with self.subTest(file=name, service=service):
                    self.assertNotIn('build', definition)
                    if service != 'db':
                        self.assertTrue(definition['image'].endswith(':${RESEARCH_IMAGE_TAG:?use scripts/' + script + '}'),
                                        definition['image'])

    def test_drill_initialize_matches_production(self):
        production = yaml.safe_load((ROOT / 'compose.research.yaml').read_text(encoding='utf-8'))['services']['initialize']
        drill = yaml.safe_load((ROOT / 'compose.research-drill.yaml').read_text(encoding='utf-8'))['services']['initialize']
        self.assertEqual(drill['command'], production['command'])
        self.assertEqual(drill['volumes'], production['volumes'])


if __name__ == '__main__':
    unittest.main()
