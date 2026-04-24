/** @type {import('next').NextConfig} */
const path = require("path");

module.exports = {
  // Resolve the workspace-local package source during tests (no publish step required).
  transpilePackages: ["@pamfilico/admin-auth-react"],
  webpack: (config) => {
    config.resolve.alias["@pamfilico/admin-auth-react"] = path.resolve(
      __dirname,
      "../js/src/index.ts",
    );
    return config;
  },
};
