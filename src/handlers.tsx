import { BodyType, Context, Handler, logger } from "xerus/primitives";
import { renderToString } from "react-dom/server";
import { PageLogin, PageScorecard } from "./pages";
import { adminAuth, loggedInRedirect } from "./middleware";

export const handleHome = new Handler(async (c: Context): Promise<Response> => {
  return c.html(renderToString(<PageLogin loginErr={c.query('loginErr')} />));
}, logger, loggedInRedirect);

export const handleStatic = new Handler(
  async (c: Context): Promise<Response> => {
    let file = await c.file("." + c.path);
    if (!file) {
      return c.status(404).send("file not found");
    }
    return file;
  },
);

export const handleLogin = new Handler(
  async (c: Context): Promise<Response> => {
    let data = await c.parseBody(BodyType.FORM);
    if (
      data.username == process.env.ADMIN_USERNAME &&
      data.password == process.env.ADMIN_PASSWORD
    ) {
			c.setCookie(process.env.ADMIN_COOKIE as string, process.env.ADMIN_TOKEN as string, {
				httpOnly: true,
				path: "/",
				secure: true,
			})
      return c.redirect("/app/scorecard");
    }
    return c.redirect("/?loginErr=invalid credentials");
  }, logger);

export const handleScorecard = new Handler(async (c: Context): Promise<Response> => {
  return c.html(renderToString(<PageScorecard/>));
}, logger, adminAuth);

export const handleLogout = new Handler(async (c: Context): Promise<Response> => {
	c.clearCookie(process.env.ADMIN_COOKIE as string)
	console.log('hit')
	return c.redirect("/")
}, logger);
