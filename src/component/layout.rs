
use crate::component::header::header;
use crate::component::header::admin_header;
use crate::component::nav::admin_nav_menu;

pub fn layout_base(title: &str, header: &str, nav_menu: &str, content: &str) -> String {
    return format!(/*html*/r#"
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="/static/css/output.css">
            <link rel="stylesheet" href="/static/css/aktr-animate.css">
            <script src="https://unpkg.com/htmx.org@1.9.12"></script>
            <script src="/static/js/index.js"></script>
            <title>{} - CFA Suite</title>
        </head>
        <body hx-boost='true'>
            {}{}
            <main class='p-6'>{}</main>
            <script>aktrRouter.hydrate(window.location.pathname)</script>
        </body>
        </html>
    "#, title, header, nav_menu, content);
}

pub fn layout_guest(title: &str, _path: &str, content: &str) -> String {
    return layout_base(title, &header(""), "", content);
}

pub fn layout_admin(title: &str, path: &str, content: &str) -> String {
    return layout_base(title, &admin_header(), &admin_nav_menu(path), content);
}