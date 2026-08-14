//! Library core for {{ project_name }}.
//!
//! Behavior lives here so it can be tested directly; `src/main.rs` stays a thin
//! command-line shell over this API.

#![forbid(unsafe_code)]

/// The project name recorded when grem stamped this crate.
pub const NAME: &str = "{{ project_name }}";

/// Build the greeting the command-line shell prints for `who`.
pub fn greeting(who: &str) -> String {
    format!("Hello, {who}! This is {NAME}.")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn greeting_names_the_caller() {
        assert!(greeting("world").starts_with("Hello, world!"));
    }
}
