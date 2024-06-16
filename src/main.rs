
mod view;
mod middleware;
mod state;
mod component;
mod security;

use crate::view::view::{
    home,
    not_found,
    admin_panel,
	logout,
};
use crate::view::form_action::login;
use crate::middleware::log::LoggerMiddleware;
use crate::state::state::new_app_state;

use std::sync::Arc;
use axum::Extension;
use axum::{
	routing::get,
    routing::post,
	Router,
};
use middleware::auth::AdminAuthMiddleware;
use middleware::auth::GuestAuthMiddleware;
use tower_http::services::ServeDir;

#[macro_use]
extern crate dotenv_codegen;
#[tokio::main]
async fn main() {

    // loading in env file
    dotenv::dotenv().ok();

	// getting hostname
	let host = "0.0.0.0";
	let addr = format!("{}:{}", host, "8000");

    // setting up shared state
    let shared_state = Arc::new(new_app_state());

    // building admin router
    let admin_routes = Router::new()
        .route("/", get(admin_panel))
        .layer(AdminAuthMiddleware);

    // building guest router
    let guest_routes = Router::new()
        .route("/", get(home))
        .route("/", post(login))
        .layer(GuestAuthMiddleware);

    // building main router
    let app = Router::new()
        .nest("/admin", admin_routes)
        .merge(guest_routes)
        .route("/logout", get(logout))
        .nest_service("/static", ServeDir::new("static"))
        .fallback(get(not_found))
        .layer(LoggerMiddleware)
        .layer(Extension(shared_state));

	// binding and serving
	println!("development server running on {}", addr);
	let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
	axum::serve(listener, app).await.unwrap()


}
