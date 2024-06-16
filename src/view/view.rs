use std::collections::HashMap;
use std::sync::Arc;
use time::Duration;

use axum::extract::Query;
use axum::http::{Uri, header::{HeaderMap, SET_COOKIE}};
use axum::response::{Html, IntoResponse, Redirect};
use axum::Extension;
use cookie::Cookie;

use crate::component::form::form_login;
use crate::component::layout::{layout_admin, layout_guest};
use crate::state::state::AppState;

pub async fn home(
    Extension(_shared_state): Extension<Arc<AppState>>, 
    Query(params): Query<HashMap<String, String>>,
    uri: Uri,
) -> impl IntoResponse {
    let mut login_err = "";
    if let Some(value) = params.get("login_err") {
        login_err = value;
    }
    Html(layout_guest("Home", uri.path(),  &format!("{}",
        form_login(login_err),
    )))
}

pub async fn admin_panel(
    Extension(_shared_state): Extension<Arc<AppState>>,
    uri: Uri,
) -> impl IntoResponse {
    Html(layout_admin("Admin", uri.path(), &format!("",

    )))
}

pub async fn logout(
    Extension(_shared_state): Extension<Arc<AppState>>,
) -> impl IntoResponse {
    let cookie = Cookie::build("session", "")
        .path("/")
        .max_age(Duration::seconds(0))
        .finish();
    let mut headers = HeaderMap::new();
    headers.insert(SET_COOKIE, cookie.to_string().parse().unwrap());
    (headers, Redirect::to("/"))
}

pub async fn not_found() -> impl IntoResponse {
    "Not Found!"
}
