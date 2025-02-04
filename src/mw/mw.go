package mw

import (
	"net/http"
	"os"

	"github.com/Phillip-England/cfasuite/src/page"
)

func UserAuth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		loginPage := page.NewLogin(r)
		cookie, err := r.Cookie(os.Getenv("SESSION_TOKEN_NAME"))
		if err != nil {
			// will be hit if a cookie does not exist
			if err == http.ErrNoCookie {
				http.Redirect(w, r, loginPage.RedirectPath, 302)
				return
			}
			// could be hit due to manually crafted cookies or internal issue with net/http
			http.Redirect(w, r, loginPage.RedirectPath, 302)
			return
		}
		if cookie.Value != os.Getenv("SESSION_TOKEN_VALUE") {
			http.Redirect(w, r, loginPage.RedirectPath, 302)
			return
		}
		next.ServeHTTP(w, r)
	})
}
