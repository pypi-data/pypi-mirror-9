#!/usr/bin/env python

"""Print human-readable information about a Communication to stdout

concrete_inspect.py is a command-line script for printing out information
about a Concrete Communication.
"""

import argparse
import codecs
import sys

import concrete.inspect
import concrete.util


def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="Print information about a Concrete Communication to stdout")
    parser.add_argument("--char-offsets", help="Print token text extracted from character offsets "
                        "(not the text stored in the tokenization) in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--dependency", help="Print HEAD tags for first dependency parse in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--entities", help="Print info about all Entities and their EntityMentions",
                        action="store_true")
    parser.add_argument("--lemmas", help="Print first set of lemma token tags in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--metadata", help="Print metadata for tools used to annotate Communication",
                        action="store_true")
    parser.add_argument("--mentions", help="Print whitespace-separated tokens, with entity mentions wrapped "
                        "using <ENTITY ID=x> tags, where 'x' is the (zero-indexed) entity number",
                        action="store_true")
    parser.add_argument("--ner", help="Print first set of Named Entity Recognition token tags in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--pos", help="Print first set of Part-Of-Speech token tags in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--situation-mentions", help="Print info about all SituationMentions",
                        action="store_true")
    parser.add_argument("--situations", help="Print info about all Situations and their SituationMentions",
                        action="store_true")
    parser.add_argument("--text", help="Print .text field",
                        action="store_true")
    parser.add_argument("--tokens", help="Print whitespace-seperated tokens for *all* Tokenizations in a "
                        "Communication.  Each sentence tokenization is printed on a separate line, and "
                        "empty lines indicate a section break",
                        action="store_true")
    parser.add_argument("--treebank", help="Print Penn-Treebank style parse trees for *all* Constituent "
                        "Parses in the Communication",
                        action="store_true")
    parser.add_argument("communication_file")
    args = parser.parse_args()

    comm = concrete.util.read_communication_from_file(args.communication_file)

    if args.char_offsets or args.dependency or args.lemmas or args.ner or args.pos:
        concrete.inspect.print_conll_style_tags_for_communication(
            comm, char_offsets=args.char_offsets, dependency=args.dependency, lemmas=args.lemmas, ner=args.ner, pos=args.pos)
    elif args.entities:
        concrete.inspect.print_entities(comm)
    elif args.mentions:
        concrete.inspect.print_tokens_with_entityMentions(comm)
    elif args.metadata:
        concrete.inspect.print_metadata(comm)
    elif args.situation_mentions:
        concrete.inspect.print_situation_mentions(comm)
    elif args.situations:
        concrete.inspect.print_situations(comm)
    elif args.text:
        concrete.inspect.print_text_for_communication(comm)
    elif args.tokens:
        concrete.inspect.print_tokens_for_communication(comm)
    elif args.treebank:
        concrete.inspect.print_penn_treebank_for_communication(comm)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
