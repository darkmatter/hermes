import { defineTool } from "eve/tools";
import { z } from "zod";

/** Filename becomes the tool name (snake_case). */
export default defineTool({
  description: "Return a pong with the current ISO timestamp.",
  inputSchema: z.object({
    note: z.string().optional().describe("Optional note echoed back"),
  }),
  async execute({ note }) {
    return {
      ok: true,
      pong: true,
      at: new Date().toISOString(),
      note: note ?? null,
    };
  },
});
