use tower::{Layer, Service};
use std::convert::Infallible;
use std::task::{Context, Poll};
use std::time::Instant;
use std::future::Future;
use std::pin::Pin;
use axum::http::{Request, Response, StatusCode};

// Middleware layer
#[derive(Clone)]
pub struct TimingMiddleware;

impl<S> Layer<S> for TimingMiddleware {
    type Service = TimingService<S>;

    fn layer(&self, service: S) -> Self::Service {
        TimingService { service }
    }
}

// Define the middleware service
#[derive(Clone)]
pub struct TimingService<S> {
    service: S,
}

// Implement the Service trait for the middleware
impl<S, B> Service<Request<B>> for TimingService<S>
where
    S: Service<Request<B>, Response = Response<B>, Error = Infallible> + Clone + Send + 'static,
    S::Future: Send + 'static,
    B: Send + 'static,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.service.poll_ready(cx)
    }

    fn call(&mut self, req: Request<B>) -> Self::Future {
        // Check if the request path contains "/static/"
        if let Some(path) = req.uri().path_and_query() {
            if path.as_str().contains("/static/") {
                // Bypass the middleware and directly call the service
                return Box::pin(self.service.call(req));
            }
        }

        // before the request
        let start = Instant::now();
        let uri = req.uri().clone();
        let method = req.method().clone();
        let fut = self.service.call(req);

        Box::pin(async move {
            let res = fut.await;
            // after the request
            let micro_seconds = start.elapsed().as_micros();
            let status = res.as_ref().map(|res| res.status()).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);
            let uri_parts = uri.path_and_query().unwrap().as_str().split('?').collect::<Vec<&str>>();
            let uri = uri_parts[0];
            if micro_seconds < 1000 {
                println!("[{}]-[{}]-[{}]-[{}µs]", status, method, uri, micro_seconds);
                return res;
            }
            println!("[{}]-[{}]-[{}]-[{}ms]", status, method, uri, start.elapsed().as_millis());
            res
        })
    }
}
