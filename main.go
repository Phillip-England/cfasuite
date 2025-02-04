package main

import (
	"html/template"
	"log"
	"net/http"

	"github.com/Phillip-England/cfasuite/src/form"
	"github.com/Phillip-England/cfasuite/src/page"
	"github.com/Phillip-England/vbf"
	"github.com/joho/godotenv"
)

const KeyTemplates = "KEYTEMPLATES"

func main() {

	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	mux, gCtx := vbf.VeryBestFramework()

	strEquals := func(input string, value string) bool {
		return input == value
	}

	funcMap := template.FuncMap{
		"strEquals": strEquals,
	}

	templates, err := vbf.ParseTemplates("./src/page", funcMap)
	if err != nil {
		panic(err)
	}

	vbf.SetGlobalContext(gCtx, KeyTemplates, templates)
	vbf.HandleStaticFiles(mux)
	vbf.HandleFavicon(mux)

	vbf.AddRoute("GET /", mux, gCtx, func(w http.ResponseWriter, r *http.Request) {
		templates, _ := vbf.GetContext(KeyTemplates, r).(*template.Template)
		if r.URL.Path == "/" {
			loginPage := page.NewLogin(r)
			vbf.ExecuteTemplate(w, templates, "login.html", loginPage)
		} else {
			vbf.WriteString(w, "404 not found")
		}
	}, vbf.MwLogger)

	vbf.AddRoute("POST /form/login", mux, gCtx, func(w http.ResponseWriter, r *http.Request) {
		err := r.ParseForm()
		if err != nil {
			http.Error(w, "Error parsing form", http.StatusBadRequest)
			return
		}
		username := r.FormValue("username")
		password := r.FormValue("password")
		loginForm := form.NewLogin(username, password)
		err = loginForm.Validate()
		if err != nil {
			loginPage := page.NewLogin(r)
			loginPage.SetLoginErr(err.Error())
			http.Redirect(w, r, loginPage.Path, 302)
			return
		}
		vbf.ExecuteTemplate(w, templates, "portal.html", nil)
	})

	err = vbf.Serve(mux, "8080")
	if err != nil {
		panic(err)
	}

}

type BaseTemplate struct {
	Title string
}
