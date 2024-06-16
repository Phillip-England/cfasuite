use std::sync::Arc;

use axum::{http::{header::SET_COOKIE, HeaderMap}, response::{IntoResponse, Redirect}, Extension, Form};
use cookie::Cookie;
use serde::Deserialize;
use time::Duration;
use jsonwebtoken::EncodingKey;

use crate::state::state::AppState;
use crate::security::security::JTWClaims;



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
    let jwt_claims = JTWClaims {
        session_token: dotenv!("ADMIN_SESSION_TOKEN").to_string(),
        exp: (time::OffsetDateTime::now_utc() + time::Duration::days(7)).unix_timestamp() as usize,
    };
    let jwt = jsonwebtoken::encode(
        &jsonwebtoken::Header::default(),
        &jwt_claims,
        &EncodingKey::from_secret(dotenv!("ADMIN_JWT_SECRET").as_bytes()),
    );
    if jwt.is_err() {
        return (headers, Redirect::to(&fail("jwt error", &form.email)));
    }
    let jwt = jwt.unwrap();
    let cookie = Cookie::build("session", jwt)
        .path("/")
        .max_age(Duration::seconds(60 * 60 * 24 * 7))
        .finish();
    let mut headers = HeaderMap::new();
    headers.insert(SET_COOKIE, cookie.to_string().parse().unwrap());
    return (headers, Redirect::to("/admin"));
}