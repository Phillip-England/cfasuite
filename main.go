package main

import (
	"html/template"
	"net/http"

	"github.com/Phillip-England/vbf"
)

const KeyTemplates = "KEYTEMPLATES"

func main() {

	mux, gCtx := vbf.VeryBestFramework()

	strEquals := func(input string, value string) bool {
		return input == value
	}

	funcMap := template.FuncMap{
		"strEquals": strEquals,
	}

	templates, err := vbf.ParseTemplates("./templates", funcMap)
	if err != nil {
		panic(err)
	}

	vbf.SetGlobalContext(gCtx, KeyTemplates, templates)
	vbf.HandleStaticFiles(mux)
	vbf.HandleFavicon(mux)

	vbf.AddRoute("GET /", mux, gCtx, func(w http.ResponseWriter, r *http.Request) {
		templates, _ := vbf.GetContext(KeyTemplates, r).(*template.Template)
		if r.URL.Path == "/" {
			vbf.ExecuteTemplate(w, templates, "login.html", nil)
		} else {
			vbf.WriteString(w, "404 not found")
		}
	}, vbf.MwLogger)

	err = vbf.Serve(mux, "8080")
	if err != nil {
		panic(err)
	}

}

type BaseTemplate struct {
	Title string
}
