# Xerus

HTTP primitives for Bun.

## Installation

```bash
bun add github:phillip-england/xerus
```

## Hello, World

Create an `index.ts` and paste in the following code:

```ts
import { Context, Handler, logger, Router } from "xerus/primitives";

const r = new Router();

r.get(
  "/static/*",
  new Handler(async (c: Context): Promise<Response> => {
    let file = await c.file("." + c.path);
    if (!file) {
      return c.status(404).send("file not found");
    }
    return file;
  }),
);

r.get(
  "/",
  new Handler(async (c: Context): Promise<Response> => {
    return c.html("<h1>Hello, World!</h1>");
  }, logger),
);

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
```

Run the application using:

```bash
bun run --hot index.ts
```

Visit `localhost:8080`

## Router

The `Router` class does one thing: it takes a request, parses it's path, and
gets you the associated `Handler`. That's it. Use it along with `Bun.serve` like
so:

```ts
const r = new Router();

r.get(
  "/",
  new Handler(async (c: Context): Promise<Response> => {
    return c.html("<h1>Hello, World!</h1>");
  }),
);

const server = Bun.serve({
  port: 8080,
  fetch: async (req: Request) => {
    try { // use a try-catch so you can catch all errors in your application
      const { handler, c } = r.find(req); // find the route (and it's context)
      if (handler) {
        return handler.execute(c);
      }
      return c.status(404).send("404 Not Found"); // return a 404 if a route does not exist
    } catch (e: any) { // catch and log all errors
      console.error(e);
      return new Response("internal server error", { status: 500 });
    }
  },
});

console.log(`Server running on ${server.port}`);
```

You can also use routes with parameters like so:

```ts
r.get(
  "/user/:id",
  new Handler(async (c: Context): Promise<Response> => {
    return c.html(`<h1>${c.param("id")}</h1>`);
  }),
);
```

Or you can use a wildcard, like in this example for serving static files from
`./static`:

```ts
r.get(
  "/static/*",
  new Handler(async (c: Context): Promise<Response> => {
    let file = await c.file("." + c.path);
    if (!file) {
      return c.status(404).send("file not found");
    }
    return file;
  }),
);
```

## Handler

The `Handler` class is used to create endpoints for our application. In this
example, we seperate concerns by first creating a handler, then adding it to our
router:

```ts
const r = new Router();

let handleHome = new Handler(async (c: Context): Promise<Response> => {
  return c.html("<h1>Hello, World!</h1>");
});

r.get("/", handlerHome);
```

## MutResponse

In Bun, the `Response` object is immutable. This makes implementing middleware
difficult as different middlewares are unable to make alterations to the
`Response` throughout it's lifecycle.

That is where `MutResponse` comes into play.

You'll mainly work with `MutResponse` via the `Context` object. For example:

```ts
// here we work directly with the Context object
r.get(
  "/",
  new Handler(async (c: Context): Promise<Response> => {
    return c.html("<h1>Hello, World!</h1>");
  }),
);

// here, we access MutResponse directly
r.get(
  "/",
  new Handler(async (c: Context): Promise<Response> => {
    return c.res.header("content-type", "text/html").body(
      "<h1>Hello, World!</h1>",
    ).send();
  }),
);
```

As you can see in the above example, `Context` abstracts on top of
`MutResponse`.

## Context

Each `Handler` instance is given access to a `Context` instance. `Context` is
used to work with the `MutResponse` as well as the `Response` type provided by
the Bun runtime.

`Context` allow us to:

- get, set, and delete cookies
- parse the incoming request body
- get a url param like :id in "/user/:id"
- set the response status code
- set a header in the response
- send an html response
- send a json response
- steam a `ReadableStream` as a response
- send or stream a file as a response
- store and retrieve data from the global store
- get a url query param like name in "/?name=bob"

## Static Files

Serving static files can be accomplished by using a wildcard path `/static/*` in
conjunction with the `Context.file` method.

In this example, I am serving static files from `./static`:

```ts
r.get(
  "/static/*",
  new Handler(async (c: Context): Promise<Response> => {
    let file = await c.file("." + c.path);
    if (!file) {
      // what to do if we can't find the requested file
      return c.status(404).send("file not found");
    }
    return file;
  }),
);
```

## Middleware

`Middleware` can be applied to a route by chaining it on to the end of a
`Handler`. this is the ONLY way to apply `Middleware` to a route, by design.

I made this decision because I do not intend for Xerus to be a fully fledged
framework. Instead, I intend to provide primitives others can use in their own
projects.

Here, I will show you how to create and use the `logger` middleware. This
`Middleware` is provided by Xerus and can be used by importing it, but it
provides a good example of how to use create and use `Middleware`.

First, here is a `Middleware` template for quick use:

```ts
export const logger = new Middleware(async (c: Context, next) => {
  // things that happen before the request
  await next();
  // things that happen after the request
});
```

Then, for our `logger` we can do this:

```ts
export const logger = new Middleware(async (c: Context, next) => {
  const start = performance.now(); // get the start time before the request
  await next();
  const duration = performance.now() - start; // calculate time taken after request
  console.log(`[${c.req.method}][${c.path}][${duration.toFixed(2)}ms]`); // print
});
```

We can then use our `Middleware` by chaining it onto the end of a `Handler`:

```ts
r.get(
  "/",
  new Handler(async (c: Context): Promise<Response> => {
    return c.html("<h1>Hello, World!</h1>");
  }, logger),
); // <====== chain middleware here
```

## Parsing Incoming Requests

`Context` has the `parseBody` method which takes in member from the `BodyType`
enum. We can require the incoming request to have a body of a specific primitive
type. For example, here we enforce the incoming request body to be JSON:

```ts
r.post(
  "/",
  new Handler(async (c: Context): Promise<Response> => {
    let { data, err } = await c.parseBody(BodyType.JSON);
    if (err) {
      return c.status(500).send("failed to parse the request body");
    }
    return c.json({ receivedBody: data });
  }, logger),
);
```

Other options include:

```ts
c.parseBody(BodyType.TEXT);
c.parseBody(BodyType.FORM);
c.parseBody(BodyType.MULTIPART_FORM);
```

## Serving

Xerus applications are served using `Bun.serve`. This is another design decision
made to help keep Xerus a tool to be used in other projects. Xerus just provides
the primitives, you can create the abstractions on top of them.

Here is a simple application served using `Bun.serve`:

```ts
const r = new Router();

r.get(
  "/context",
  new Handler(async (c: Context): Promise<Response> => {
    return c.html("<h1>Hello, World!</h1>");
  }, logger),
);

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
```
