export default {
  transform: {
    "^.+\\.js$": "babel-jest"
  },
  testEnvironment: "jsdom",
  setupFiles: ["<rootDir>/jest.setup.js"]
};
