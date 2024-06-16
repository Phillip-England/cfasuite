

pub fn template_nav(nav_items: &str) -> String {
    return format!(/*html*/r#"
        <nav id='nav' class='flex flex-col hidden opacity-0 border-r absolute bg-white top-0 left-0 w-[75%] h-full z-30'>
            <div class='flex items-center p-4 border-b'>
                <img class='w-[150px]' src="/static/img/logo.svg" alt="CFA Suite Logo">
            </div>
            <ul class='flex flex-col gap-1 p-1'>{}</ul>
        </nav>
        {}
    "#, nav_items, nav_overlay());
}

pub fn admin_nav_menu(path: &str) -> String {
    return format!(/*html*/r#"{}"#,
        template_nav(&format!(r#"{}{}"#,
            nav_item("Admin Panel", "/admin", path),
            nav_item("Logout", "/logout", path),
        )
    ));
}

pub fn nav_item(title: &str, href: &str, path: &str) -> String {
    let active_class = if path == href { "bg-gray-100" } else { "" };
    return format!(/*html*/r#"
        <li class='flex border rounded {}'>
            <a class='p-4 w-full' href="{}">{}</a>
        </li>
    "#, active_class, href, title);
}

pub fn nav_overlay() -> String {
    return format!(/*html*/r#"
        <div id='nav-overlay' class='absolute hidden opacity-0 top-0 bg-black opacity-50 h-full w-full z-20'></div>
    "#);
}