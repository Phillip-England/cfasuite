use std::sync::Arc;

use axum::{http::{header::SET_COOKIE, HeaderMap}, response::{IntoResponse, Redirect}, Extension, Form};
use cookie::Cookie;
use serde::Deserialize;
use time::Duration;

use crate::state::state::AppState;



#[derive(Deserialize)]
pub struct LoginForm {
    pub email: String,
    pub password: String,
}

pub async fn login(
    Extension(_shared_state): Extension<Arc<AppState>>,
    Form(form): Form<LoginForm>,
) -> impl IntoResponse {
    let headers = HeaderMap::new();
    fn fail(login_err: &str, email: &str) -> String {
        format!("/?login_err={}&email={}", login_err, email)
    }
    if form.email == "" || form.password == "" {
        return (headers, Redirect::to(&fail("invalid credentails", &form.email)));
    }
    if form.email != dotenv!("ADMIN_EMAIL") && form.password != dotenv!("ADMIN_PASSWORD") {
        return (headers, Redirect::to(&fail("invalid credentails", &form.email)));
    }
    let cookie = Cookie::build("session", dotenv!("ADMIN_SESSION_TOKEN"))
    .path("/")
    .max_age(Duration::seconds(60 * 60 * 24 * 7))
    .finish();
    let mut headers = HeaderMap::new();
    headers.insert(SET_COOKIE, cookie.to_string().parse().unwrap());
    return (headers, Redirect::to("/admin"));
}