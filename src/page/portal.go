package page

import "net/http"

type Portal struct {
	RedirectPath string
}

func NewPortal(r *http.Request) *Login {
	page := &Login{
		RedirectPath: "/portal",
	}
	return page
}
