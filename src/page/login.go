package page

import "net/http"

type Login struct {
	LoginErr     string
	HasLoginErr  bool
	RedirectPath string
	TemplateName string
}

func NewLogin(r *http.Request) *Login {
	page := &Login{
		RedirectPath: "/",
		TemplateName: "login.html",
	}
	loginErr := r.URL.Query().Get("loginErr")
	if loginErr != "" {
		page.SetLoginErr(loginErr)
	}
	return page
}

func (p *Login) SetLoginErr(err string) {
	p.HasLoginErr = true
	p.LoginErr = err
	p.RedirectPath = "/?loginErr=" + p.LoginErr
}
