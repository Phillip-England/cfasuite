import { Context, Middleware } from "xerus/xerus";
import { STORE_SOUTHROADS, STORE_UTICA } from "./const";

export const mwAdminRedirect = new Middleware(
  async (c: Context, next: any): Promise<void | Response> => {
    let authCookie = c.getCookie(process.env.ADMIN_COOKIE as string);
    if (authCookie) {
      return c.redirect("/app/scorecard");
    }
    await next();
  },
);

export const mwAdminAuth = new Middleware(
  async (c: Context, next: any): Promise<void | Response> => {
    let authCookie = c.getCookie(process.env.ADMIN_COOKIE as string);
    if (authCookie != process.env.ADMIN_TOKEN) {
      return c.redirect("/");
    }
    await next();
  },
);

export const mwStoreSelection = new Middleware(
  async (c: Context, next: any): Promise<void | Response> => {
    let selectedStore = c.query("store");
    let storeCookieName = process.env.STORE_COOKIE as string;
    switch (selectedStore) {
      case STORE_SOUTHROADS: {
        c.setCookie(storeCookieName, STORE_SOUTHROADS);
        break;
      }
      case STORE_UTICA: {
        c.setCookie(storeCookieName, STORE_UTICA);
        break;
      }
      default: {
        let storeCookie = c.getCookie(storeCookieName);
        if (!storeCookie) {
          c.setCookie(storeCookieName, STORE_SOUTHROADS);
        }
      }
    }
    await next();
  },
);
