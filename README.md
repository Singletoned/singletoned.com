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
This project uses Husky and lint-staged to automatically format JavaScript files in the `scripts` directory before committing. The formatting is done using Prettier according to the rules defined in `.prettierrc`.

To manually format all files:
```
npm run format
```
or
```
yarn format
```

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