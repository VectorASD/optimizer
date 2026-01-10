import sys
sys.path += ("external/pegen/src",)

from pegen import build

import os
from importlib.machinery import SourceFileLoader
from typing import Any

generated_dir = "generated"

grammar_file = os.path.join(os.path.dirname(__file__), "external", "pegen", "data", "python.gram")
output_file = os.path.join(generated_dir, "generated_parser.py")
# os.path.exists(grammar_file)

if not os.path.exists(output_file):
    os.makedirs(generated_dir, exist_ok=True)
    grammar, parser, tokenizer, gen = build.build_python_parser_and_generator(grammar_file, output_file)
    # print("grammar:", grammar)
    # print("parser:", parser)
    # print("tokenizer:", tokenizer)
    # print("gen:", gen)

loader = SourceFileLoader("py_parser", output_file)
py_parser = loader.load_module()

def parse_it(source: str) -> Any:
    ast = py_parser.parse_string(source, mode="exec", py_version=(3, 12), token_stream_factory=None, verbose=False)
    return ast

if __name__ == "__main__":
    source = """
print("meow!")
    """
    ast = parse_it(source)
    print(ast)
