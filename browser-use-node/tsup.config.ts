import { defineConfig } from "tsup";

export default defineConfig({
  entry: {
    index: "src/index.ts",
    v3: "src/v3.ts",
  },
  format: ["cjs", "esm"],
  dts: true,
  splitting: true,
  clean: true,
  sourcemap: true,
});
