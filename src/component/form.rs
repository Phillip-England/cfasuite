

pub struct PropsTemplateForm<'a> {
    pub title: &'a str,
    pub action: &'a str,
    pub err: &'a str,
    pub content: &'a str,
}

pub fn template_form(props: PropsTemplateForm) -> String {
    let lower_title = props.title.to_lowercase();
    return format!(/*html*/r#"
            <form id='{}-form' class='flex flex-col gap-12' action="{}" method="POST">
                <h2 class='text-2xl font-semibold'>{}</h2>
                {}{}
            </form>
        "#,
        lower_title,
        props.action,
        props.title,
        form_err(props.err),
        props.content,
    );
}

pub fn form_login(err: &str, email: &str) -> String {
    return template_form(PropsTemplateForm {
        title: "Login",
        action: "/",
        err: err,
        content: &format!(r#"{}{}{}"#,
            form_input(PropsFormInput {
                input_type: "text",
                label: "Email",
                name: "email",
                value: email,
            }),
            form_input(PropsFormInput {
                input_type: "password",
                label: "Password",
                name: "password",
                value: "",
            }),
            form_submit("Login"),
        ),
    });
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

pub struct PropsFormInput<'a> {
    pub input_type: &'a str,
    pub label: &'a str,
    pub name: &'a str,
    pub value: &'a str,
}

pub fn form_input(props: PropsFormInput) -> String {
    return format!(/*html*/r#"
        <div class='flex flex-col gap-1'>
            <label class='text-sm' for="{}">{}</label>
            <input type="{}" name="{}" autocomplete="current-{}" value="{}" class='px-2 py-1 text-sm border border-gray-100 transition duration-200 focus:outline-none focus:border-gray-500 rounded'>
        </div>
    "#, props.name, props.label, props.input_type, props.name, props.name, props.value);
}

pub fn form_submit(label: &str) -> String {
    return format!(/*html*/r#"
        <button type="submit" class='p-2 focus:outline-none bg-primary text-sm rounded text-white transition duration-200 focus:ring-4 focus:ring-primary focus:ring-opacity-50'>{}</button>
    "#, label);
}

