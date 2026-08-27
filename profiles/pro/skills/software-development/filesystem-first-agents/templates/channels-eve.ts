import { eveChannel } from "eve/channels/eve";
import { localDev, placeholderAuth, vercelOidc } from "eve/channels/auth";

/** auth is required — empty eveChannel() fails at compile/eval. */
export default eveChannel({
  auth: [
    vercelOidc(),
    localDev(),
    // Temporary open first-run policy; tighten for exposed hosts.
    placeholderAuth(),
  ],
});
