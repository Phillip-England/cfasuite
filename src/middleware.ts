import { Context, Middleware, type MiddlewareFn } from "xerus/primitives";
import { STORE_SOUTHROADS } from "./const";

export const mwAdminRedirect = new Middleware(async (c: Context, next): Promise <void|Response> => {
	let authCookie = c.getCookie(process.env.ADMIN_COOKIE as string)
	if (authCookie) {
		return c.redirect("/app/scorecard")
	} 
	await next()
})

export const mwAdminAuth = new Middleware(async (c: Context, next): Promise<void | Response> => {
	let authCookie = c.getCookie(process.env.ADMIN_COOKIE as string)
	if (authCookie != process.env.ADMIN_TOKEN) {
		return c.redirect("/")
	} 
	await next()
})

export const mwStoreSelection = new Middleware(async (c: Context, next): Promise<void | Response> => {
	let storeCookie = c.getCookie(process.env.STORE_COOKIE as string)
	if (!storeCookie) {
		c.setCookie(process.env.STORE_COOKIE as string, STORE_SOUTHROADS)	
	}
	await next()
})