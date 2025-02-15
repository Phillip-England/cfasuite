import { BodyType, Context, Handler, logger } from "xerus/xerus";
import { renderToString } from "react-dom/server";
import { PageLogin, PageScorecard } from "./pages";

export const handleHome = async (c: Context): Promise<Response> => {
  return c.html(renderToString(<PageLogin loginErr={c.query("loginErr")} />));
};

export const handleStatic = async (c: Context): Promise<Response> => {
  let file = Bun.file("." + c.path);
  if (!file) {
    return c.status(404).text("file not found");
  }
  return await c.file(file);
};

export const handleLogin = async (c: Context): Promise<Response> => {
  let data = await c.parseBody(BodyType.FORM);
  if (
    data.username == process.env.ADMIN_USERNAME &&
    data.password == process.env.ADMIN_PASSWORD
  ) {
    c.setCookie(
      process.env.ADMIN_COOKIE as string,
      process.env.ADMIN_TOKEN as string,
      {
        httpOnly: true,
        path: "/",
        secure: true,
      },
    );
    return c.redirect("/app/scorecard/leadership");
  }
  return c.redirect("/?loginErr=invalid credentials");
};

export const handleScorecard = async (c: Context): Promise<Response> => {
  return c.html(renderToString(<PageScorecard currentPath={c.path} />));
};

export const handleLogout = async (c: Context): Promise<Response> => {
  c.clearCookie(process.env.ADMIN_COOKIE as string);
  return c.redirect("/");
};
