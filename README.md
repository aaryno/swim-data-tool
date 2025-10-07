# swim-data-tool

A modern CLI tool for swim team record management.

## Features

- 🏊 **Data Collection**: Import swim data from USA Swimming and World Aquatics
- 📊 **Record Generation**: Automatically generate team records by course, age group, and event
- 🔍 **Swim Classification**: Classify unattached swims (probationary, college, etc.)
- 📈 **Analysis**: Generate top 10 lists and annual summaries
- 🎨 **Beautiful CLI**: Rich terminal output with progress indicators
- ⚡ **Fast**: Built with modern Python and uv package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/aaryno/swim-data-tool.git
cd swim-data-tool

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv sync --dev

# Run the tool
uv run swim-data-tool --help
```

## Quick Start

```bash
# Initialize a new team
swim-data-tool init "Team Name"

# Import data
swim-data-tool import swimmers --src=usa-swimming

# Generate records
swim-data-tool generate records

# View status
swim-data-tool status
```

## Commands

- `init` - Initialize a new team repository
- `import` - Import swim data from APIs
- `classify` - Classify and organize swim data
- `generate` - Generate records and reports
- `status` - Show current status and configuration

## Development

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
```

## License

MIT
