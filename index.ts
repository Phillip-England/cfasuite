import { Context, Handler, logger, Router } from "xerus/primitives";
import { handleHome, handleLogin, handleStatic } from "./src/handlers";

const r = new Router();

r
  .get("/static/*", handleStatic)
  .get("/", handleHome)
  .post('/form/login', handleLogin)

const server = Bun.serve({
  port: 8080,
  fetch: async (req: Request) => {
    try {
      const { handler, c } = r.find(req);
      if (handler) {
        return handler.execute(c);
      }
      return c.status(404).send("404 Not Found");
    } catch (e: any) {
      console.error(e);
      return new Response("internal server error", { status: 500 });
    }
  },
});

console.log(`Server running on ${server.port}`);
