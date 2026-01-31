import pluginVue from "eslint-plugin-vue";
import vueTsEslintConfig from "@vue/eslint-config-typescript";

export default [
  {
    name: "app/files-to-lint",
    files: ["**/*.{ts,mts,tsx,vue}"],
  },
  {
    name: "app/files-to-ignore",
    ignores: [
      "**/dist/**",
      "**/dist-ssr/**",
      "**/coverage/**",
      "**/node_modules/**",
      "**/vite-env.d.ts",
    ],
  },
  ...pluginVue.configs["flat/essential"],
  ...vueTsEslintConfig(),
  {
    rules: {
      // Allow unused vars with underscore prefix
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
      // Disable any warnings - will gradually add types
      "@typescript-eslint/no-explicit-any": "off",
      // Vue specific
      "vue/multi-word-component-names": "off",
    },
  },
];
