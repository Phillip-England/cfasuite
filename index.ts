import { Context, Handler, logger, Router } from "xerus/primitives";
import { handleHome, handleLogin, handleLogout, handleScorecard, handleStatic } from "./src/handlers";

const r = new Router();

r
  .get("/static/*", handleStatic)
  .get("/", handleHome)
  .post("/form/login", handleLogin)
	.get('/app/scorecard', handleScorecard)
	.get('/app/logout', handleLogout)

const server = Bun.serve({
  port: 8080,
  fetch: async (req: Request) => {
    try {
      const { handler, c } = r.find(req);
      if (handler) {
        return await handler.execute(c);
      }
      return new Response("404 Not Found", { status: 404 });
    } catch (e: any) {
      console.error(e);
      return new Response("internal server error", {
        status: 500,
        headers: { "Content-Type": "text/plain" }, // Ensure text response
      });
    }
  },
});

console.log(`Server running on ${server.port}`);
