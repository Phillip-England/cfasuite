import { BodyType, Context, Handler, logger } from "xerus/primitives";
import { renderToString } from "react-dom/server";
import { PageLogin } from "./pages";

export const handleHome = new Handler(async (c: Context): Promise<Response> => {
  return c.html(renderToString(<PageLogin loginErr=""/>));
}, logger);

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
    let { data, err } = await c.parseBody(BodyType.FORM)
    if (err) {
      return c.status(400).send('invalid parsing at /form/login')
    }
    if (data.username == process.env.ADMIN_USERNAME && data.password == process.env.ADMIN_PASSWORD) {
      return c.redirect('/')
    }
    return c.redirect('/')
  },
);
