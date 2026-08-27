import { defaultBackend, defineSandbox } from "eve/sandbox";

/** Local-first backend order; does not select Vercel Sandbox. */
export default defineSandbox({
  backend: defaultBackend(),
});
