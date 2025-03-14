export default {
  transform: {
    "^.+\\.js$": "babel-jest"
  },
  setupFilesAfterEnv: ["jest-canvas-mock"]
};
