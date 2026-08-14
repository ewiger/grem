//! Command-line entry point for {{ project_name }}.
//!
//! Parse arguments, call into the library, print. Keep logic in `src/lib.rs`.

use clap::Parser;

use {{ package_name }}::greeting;

/// {{ project_name }}
#[derive(Debug, Parser)]
#[command(version, about)]
struct Cli {
    /// Who to greet.
    #[arg(default_value = "world")]
    who: String,
}

fn main() {
    let cli = Cli::parse();

    println!("{}", greeting(&cli.who));
}
