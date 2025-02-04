package page

import "net/http"

type Portal struct {
	RedirectPath string
	TemplateName string
}

func NewPortal(r *http.Request) *Portal {
	page := &Portal{
		RedirectPath: "/portal",
		TemplateName: "portal.html",
	}
	return page
}
