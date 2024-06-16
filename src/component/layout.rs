
use crate::component::header::header;
use crate::component::header::admin_header;
use crate::component::nav::admin_nav_menu;
use crate::component::misc::main_loader;

use super::misc::overlay;

pub struct PropsLayoutBase<'a> {
    pub title: &'a str,
    pub header: &'a str,
    pub nav_menu: &'a str,
    pub overlay: &'a str,
    pub loader: &'a str,
    pub content: &'a str,
}

pub fn layout_base(props: PropsLayoutBase) -> String {
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
            {}{}{}{}
            <main class='p-6'>{}</main>
            <script>aktrRouter.hydrate(window.location.pathname)</script>
        </body>
        </html>
    "#, props.title, props.header, props.nav_menu, props.loader, props.overlay, props.content);
}

pub fn layout_guest(title: &str, _path: &str, content: &str) -> String {
    return layout_base(PropsLayoutBase {
        title: title,
        header: &header(""),
        nav_menu: "",
        overlay: &overlay("overlay"),
        loader: &main_loader("main-loader"),
        content: content,
    });
}

pub fn layout_admin(title: &str, path: &str, content: &str) -> String {
    return layout_base(PropsLayoutBase {
        title: title,
        header: &admin_header(),
        nav_menu: &admin_nav_menu(path),
        overlay: &overlay("overlay"),
        loader: &main_loader("main-loader"),
        content: content,
    });
}