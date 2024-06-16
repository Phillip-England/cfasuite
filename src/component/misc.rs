

pub fn overlay(id: &str) -> String {
    return format!(/*html*/r#"
        <div id='{}' class='absolute hidden opacity-0 top-0 bg-black opacity-50 h-full w-full z-20'></div>
    "#, id);
}