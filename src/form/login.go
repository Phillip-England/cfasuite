package form

import (
	"fmt"
	"os"
)

type Login struct {
	Username string
	Password string
}

func NewLogin(username string, password string) *Login {
	return &Login{
		Username: username,
		Password: password,
	}
}

func (f *Login) Validate() error {
	if f.Username != os.Getenv("USERNAME") {
		return fmt.Errorf("invalid credentials")
	}
	if f.Password != os.Getenv("PASSWORD") {
		return fmt.Errorf("invalid credentials")
	}
	return nil
}
