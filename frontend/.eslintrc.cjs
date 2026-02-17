module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-type-checked',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs', 'vite.config.ts', 'node_modules'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: ['./tsconfig.json', './tsconfig.node.json'],
    tsconfigRootDir: __dirname,
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: ['@typescript-eslint', 'react', 'react-hooks', 'react-refresh'],
  settings: {
    react: {
      version: 'detect',
    },
  },
  rules: {
    // React Refresh (Vite HMR)
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],

    // React rules
    'react/prop-types': 'off', // TypeScript handles prop validation
    'react/react-in-jsx-scope': 'off', // Not needed with React 18+ JSX transform
    'react/jsx-no-target-blank': 'error',
    'react/self-closing-comp': 'warn',
    'react/jsx-curly-brace-presence': [
      'warn',
      { props: 'never', children: 'never' },
    ],

    // React Hooks rules
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // TypeScript rules
    '@typescript-eslint/no-unused-vars': [
      'warn',
      {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        destructuredArrayIgnorePattern: '^_',
      },
    ],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    '@typescript-eslint/no-floating-promises': 'error',
    '@typescript-eslint/no-misused-promises': [
      'error',
      {
        checksVoidReturn: {
          attributes: false,
        },
      },
    ],
    '@typescript-eslint/await-thenable': 'error',
    '@typescript-eslint/consistent-type-imports': [
      'warn',
      { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
    ],

    // General rules
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'warn',
    'no-duplicate-imports': 'error',
    'no-unused-expressions': 'error',
    'prefer-const': 'warn',
    eqeqeq: ['error', 'always'],
    curly: ['warn', 'all'],
  },
  overrides: [
    {
      // Relax rules for test files
      files: ['**/__tests__/**/*', '**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-non-null-assertion': 'off',
        '@typescript-eslint/no-floating-promises': 'off',
        'no-console': 'off',
      },
    },
  ],
};
