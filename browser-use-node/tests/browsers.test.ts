import { describe, expect, it, vi } from "vitest";

import { Browsers as V2Browsers } from "../src/v2/resources/browsers.js";
import { Browsers as V3Browsers } from "../src/v3/resources/browsers.js";

describe.each([
  ["v2", V2Browsers],
  ["v3", V3Browsers],
])("%s browser metadata", (_version, Browsers) => {
  it("sends metadata on create and as repeated-filter input on list", async () => {
    const http = {
      post: vi.fn(async () => ({})),
      get: vi.fn(async () => ({ items: [], totalItems: 0, pageNumber: 1, pageSize: 10 })),
    };
    const browsers = new Browsers(http as any);

    await browsers.create({
      metadata: { team: "sdk", env: "test" },
      pdfRendererEnabled: false,
      solveCaptchas: false,
    });
    await browsers.list({ metadata: ["team", "env=test"] });

    expect(http.post).toHaveBeenCalledWith("/browsers", {
      metadata: { team: "sdk", env: "test" },
      pdfRendererEnabled: false,
      solveCaptchas: false,
    });
    expect(http.get).toHaveBeenCalledWith("/browsers", {
      metadata: ["team", "env=test"],
    });
  });

  it("rejects more than 10 metadata entries", () => {
    const http = { post: vi.fn() };
    const browsers = new Browsers(http as any);
    const metadata = Object.fromEntries(
      Array.from({ length: 11 }, (_, index) => [`key-${index}`, `value-${index}`]),
    );

    expect(() => browsers.create({ metadata })).toThrow(
      "metadata supports at most 10 key-value pairs",
    );
    expect(http.post).not.toHaveBeenCalled();
  });
});
