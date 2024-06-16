use serde::Deserialize;
use serde::Serialize;



#[derive(Debug, Serialize, Deserialize)]
pub struct JTWClaims {
    pub session_token: String,
    pub exp: usize,
}
