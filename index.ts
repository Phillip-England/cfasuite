import { logger, Xerus } from "xerus/xerus";
import {
  handleHome,
  handleLogin,
  handleLogout,
  handleScorecard,
  handleStatic,
} from "./src/handlers";
import {
  mwAdminAuth,
  mwAdminRedirect,
  mwStoreSelection,
} from "./src/middleware";

const app = new Xerus();

app.DEBUG_MODE = true;

app.use(logger);

app.group("/app/scorecard", mwAdminAuth, mwStoreSelection)
  .get("/leadership", handleScorecard)
  .get("/talent", handleScorecard)
  .get("/cem", handleScorecard)
  .get("/sales", handleScorecard)
  .get("/finance", handleScorecard)
  .get("/logout", handleLogout);

app.group("/app", mwAdminAuth)
  .get("/logout", handleLogout);

app
  .get("/static/*", handleStatic)
  .get("/", handleHome, mwAdminRedirect)
  .post("/form/login", handleLogin);

const server = Bun.serve({
  port: 8080,
  fetch: async (req: Request) => {
    return await app.run(req);
  },
});

console.log(`Server running on ${server.port}`);
