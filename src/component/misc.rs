

pub fn overlay(id: &str) -> String {
    return format!(/*html*/r#"
        <div id='{}' class='absolute hidden opacity-0 top-0 bg-black opacity-50 h-full w-full z-20'></div>
    "#, id);
}

pub fn main_loader(id: &str) -> String {
    return format!(/*html*/r#"
        <div id='{}' class='fixed hidden opacity-0 top-0 left-0 w-full h-full z-30 flex justify-center'>
            <div class='rounded-full border-8 border-t-8 border-t-primary relative top-[100px] animate-spin border-black h-32 w-32'></div>
        </div>
    "#, id);
}