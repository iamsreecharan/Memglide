import { describe, expect, it, vi } from "vitest";
import { api, ApiError, post, queryString } from "../src/api";

describe("local API transport", () => {
  it("adds browser mutation protection and reports structured server errors", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            error: { code: "conflict", message: "Source hash changed" },
          }),
          { status: 409, headers: { "Content-Type": "application/json" } },
        ),
      );
    vi.stubGlobal("fetch", fetch);
    await expect(
      post("/sessions/s/memories", { content: "Verified" }),
    ).rejects.toEqual(new ApiError("Source hash changed", 409));
    expect(fetch).toHaveBeenCalledWith(
      "/api/sessions/s/memories",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "X-Memglide-Request": "1",
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({ content: "Verified" }),
      }),
    );
  });

  it("distinguishes an unavailable local service and URL-encodes query filters", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Network error")),
    );
    await expect(api("/health")).rejects.toThrow(
      "Cannot reach the local Memglide service",
    );
    expect(
      queryString({
        query: "auth & JWT",
        empty: "",
        absent: undefined,
        level: 2,
      }),
    ).toBe("?query=auth+%26+JWT&level=2");
  });
});
