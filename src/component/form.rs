

pub fn template_form(title: &str, action: &str, err: &str, content: &str) -> String {
    let lower_title = title.to_lowercase();
    return format!(/*html*/r#"
            <form id='{}-form' class='flex flex-col gap-12' action="{}" method="POST">
                <h2 class='text-2xl font-semibold'>{}</h2>
                {}{}
            </form>
        "#,
        lower_title,
        action,
        title,
        form_err(err),
        content,
    );
}

pub fn form_err(err: &str) -> String {
    let mut err_html = format!(r#"
            <p class='form-err text-sm text-error'>{}</p>
        "#, 
    err);
    if err == "" {
        err_html = String::from("<p class='form-err text-sm text-error invisible'>invisible</p>");
    }
    return err_html;
}

pub fn form_login(err: &str) -> String {
    return template_form("Login", "/", err, &format!(/*html*/r#"{}{}{}"#,
        form_input("text", "Email", "email"),
        form_input("password", "Password", "password"),
        form_submit("Login"),
    ));
}

pub fn form_input(input_type: &str, label: &str, name: &str) -> String {
    return format!(/*html*/r#"
        <div class='flex flex-col gap-1'>
            <label class='text-sm' for="{}">{}</label>
            <input type="{}" name="{}" autocomplete="current-{}" class='px-2 py-1 text-sm border border-gray-100 transition duration-200 focus:outline-none focus:border-gray-500 rounded'>
        </div>
    "#, name, label, input_type, name, name);
}

pub fn form_submit(label: &str) -> String {
    return format!(/*html*/r#"
        <button type="submit" class='p-2 border focus:outline-none bg-primary text-sm rounded text-white transition duration-200 focus:ring-2 focus:ring-primary focus:ring-opacity-50'>{}</button>
    "#, label);
}

