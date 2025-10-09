"""Tests for init command."""

from pathlib import Path

from swim_data_tool.commands.init import InitCommand


class TestInitCommand:
    """Test suite for InitCommand."""

    def test_init_command_creation(self, tmp_path):
        """Test that InitCommand can be created."""
        cmd = InitCommand("Test Team", tmp_path)
        assert cmd.team_name == "Test Team"
        assert cmd.cwd == tmp_path

    def test_template_dir_exists(self):
        """Test that template directory exists."""
        cmd = InitCommand("Test", Path.cwd())
        assert cmd.TEMPLATE_DIR.exists()
        assert cmd.TEMPLATE_DIR.is_dir()

    def test_template_files_exist(self):
        """Test that all required template files exist."""
        cmd = InitCommand("Test", Path.cwd())

        required_templates = [
            "env.template",
            ".gitignore.template",
            "README.md.template",
            "claude.md.template",
            "gitkeep.template",
        ]

        for template in required_templates:
            template_path = cmd.TEMPLATE_DIR / template
            assert template_path.exists(), f"Missing template: {template}"

    def test_directory_structure_defined(self):
        """Test that directory structure is properly defined."""
        cmd = InitCommand("Test", Path.cwd())
        assert len(cmd.DIRECTORIES) > 0
        assert "data" in cmd.DIRECTORIES
        assert "data/raw" in cmd.DIRECTORIES
        assert "data/records" in cmd.DIRECTORIES

    def test_write_from_template(self, tmp_path):
        """Test template variable substitution."""
        cmd = InitCommand("Test Team", tmp_path)

        # Create a simple test template
        test_template = tmp_path / "test.template"
        test_template.write_text("Hello {{NAME}}, you are {{AGE}} years old.")

        # Write output with substitutions
        output_file = tmp_path / "output.txt"
        cmd.TEMPLATE_DIR = tmp_path  # Override to use tmp_path
        cmd._write_from_template("test.template", output_file, {"NAME": "Alice", "AGE": "30"})

        # Check output
        assert output_file.exists()
        content = output_file.read_text()
        assert content == "Hello Alice, you are 30 years old."
        assert "{{NAME}}" not in content
        assert "{{AGE}}" not in content


class TestTemplateContent:
    """Test template file content."""

    def test_env_template_has_required_vars(self):
        """Test that env.template contains required variables."""
        cmd = InitCommand("Test", Path.cwd())
        template_path = cmd.TEMPLATE_DIR / "env.template"
        content = template_path.read_text()

        required_vars = [
            "{{CLUB_NAME}}",
            "{{CLUB_ABBREVIATION}}",
            "{{USA_SWIMMING_TEAM_CODE}}",
            "{{LSC_CODE}}",
            "{{LSC_NAME}}",
            "{{START_YEAR}}",
            "{{END_YEAR}}",
        ]

        for var in required_vars:
            assert var in content, f"Missing variable in env.template: {var}"

    def test_readme_template_has_placeholders(self):
        """Test that README.md.template has proper placeholders."""
        cmd = InitCommand("Test", Path.cwd())
        template_path = cmd.TEMPLATE_DIR / "README.md.template"
        content = template_path.read_text()

        assert "{{CLUB_NAME}}" in content
        assert "{{USA_SWIMMING_TEAM_CODE}}" in content
        assert "{{SWIM_DATA_TOOL_VERSION}}" in content

    def test_claude_template_has_placeholders(self):
        """Test that claude.md.template has proper placeholders."""
        cmd = InitCommand("Test", Path.cwd())
        template_path = cmd.TEMPLATE_DIR / "claude.md.template"
        content = template_path.read_text()

        assert "{{CLUB_NAME}}" in content
        assert "{{REPO_NAME}}" in content
