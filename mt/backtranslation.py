import torch
import argparse
import json
import torch
from transformers import MarianTokenizer, MarianMTModel
from typing import List


def load_model(src_lang, tgt_lang, data_src="wmt16"):
    '''
    Loads translation model for both forward and backward directions.
    If multiple sources exist, if specified source exists loads that. Otherwise returns earliest.
    takes specification
    into account.
    :param src_lang:
    :param tgt_lang:
    :param year:
    :return:
    '''
    fwd_mname = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'
    bwd_mname = f'Helsinki-NLP/opus-mt-{tgt_lang}-{src_lang}'

    print(fwd_mname)
    print(bwd_mname)

    fwd_model = MarianMTModel.from_pretrained(fwd_mname)
    fwd_tok = MarianTokenizer.from_pretrained(fwd_mname)

    bwd_model = MarianMTModel.from_pretrained(bwd_mname)
    bwd_tok = MarianTokenizer.from_pretrained(bwd_mname)

    return fwd_model, fwd_tok, bwd_model, bwd_tok


def backtranslate(examples, fwd_model, fwd_tok, bwd_model, bwd_tok, BATCH_SIZE=64):
    '''
    Produce backtranslation for a given piece of text using a given model
    :param examples: list of sentences to be translated
    :param n_translations: Number of backtranslations to generate
    :return: backtranslated examples
    '''

    dev_questions = examples
    backtranslated_examples = []
    n_batches = int(len(dev_questions) / BATCH_SIZE)

    for batch_ind in range(n_batches + 1):
        print(batch_ind)
        batch_questions = dev_questions[batch_ind * BATCH_SIZE:(batch_ind + 1) * BATCH_SIZE]
        batch = fwd_tok.prepare_translation_batch(src_texts=batch_questions)  # don't need tgt_text for inference
        gen = fwd_model.generate(**batch)  # for forward pass: model(**batch)
        translated_examples: List[str] = fwd_tok.batch_decode(gen, skip_special_tokens=True)

        batch = bwd_tok.prepare_translation_batch(src_texts=translated_examples)
        gen = bwd_model.generate(**batch)  # for forward pass: model(**batch)
        backtranslated_example: List[str] = bwd_tok.batch_decode(gen, skip_special_tokens=True)
        backtranslated_examples += backtranslated_example

    return backtranslated_examples


def read_data(filename):
    f = open(filename, "r")
    all_lines = f.read().strip().split("\n")
    return all_lines


def write_data(examples, write_path):
    f = open(write_path, "w")
    for each_example in examples:
        f.write(each_example + "\n")
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--src_lang", default="en", type=str)
    parser.add_argument("--tgt_lang", default="de", type=str)
    parser.add_argument("--data_src", type=str, help="source data file to perturb with synthetic translation noise")
    parser.add_argument("--data_tgt", type=str, help="target path to dump perturbed data")
    args = parser.parse_args()

    examples = read_data(args.data_src)

    # Get translation models
    fwd_model, fwd_tok, bwd_model, bwd_tok = load_model(args.src_lang, args.tgt_lang, "wmt19")

    # Get perturbed data for every squad instance
    perturbed_dev_examples = backtranslate(examples, fwd_model, fwd_tok, bwd_model, bwd_tok)

    # Write perturbed dataset
    write_data(perturbed_dev_examples, args.data_tgt)
