# Contributing to AC-Virtual-Engineer

First off, thank you for considering contributing to this project! It's people like you that make the open-source community such a great place to learn, inspire, and create.

## Getting Started

1. **Fork the Repository**: Click the 'Fork' button at the top right of this page.
2. **Clone your Fork**: `git clone https://github.com/YOUR_USERNAME/AC-Virtual-Engineer.git`
3. **Create a Branch**: `git checkout -b feature/your-feature-name`

## Development Guidelines

### Backend (Python)

- We use `black` for code formatting and `flake8` for linting.
- Type hints are strongly encouraged. We use `mypy` for static type checking.
- Install dev dependencies using `pip install -r backend/requirements-dev.txt`.
- Before committing, ensure your code passes: `black .`, `flake8`, and `mypy .`.

### Frontend (React/TypeScript)

- We use ESLint for code quality.
- Ensure you run `npm run lint` inside the `/frontend` directory before opening a PR.

## Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/). This allows `release-please` to automatically generate changelogs and bump versions.

- `feat:` for new features (e.g., `feat: add fuel calculation logic`)
- `fix:` for bug fixes (e.g., `fix: resolve UDP socket timeout`)
- `docs:` for documentation changes
- `chore:` for maintenance tasks (e.g., updating dependencies)

## Opening a Pull Request

1. Push your changes to your fork: `git push origin feature/your-feature-name`
2. Open a Pull Request against the `main` branch of this repository.
3. Fill out the provided Pull Request template completely.

Your PR will trigger our GitHub Actions workflows (`backend-ci` and `frontend-ci`). Please ensure all checks pass!
