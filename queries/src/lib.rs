use lalrpop_util::lalrpop_mod;
use serde::{Deserialize, Serialize};

lalrpop_mod!(pub grammar);

#[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(tag = "kind", content = "content")]
pub enum Query {
    Prev(Box<Query>),
    Root,
    Agent(String),
    Access { base: Box<Query>, field: String },
    Base(String),
    Tuple(Vec<Query>),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test() {
        // NOTE: This test gives and example input/output pair for the parser.
        let input = "prev!(time)";
        let expected_output = r#"{"kind":"Prev","content":{"kind":"Base","content":"time"}}"#;

        let parser = grammar::QueryParser::new();
        let query = parser
            .parse(input)
            .unwrap_or_else(|err| panic!("Could not parse input! {err}"));
        let output = serde_json::to_string(&query).unwrap();

        assert_eq!(output, expected_output);
    }
}
