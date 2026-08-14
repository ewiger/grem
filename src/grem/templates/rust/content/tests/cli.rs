//! Integration tests exercise {{ project_name }} through its public API.

use {{ package_name }}::{NAME, greeting};

#[test]
fn greeting_mentions_the_project() {
    let message = greeting("world");

    assert!(message.starts_with("Hello, world!"));
    assert!(message.contains(NAME));
}
