import { Context, Middleware, type MiddlewareFn } from "xerus/primitives";

export const loggedInRedirect = new Middleware(async (c: Context, next): Promise <void|Response> => {
	let authCookie = c.getCookie(process.env.ADMIN_COOKIE as string)
	if (authCookie) {
		return c.redirect("/app/scorecard")
	} 
	await next()
})

export const adminAuth = new Middleware(async (c: Context, next): Promise<void | Response> => {
	let authCookie = c.getCookie(process.env.ADMIN_COOKIE as string)
	if (authCookie != process.env.ADMIN_TOKEN) {
		return c.redirect("/")
	} 
	await next()
})