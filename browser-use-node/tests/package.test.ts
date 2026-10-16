import { readFileSync } from "fs";
import { describe, expect, it } from "vitest";

const pkg = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));

describe("package entry points", () => {
  it("exposes /v2 as the root client and maps every subpath for node10 type resolution", () => {
    expect(pkg.exports["./v2"]).toEqual(pkg.exports["."]);
    for (const [subpath, target] of Object.entries<any>(pkg.exports)) {
      if (subpath === ".") continue;
      expect(pkg.typesVersions["*"][subpath.slice(2)]).toEqual([target.import.types]);
    }
  });
});
