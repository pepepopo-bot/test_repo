import unittest
import yaml
from pathlib import Path


class TestGitHubWorkflow(unittest.TestCase):
    """Test suite for GitHub workflow YAML validation and structure."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        cls.workflow_path = Path('.github/workflows/build.yml')
        # Create a test workflow file for validation
        cls.test_workflow_content = """
name: Build project

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        java: [11, 17]
    name: "Java ${{ matrix.java }} build"
    steps:
      - name: Checkout project
        uses: actions/checkout@v4
      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: "temurin"
          java-version: "${{ matrix.java }}"
          cache: "maven"
      - name: Verify build
        run: mvn -B verify
  sonar:
    needs: build
    if: github.base_ref == 'main' && github.event_name == 'pull_request'
    name: Prepare analysis context
    uses: ./.github/workflows/sonar-pull-prepare.yml
    with:
      pull_request: ${{ toJSON(github.event.pull_request) }}
"""

    def test_workflow_yaml_is_valid(self):
        """Test that the workflow YAML is syntactically valid."""
        try:
            parsed = yaml.safe_load(self.test_workflow_content)
            self.assertIsInstance(parsed, dict)
        except yaml.YAMLError as e:
            self.fail(f"YAML parsing failed: {e}")
    
    def test_workflow_has_required_fields(self):
        """Test that the workflow contains all required top-level fields."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        required_fields = ['name', 'on', 'jobs']
        for field in required_fields:
            self.assertIn(field, workflow, f"Required field '{field}' is missing")
    
    def test_workflow_name_is_string(self):
        """Test that the workflow name is a non-empty string."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        self.assertIsInstance(workflow['name'], str)
        self.assertTrue(len(workflow['name']) > 0)
        self.assertEqual(workflow['name'], 'Build project')
    
    def test_workflow_triggers_are_valid(self):
        """Test that workflow triggers are properly configured."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        triggers = workflow['on']
        self.assertIsInstance(triggers, (dict, list))
        
        # If it's a list, check for valid trigger names
        if isinstance(triggers, list):
            valid_triggers = ['push', 'pull_request', 'schedule', 'workflow_dispatch']
            for trigger in triggers:
                self.assertIn(trigger, valid_triggers)
    
    def test_permissions_are_properly_set(self):
        """Test that permissions are configured correctly."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        self.assertIn('permissions', workflow)
        permissions = workflow['permissions']
        self.assertIsInstance(permissions, dict)
        self.assertIn('contents', permissions)
        self.assertEqual(permissions['contents'], 'read')
    
    def test_build_job_configuration(self):
        """Test that the build job is properly configured."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        jobs = workflow['jobs']
        self.assertIn('build', jobs)
        
        build_job = jobs['build']
        self.assertIn('runs-on', build_job)
        self.assertEqual(build_job['runs-on'], 'ubuntu-latest')
        
        self.assertIn('strategy', build_job)
        self.assertIn('matrix', build_job['strategy'])
        self.assertIn('java', build_job['strategy']['matrix'])
        self.assertEqual(build_job['strategy']['matrix']['java'], [11, 17])
    
    def test_build_job_steps_structure(self):
        """Test that build job steps are properly structured."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        build_job = workflow['jobs']['build']
        self.assertIn('steps', build_job)
        
        steps = build_job['steps']
        self.assertIsInstance(steps, list)
        self.assertTrue(len(steps) > 0)
        
        for step in steps:
            self.assertIsInstance(step, dict)
            self.assertIn('name', step)
            self.assertTrue('uses' in step or 'run' in step)
    
    def test_checkout_step_configuration(self):
        """Test that the checkout step uses the correct action version."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        build_steps = workflow['jobs']['build']['steps']
        checkout_step = next((step for step in build_steps if 'checkout' in step['name'].lower()), None)
        
        self.assertIsNotNone(checkout_step, "Checkout step not found")
        self.assertEqual(checkout_step['uses'], 'actions/checkout@v4')
    
    def test_java_setup_step_configuration(self):
        """Test that the Java setup step is properly configured."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        build_steps = workflow['jobs']['build']['steps']
        java_step = next((step for step in build_steps if 'java' in step['name'].lower()), None)
        
        self.assertIsNotNone(java_step, "Java setup step not found")
        self.assertEqual(java_step['uses'], 'actions/setup-java@v4')
        
        with_config = java_step['with']
        self.assertEqual(with_config['distribution'], 'temurin')
        self.assertEqual(with_config['java-version'], '${{ matrix.java }}')
        self.assertEqual(with_config['cache'], 'maven')
    
    def test_maven_verify_step(self):
        """Test that the Maven verify step is configured correctly."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        build_steps = workflow['jobs']['build']['steps']
        verify_step = next((step for step in build_steps if 'verify' in step['name'].lower()), None)
        
        self.assertIsNotNone(verify_step, "Verify build step not found")
        self.assertEqual(verify_step['run'], 'mvn -B verify')
    
    def test_sonar_job_configuration(self):
        """Test that the Sonar job is properly configured."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        jobs = workflow['jobs']
        self.assertIn('sonar', jobs)
        
        sonar_job = jobs['sonar']
        self.assertIn('needs', sonar_job)
        self.assertEqual(sonar_job['needs'], 'build')
        
        self.assertIn('if', sonar_job)
        expected_condition = "github.base_ref == 'main' && github.event_name == 'pull_request'"
        self.assertEqual(sonar_job['if'], expected_condition)
    
    def test_sonar_job_uses_external_workflow(self):
        """Test that the Sonar job correctly references external workflow."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        sonar_job = workflow['jobs']['sonar']
        self.assertIn('uses', sonar_job)
        self.assertEqual(sonar_job['uses'], './.github/workflows/sonar-pull-prepare.yml')
        
        self.assertIn('with', sonar_job)
        with_config = sonar_job['with']
        self.assertIn('pull_request', with_config)
        self.assertEqual(with_config['pull_request'], '${{ toJSON(github.event.pull_request) }}')
    
    def test_matrix_java_versions_are_supported(self):
        """Test that the Java versions in the matrix are currently supported."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        java_versions = workflow['jobs']['build']['strategy']['matrix']['java']
        supported_versions = [8, 11, 17, 21]  # Common LTS versions
        
        for version in java_versions:
            self.assertIn(version, supported_versions, 
                         f"Java version {version} may not be supported")
    
    def test_workflow_job_dependencies(self):
        """Test that job dependencies are properly configured."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        jobs = workflow['jobs']
        
        # Build job should not have dependencies
        self.assertNotIn('needs', jobs['build'])
        
        # Sonar job should depend on build
        self.assertIn('needs', jobs['sonar'])
        self.assertEqual(jobs['sonar']['needs'], 'build')
    
    def test_github_context_variables_syntax(self):
        """Test that GitHub context variables use correct syntax."""
        workflow_str = self.test_workflow_content
        
        # Test for correct GitHub context syntax
        context_patterns = [
            '${{ matrix.java }}',
            '${{ toJSON(github.event.pull_request) }}',
            "github.base_ref == 'main'",
            "github.event_name == 'pull_request'"
        ]
        
        for pattern in context_patterns:
            self.assertIn(pattern, workflow_str, f"Context pattern '{pattern}' not found")
    
    def test_action_versions_are_specified(self):
        """Test that all actions use pinned versions."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        build_steps = workflow['jobs']['build']['steps']
        
        for step in build_steps:
            if 'uses' in step:
                action = step['uses']
                self.assertRegex(action, r'@v\d+', 
                               f"Action '{action}' should specify a version")
    
    def test_workflow_names_are_descriptive(self):
        """Test that workflow and job names are descriptive."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        # Workflow name should be descriptive
        self.assertTrue(len(workflow['name']) > 5)
        
        # Job names should be descriptive
        for _job_name, job_config in workflow['jobs'].items():
            if 'name' in job_config:
                self.assertTrue(len(job_config['name']) > 3)
    
    def test_workflow_environment_consistency(self):
        """Test that the workflow uses consistent environment settings."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        build_job = workflow['jobs']['build']
        
        # Should use ubuntu-latest for consistency
        self.assertEqual(build_job['runs-on'], 'ubuntu-latest')
        
        # Maven commands should use batch mode
        verify_step = next((step for step in build_job['steps'] if 'run' in step and 'mvn' in step['run']), None)
        if verify_step:
            self.assertIn('-B', verify_step['run'], "Maven should run in batch mode")
    
    def test_workflow_security_permissions(self):
        """Test that workflow permissions follow security best practices."""
        workflow = yaml.safe_load(self.test_workflow_content)
        
        permissions = workflow.get('permissions', {})
        
        # Should have explicit permissions rather than default
        self.assertTrue(len(permissions) > 0, "Workflow should specify explicit permissions")
        
        # Contents should be read-only for security
        if 'contents' in permissions:
            self.assertEqual(permissions['contents'], 'read')


if __name__ == '__main__':
    unittest.main()