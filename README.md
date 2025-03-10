# Personal Website

## Development Setup

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation
1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```
3. Set up pre-commit hooks:
   ```
   npx husky install
   chmod +x .husky/pre-commit
   ```

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to run code quality checks before each commit.

### Setup

1. Install the development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```

2. Install the pre-commit hooks:
   ```
   pre-commit install
   ```

3. (Optional) Run the hooks against all files:
   ```
   pre-commit run --all-files
   ```

The pre-commit hooks will now run automatically on each commit.

### Building the Site
To build the site:
```
npm run build
```
or
```
yarn build
```

### Troubleshooting
If pre-commit hooks aren't working:
1. Make sure Husky is installed: `npx husky install`
2. Make sure the pre-commit hook is executable: `chmod +x .husky/pre-commit`
3. Make sure the Husky helper script is executable: `chmod +x .husky/_/husky.sh`
4. Try running the formatter manually: `npm run format` 
