

pub fn header(icons: &str) -> String {
    return format!(/*html*/r#"
        <header class='flex items-center justify-between p-4 border-b border-gray-100'>
            <div class='flex items-center'>
                <img class='w-[150px]' src="/static/img/logo.svg" alt="CFA Suite Logo">
            </div>
            <div class='flex items-center justify-between'>{}</div>
        </header>
    "#, icons);
}

pub fn admin_header() -> String {
    return header(&header_bars())
}


pub fn header_bars() -> String {
    return format!(/*html*/r#"
        <div id='header-bars'>
            <svg class="w-8 h-8" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M5 7h14M5 12h14M5 17h14"/>
            </svg>
        </div>
    "#);
}