use sedaro_nano_queries::grammar;
use std::io::{read_to_string, stdin};

fn main() {
    let input =
        read_to_string(stdin()).unwrap_or_else(|err| panic!("Could not read input stream! {err}"));
    let parser = grammar::QueryParser::new();
    let query = parser
        .parse(&input)
        .unwrap_or_else(|err| panic!("Could not parse input! {err}"));
    let output = serde_json::to_string(&query).unwrap();
    print!("{output}")
}
