//==============================
// cookies
//==============================

export interface CookieOptions {
  path?: string;
  domain?: string;
  maxAge?: number;
  expires?: Date;
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: "Strict" | "Lax" | "None";
}

//==============================
// context
//==============================

export enum BodyType {
  JSON = "json",
  TEXT = "string",
  FORM = "form",
  MULTIPART_FORM = "multipart_form",
}

export class Context {
  req: Request;
  res: MutResponse;
  url: URL;
  path: string;
  method: string;
  route: string;
  segments: string[];
  params: Record<string, string>;
  private _body?: string | Record<string, any> | FormData;
  storeData: Record<string, string>;

  constructor(req: Request, params: Record<string, string> = {}) {
    this.req = req;
    this.res = new MutResponse();
    this.url = new URL(this.req.url);
    this.path = this.url.pathname.replace(/\/+$/, "") || "/";
    this.method = this.req.method;
    this.route = `${this.method} ${this.path}`;
    this.segments = this.path.split("/").filter(Boolean);
    this.params = params;
    this.storeData = {};
  }

  redirect(location: string, status: number = 302): Response {
    this.res.status(status);
    this.res.setHeader("Location", location);
    return this.res.send();
  }

  async parseBody<T extends BodyType>(
    expectedType: T,
  ): Promise<{
    data: T extends BodyType.JSON ? Record<string, any>
      : T extends BodyType.TEXT ? string
      : T extends BodyType.FORM ? Record<string, string>
      : T extends BodyType.MULTIPART_FORM ? FormData
      : never;
    err?: Error;
  }> {
    if (this._body !== undefined) {
      return { data: this._body as any };
    }
  
    const contentType = this.req.headers.get("Content-Type") || "";
  
    try {
      let parsedData: any;
  
      if (contentType.includes("application/json")) {
        parsedData = await this.req.json();
        if (expectedType !== BodyType.JSON) {
          throw new Error("Unexpected JSON data");
        }
      } else if (contentType.includes("application/x-www-form-urlencoded")) {
        parsedData = Object.fromEntries(
          new URLSearchParams(await this.req.text()),
        );
        if (expectedType !== BodyType.FORM) {
          throw new Error("Unexpected FORM data");
        }
      } else if (contentType.includes("multipart/form-data")) {
        parsedData = await this.req.formData();
        if (expectedType !== BodyType.MULTIPART_FORM) {
          throw new Error("Unexpected MULTIPART_FORM data");
        }
      } else {
        parsedData = await this.req.text();
        if (expectedType !== BodyType.TEXT) {
          throw new Error("Unexpected TEXT data");
        }
      }
  
      this._body = parsedData;
      return { data: parsedData };
    } catch (err: any) {
      return {
        data: (expectedType === BodyType.JSON
          ? {}
          : expectedType === BodyType.FORM
          ? {}
          : expectedType === BodyType.MULTIPART_FORM
          ? new FormData()
          : "") as any, // Ensure a valid default value
        err: new Error(`Body parsing failed: ${err.message}`),
      };
    }
  }
  

  param(name: string, defaultValue?: string): string | undefined {
    return this.params[name] ?? defaultValue;
  }

  status(code: number): this {
    this.res.status(code);
    return this;
  }

  setHeader(name: string, value: string): this {
    this.res.setHeader(name, value);
    return this;
  }

  getHeader(name: string): string | null {
    return this.res.getHeader(name);
  }

  send(content: string): Response {
    return this.res.body(content).send();
  }

  html(content: string): Response {
    this.setHeader("Content-Type", "text/html");
    return this.send(content);
  }

  json(data: any): Response {
    this.setHeader("Content-Type", "application/json");
    return this.send(JSON.stringify(data));
  }

  async stream(stream: ReadableStream): Promise<Response> {
    this.setHeader("Content-Type", "application/octet-stream");
    return new Response(stream, {
      status: this.res.statusCode,
      headers: this.res.headers,
    });
  }

  async file(filePath: string, stream = false): Promise<Response | undefined> {
    const file = Bun.file(filePath);
    if (!file) return undefined;

    this.res.setHeader("Content-Type", file.type || "application/octet-stream");
    return stream
      ? new Response(file.stream(), {
        status: this.res.statusCode,
        headers: this.res.headers,
      })
      : new Response(file, {
        status: this.res.statusCode,
        headers: this.res.headers,
      });
  }

  setStore(key: string, value: any): void {
    this.storeData[key] = value;
  }

  getStore(key: string): any {
    return this.storeData[key] || undefined;
  }

  query(name: string, defaultValue?: string): string | undefined {
    return this.url.searchParams.get(name) ?? defaultValue;
  }

  getCookie(name: string): string | undefined {
    const cookies = this.req.headers.get("Cookie");
    if (!cookies) return undefined;

    const cookieMap = Object.fromEntries(
      cookies.split("; ").map((c) => c.split("=")),
    );

    return cookieMap[name];
  }

  setCookie(name: string, value: string, options: CookieOptions = {}): void {
    let cookieString = `${name}=${encodeURIComponent(value)}`;

    if (options.path) cookieString += `; Path=${options.path}`;
    if (options.domain) cookieString += `; Domain=${options.domain}`;
    if (options.maxAge !== undefined) {
      cookieString += `; Max-Age=${options.maxAge}`;
    }
    if (options.expires) {
      cookieString += `; Expires=${options.expires.toUTCString()}`;
    }
    if (options.httpOnly) cookieString += `; HttpOnly`;
    if (options.secure) cookieString += `; Secure`;
    if (options.sameSite) cookieString += `; SameSite=${options.sameSite}`;

    // Fix: Use append instead of setHeader to allow multiple cookies
    this.res.headers.append("Set-Cookie", cookieString);
  }

  clearCookie(name: string): void {
    this.setCookie(name, "", {
      maxAge: 0,
      expires: new Date(0),
    });
  }
}

//==============================
// handler
//==============================

export class Handler {
  private mainHandler: (c: Context) => Promise<Response>;
  private middlewares: Middleware[];

  constructor(
    mainHandler: (c: Context) => Promise<Response>,
    ...middlewares: Middleware[]
  ) {
    this.mainHandler = mainHandler;
    this.middlewares = middlewares;
  }

  async execute(c: Context): Promise<Response> {
    // Build the execution chain from the inside out
    let chain = this.mainHandler;

    // Work backwards through middleware array to build chain from inside out
    for (let i = this.middlewares.length - 1; i >= 0; i--) {
      const middleware = this.middlewares[i];
      const nextChain = chain;
      chain = async (context: Context): Promise<Response> => {
        let finalResponse: Response | undefined;

        // Execute the current middleware
        const result = await middleware.execute(context, async () => {
          const response = await nextChain(context);
          finalResponse = response;
          return response;
        });

        // Return early response from middleware if present
        if (result instanceof Response) {
          return result;
        }

        // Return the response from the next handler in chain
        if (finalResponse) {
          return finalResponse;
        }

        return new Response("no response generated", { status: 500 });
      };
    }

    // Execute the final chain
    return chain(c);
  }
}

//==============================
// middleware
//==============================

export type MiddlewareFn = (
  c: Context,
  next: () => Promise<void | Response>,
) => Promise<void | Response>;

export class Middleware {
  private callback: MiddlewareFn;

  constructor(callback: MiddlewareFn) {
    this.callback = callback;
  }

  async execute(
    c: Context,
    next: () => Promise<void | Response>,
  ): Promise<void | Response> {
    return this.callback(c, next);
  }
}

// Example middleware using the new class
export const logger = new Middleware(async (c: Context, next) => {
  const start = performance.now();
  await next();
  const duration = performance.now() - start;
  console.log(`[${c.req.method}][${c.path}][${duration.toFixed(2)}ms]`);
});

export class MutResponse {
  statusCode: number;
  headers: Headers;
  bodyContent: string;

  constructor() {
    this.statusCode = 200;
    this.headers = new Headers();
    this.bodyContent = "";
  }

  status(code: number): this {
    this.statusCode = code;
    return this;
  }

  setHeader(name: string, value: string): this {
    this.headers.set(name, value);
    return this;
  }

  getHeader(name: string): string | null {
    return this.headers.get(name);
  }

  body(content: string | object): this {
    this.bodyContent = typeof content === "object"
      ? JSON.stringify(content)
      : content;
    return this;
  }

  send(): Response {
    return new Response(this.bodyContent, {
      status: this.statusCode,
      headers: this.headers,
    });
  }
}

//==============================
// router
//==============================

class TrieNode {
  handlers: Map<string, Handler> = new Map();
  children: Map<string, TrieNode> = new Map();
  paramKey?: string;
  wildcard?: TrieNode;
}

export class Router {
  private root: TrieNode = new TrieNode();
  private staticRoutes: Map<string, Map<string, Handler>> = new Map();
  private resolvedRoutes: Map<
    string,
    { handler?: Handler; params: Record<string, string> }
  > = new Map();

  private readonly MAX_CACHE_SIZE = 100; // Adjust size as needed

  get(path: string, handler: Handler): Router {
    this.add("GET", path, handler);
    return this;
  }
  post(path: string, handler: Handler): Router {
    this.add("POST", path, handler);
    return this;
  }
  put(path: string, handler: Handler): Router {
    this.add("PUT", path, handler);
    return this;
  }
  delete(path: string, handler: Handler): Router {
    this.add("DELETE", path, handler);
    return this;
  }
  patch(path: string, handler: Handler): Router {
    this.add("PATCH", path, handler);
    return this;
  }

  private add(method: string, path: string, handler: Handler) {
    if (!path.includes(":") && !path.includes("*")) {
      if (!this.staticRoutes.has(path)) {
        this.staticRoutes.set(path, new Map());
      }

      if (this.staticRoutes.get(path)!.has(method)) {
        throw new Error(`Route ${method} ${path} has already been registered`);
      }

      this.staticRoutes.get(path)!.set(method, handler);
      return;
    }

    const parts = path.split("/").filter(Boolean);
    let node = this.root;

    for (const part of parts) {
      if (part.startsWith(":")) {
        if (!node.children.has(":param")) {
          node.children.set(":param", new TrieNode());
          node.children.get(":param")!.paramKey = part.slice(1);
        }
        node = node.children.get(":param")!;
      } else if (part === "*") {
        if (!node.wildcard) {
          node.wildcard = new TrieNode();
        }
        node = node.wildcard;
      } else {
        if (!node.children.has(part)) {
          node.children.set(part, new TrieNode());
        }
        node = node.children.get(part)!;
      }
    }

    if (node.handlers.has(method)) {
      throw new Error(`Route ${method} ${path} has already been registered`);
    }

    node.handlers.set(method, handler);
  }

  find(req: Request): { handler?: Handler; c: Context } {
    const { method } = req;
    const url = new URL(req.url);
    const path = url.pathname;

    // 1️⃣ Fast O(1) lookup for static routes
    if (this.staticRoutes.has(path)) {
      const methodHandlers = this.staticRoutes.get(path)!;
      const handler = methodHandlers.get(method);
      return { handler, c: new Context(req) };
    }

    // 2️⃣ Cached lookup for previously resolved paths
    const cacheKey = `${method} ${path}`;
    if (this.resolvedRoutes.has(cacheKey)) {
      // Move accessed key to the end (mark as most recently used)
      const cached = this.resolvedRoutes.get(cacheKey)!;
      this.resolvedRoutes.delete(cacheKey);
      this.resolvedRoutes.set(cacheKey, cached);
      return { handler: cached.handler, c: new Context(req, cached.params) };
    }

    // 3️⃣ Trie traversal for dynamic routes
    const parts = path.split("/").filter(Boolean);
    let node: TrieNode | undefined = this.root;
    let params: Record<string, string> = {};

    for (const part of parts) {
      if (node!.children.has(part)) {
        node = node!.children.get(part);
      } else if (node!.children.has(":param")) {
        let paramNode = node!.children.get(":param")!;
        params[paramNode.paramKey!] = part;
        node = paramNode;
      } else if (node!.wildcard) {
        node = node!.wildcard;
        break;
      } else {
        return { handler: undefined, c: new Context(req) };
      }
    }

    const handler = node!.handlers.get(method);

    // 4️⃣ Cache resolved dynamic routes
    if (this.resolvedRoutes.size >= this.MAX_CACHE_SIZE) {
      const firstKey = this.resolvedRoutes.keys().next().value;
      if (firstKey !== undefined) { // ✅ Fix: Ensure firstKey is not undefined
        this.resolvedRoutes.delete(firstKey);
      }
    }
    this.resolvedRoutes.set(cacheKey, { handler, params });

    return { handler, c: new Context(req, params) };
  }
}
