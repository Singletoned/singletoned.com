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
   ```

### Pre-commit Hooks
This project uses pre-commit hooks to automatically format JavaScript files in the `scripts` directory before committing. The formatting is done using Prettier according to the rules defined in `.prettierrc`.

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