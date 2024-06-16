# go-quickstart
go-quickstart is a small layer over the standard http library in Go to make building routes and chaining middleware as simple as possible

## Requirements
Go version 1.22.0 or greater required

### Tailwind
This repo comes with a script to run tailwind at `/tailwind.sh` but you'll need to install the [tailwind binary](https://tailwindcss.com/blog/standalone-cli) and place it somewhere on your system's PATH.

Make sure the binary is named, `tailwindcss`.

## Installation
Clone the repo:
```bash
git clone https://github.com/phillip-england/go-quickstart <your-app-name>
```

## Serving
From the root of your app run:
```bash
go run main.go
```
The application server on `localhost:8080` by default. This can be easliy changed in `main.go`.

## Features
Here is an overview of the provided features.

### Router
A router can be created:
```go
r, err := route.NewRouter()
if err != nil {
    panic(err)
}
```

Routes can be added:
```go
r.Add("GET /", handler.HandleHome)
```

Then serve your app:
```go
port := "8080"
r.Serve(port, fmt.Sprintf("Server is running on port %s", port))
```

### Handlers
Here is a simple `Handler`:
```go
func HandleHome(httpContext *httpcontext.Context, w http.ResponseWriter, r *http.Request) {
	err := httpContext.Templates.ExecuteTemplate(w, "base.html", templates.BasePageData{
		Title:   "Home",
		Content: templates.ExecuteTemplate(httpContext.Templates, "hello-world.html", nil),
	})
	if err != nil {
		fmt.Println(err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
}
```

It simply executes a few templates found in `/html` and checks for any errors.


Handlers are functions with the following definition:
```go
type HandlerFunc func(ctx *httpcontext.Context, w http.ResponseWriter, r *http.Request)
```

Notice how the `HandlerFunc` takes in a `*httpcontext.Context`? This just enables you to share data between your middleware and handler.

To add more values to your context, simply update `./internal/httpcontext/httpcontext.go`:
```go
type Context struct {
	context.Context
	Templates *template.Template
	StartTime time.Time
    NewContextValue string // new value added
}
```

Now the `NewContextValue` can be set and shared amoung your middleware and handler.

### Middleware

Middleware can be "chained" onto handlers:
```go
func CustomMiddleware(ctx *httpcontext.Context, w http.ResponseWriter, r *http.Request) error {
	fmt.Println("Executing custom middleware")
	return nil
}

r.Add("GET /", handler.HandleHome, CustomMiddleware) // chaining middleware
```

You can even chain the same middleware multiple times:
```go
r.Add("GET /", handler.HandleHome, CustomMiddleware, CustomMiddleware)
```

The definition for `MiddlewareFunc` is exactly like `HandlerFunc` except `MiddlewareFunc` can return an error:
```go
type MiddlewareFunc func(ctx *httpcontext.Context, w http.ResponseWriter, r *http.Request) error
```

If a `MiddlewareFunc` returns an error, the request/response cycle will exit:
```go
func ExitMiddleware(ctx *httpcontext.Context, w http.ResponseWriter, r *http.Request) error {
	w.Write([]byte("exiting from middleware\n"))
	return errors.New("exit!")
}
r.Add("GET /exit", handler.HandleHome, CustomMiddleware, ExitMiddleware)
```