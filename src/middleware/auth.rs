use jsonwebtoken::{decode, DecodingKey, Validation};
use tower::{Layer, Service};
use std::convert::Infallible;
use std::task::{Context, Poll};
use std::future::Future;
use std::pin::Pin;
use axum::http::{Request, Response, StatusCode, header};
use crate::security::security::JTWClaims;

// Middleware layer
#[derive(Clone)]
pub struct AuthMiddleware;

impl<S> Layer<S> for AuthMiddleware {
    type Service = AuthService<S>;

    fn layer(&self, service: S) -> Self::Service {
        AuthService { service }
    }
}

// Define the middleware service
#[derive(Clone)]
pub struct AuthService<S> {
    service: S,
}

// Implement the Service trait for the middleware
impl<S, B> Service<Request<B>> for AuthService<S>
where
    S: Service<Request<B>, Response = Response<B>, Error = Infallible> + Clone + Send + 'static,
    S::Future: Send + 'static,
    B: Send + 'static + Default, // Ensure B has a default implementation
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.service.poll_ready(cx)
    }

    fn call(&mut self, req: Request<B>) -> Self::Future {
        // get the value of session token cookie
        let admin_session_token = req
            .headers()
            .get("cookie")
            .and_then(|cookie| {
                let cookie = cookie.to_str().ok()?;
                let cookie = cookie.split(';').collect::<Vec<&str>>();
                let session_token = cookie.iter().find(|cookie| cookie.contains("session="))?;
                let session_token = session_token.split('=').collect::<Vec<&str>>();
                session_token.get(1).cloned()
            });
        
        let validation = Validation::default();
        let token_data = decode::<JTWClaims>(
            &admin_session_token.unwrap_or_default(),
            &DecodingKey::from_secret(dotenv!("ADMIN_JWT_SECRET").as_bytes()),
            &validation,
        );

        if token_data.is_err() {
            let res = Response::builder()
                .status(StatusCode::FOUND) // Use 302 Found for redirect
                .header(header::LOCATION, "/") // Set Location header to "/"
                .body(B::default()) // Use B's default implementation for the body
                .unwrap();
            return Box::pin(async move { Ok(res) });
        }

        let fut = self.service.call(req);

        Box::pin(async move {
            let res = fut.await;
            res
        })
    }
}
