import { expect, test } from "bun:test";

const BASE_URL = "http://localhost:8080";

test("GET / should return Hello, world!", async () => {
  const res = await fetch(`${BASE_URL}/`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.message).toBe("Hello, world!");
});

test("GET /context/html should return HTML response", async () => {
  const res = await fetch(`${BASE_URL}/context/html`);
  const data = await res.text();
  expect(res.status).toBe(200);
  expect(data).toBe("<h1>Hello, World!</h1>");
});

test("GET /context/json should return JSON response", async () => {
  const res = await fetch(`${BASE_URL}/context/json`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data).toEqual({ testing: "json" });
});

test("POST /context/parseJSON/invalidJSON should return error for invalid JSON", async () => {
  const res = await fetch(`${BASE_URL}/context/parseJSON/invalidJSON`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{invalidJson}",
  });
  const data = await res.text();
  expect(res.status).toBe(500);
  expect(data).toBe("invalid json");
});

test("POST /context/parseJSON/validJSON should return parsed JSON", async () => {
  const res = await fetch(`${BASE_URL}/context/parseJSON/validJSON`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "Hello" }),
  });
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data).toBe("<h1>[object Object]</h1>"); // Ensure this is the expected output
});

test("POST /context/parseText should parse text body", async () => {
  const res = await fetch(`${BASE_URL}/context/parseText`, {
    method: "POST",
    headers: { "Content-Type": "text/plain" },
    body: "Hello, World!",
  });
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.receivedText).toBe("Hello, World!");
});

test("POST /context/parseForm should parse URL-encoded form data", async () => {
  const res = await fetch(`${BASE_URL}/context/parseForm`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "key=value&foo=bar",
  });
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.receivedFormData).toEqual({ key: "value", foo: "bar" });
});

test("POST /context/parseMultipartForm should parse multipart form data", async () => {
  const formData = new FormData();
  formData.append("key", "value");
  formData.append("foo", "bar");

  const res = await fetch(`${BASE_URL}/context/parseMultipartForm`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.receivedMultipartFormData).toEqual({ key: "value", foo: "bar" });
});

test("GET /context/headers should return User-Agent", async () => {
  const res = await fetch(`${BASE_URL}/context/headers`, {
    method: "GET",
    headers: { "User-Agent": "BunTest" },
  });
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.userAgent).toBe("BunTest");
});

test("GET /context/stream-file should return a file", async () => {
  const res = await fetch(`${BASE_URL}/context/stream-file`);
  expect(res.status).toBe(200);
});

const methods = ["PUT", "DELETE", "PATCH"];
methods.forEach((method) => {
  test(`${method} /context/method/${method.toLowerCase()} should return method received`, async () => {
    const res = await fetch(
      `${BASE_URL}/context/method/${method.toLowerCase()}`,
      {
        method,
      },
    );
    const data = await res.json();
    expect(res.status).toBe(200);
    expect(data.message).toBe(`${method} method received`);
  });
});

test("GET /context/params/:id should return parameter value", async () => {
  const res = await fetch(`${BASE_URL}/context/params/123`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.paramValue).toBe("123");
});

test("GET /context/params/:id/details/:detailId should return both parameters", async () => {
  const res = await fetch(`${BASE_URL}/context/params/123/details/456`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data).toEqual({ id: "123", detailId: "456" });
});

test("GET /context/query/multiple should return query parameters with defaults", async () => {
  const res = await fetch(
    `${BASE_URL}/context/query/multiple?key1=foo&key2=bar`,
  );
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data).toEqual({ key1: "foo", key2: "bar" });
});

test("GET /context/status/200 should return 200 OK", async () => {
  const res = await fetch(`${BASE_URL}/context/status/200`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.message).toBe("OK");
});

test("GET /context/status/400 should return 400 Bad Request", async () => {
  const res = await fetch(`${BASE_URL}/context/status/400`);
  const data = await res.json();
  expect(res.status).toBe(400);
  expect(data.error).toBe("Bad Request");
});

test("GET /context/status/500 should return 500 Internal Server Error", async () => {
  const res = await fetch(`${BASE_URL}/context/status/500`);
  const data = await res.json();
  expect(res.status).toBe(500);
  expect(data.error).toBe("Internal Server Error");
});

test("GET /context/headers/custom should return custom header", async () => {
  const res = await fetch(`${BASE_URL}/context/headers/custom`);
  expect(res.headers.get("X-Custom-Header")).toBe("CustomValue");
});

test("GET /context/set-secure-cookie should set secure cookie", async () => {
  const res = await fetch(`${BASE_URL}/context/set-secure-cookie`);
  expect(res.headers.get("set-cookie")).toContain("secureTest=secureValue");
});

test("GET /context/set-expiring-cookie should set expiring cookie", async () => {
  const res = await fetch(`${BASE_URL}/context/set-expiring-cookie`);
  expect(res.headers.get("set-cookie")).toContain("expiringTest=willExpire");
});

test("POST /context/parseBody/empty should return parsed body", async () => {
  const res = await fetch(`${BASE_URL}/context/parseBody/empty`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ test: "data" }),
  });
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.receivedBody).toEqual({ test: "data" });
});

test("POST /context/parseBody/largeJSON should return parsed JSON", async () => {
  const res = await fetch(`${BASE_URL}/context/parseBody/largeJSON`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ large: "json" }),
  });
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.receivedBody).toEqual({ large: "json" });
});

test("GET /context/serve-image should return image file", async () => {
  const res = await fetch(`${BASE_URL}/context/serve-image`);
  expect(res.status).toBe(200);
});

test("GET /context/serve-text-file should return text file", async () => {
  const res = await fetch(`${BASE_URL}/context/serve-text-file`);
  expect(res.status).toBe(200);
});

test("GET /middleware/early-response should return early response", async () => {
  const res = await fetch(`${BASE_URL}/middleware/early-response`);
  const data = await res.text();
  expect(res.status).toBe(200);
  console.log(data);
  expect(data).toBe("hello from middleware");
});

test("GET /middleware/order-test should pass through middleware", async () => {
  const res = await fetch(`${BASE_URL}/middleware/order-test`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.message).toBe("Middleware order test");
});

test("GET /wildcard/* should match wildcard route", async () => {
  const res = await fetch(`${BASE_URL}/wildcard/anything`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.message).toBe("Matched wildcard route for /wildcard/anything");
});

test("GET /wildcard/deep/* should match deep wildcard route", async () => {
  const res = await fetch(`${BASE_URL}/wildcard/deep/anything/here`);
  const data = await res.json();
  expect(res.status).toBe(200);
  expect(data.message).toBe(
    "Matched deep wildcard route for /wildcard/deep/anything/here",
  );
});

test("GET /set-cookies should set multiple cookies", async () => {
  const res = await fetch(`${BASE_URL}/set-cookies`);
  expect(res.status).toBe(200);
  const setCookieHeader = res.headers.getSetCookie();
  expect(setCookieHeader).toBeTruthy();
  expect(setCookieHeader.some((cookie) => cookie.includes("user=john_doe")))
    .toBe(true);
  expect(setCookieHeader.some((cookie) => cookie.includes("session=xyz123")))
    .toBe(true);
});

test("GET /get-cookies should return previously set cookies", async () => {
  await fetch(`${BASE_URL}/set-cookies`);
  const res = await fetch(`${BASE_URL}/get-cookies`, {
    headers: {
      Cookie: "user=john_doe; session=xyz123",
    },
  });
  expect(res.status).toBe(200);
  const data = await res.json();
  expect(data).toEqual({
    user: "john_doe",
    session: "xyz123",
  });
});

test("GET /middleware/modify-context should modify context and return stored value", async () => {
  const res = await fetch(`${BASE_URL}/middleware/modify-context`);
  const data = await res.json();

  expect(res.status).toBe(200);
  expect(data.message).toBe("This was set by middleware!");
});
