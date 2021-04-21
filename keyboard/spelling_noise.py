import random
import numpy as np
from transformers.data.processors.squad import SquadResult, SquadV1Processor
import argparse
import json
import re
import numpy as np


def tokenize(string):
    return string.split()


def perturb_word_swap(word):
    if len(word) == 2:
        new_word = word[::-1]
    else:
        char_ind = int(np.random.uniform(0, len(word) - 1))
        new_word = list(word)
        first_char = new_word[char_ind]
        new_word[char_ind] = new_word[char_ind + 1]
        new_word[char_ind + 1] = first_char
        new_word = "".join(new_word)
    return new_word


def perturb_word_kb(word):
    keyboard_char_dict = {"a": ['s'], "b": ['v', 'n'], "c": ['x', 'v'], "d": ['s', 'f'], "e": ['r', 'w'],
                          "f": ['g', 'd'], "g": ['f', 'h'], "h": ['g', 'j'], "i": ['u', 'o'], "j": ['h', 'k'],
                          "k": ['j', 'l'], "l": ['k'], "m": ['n'], "n": ['m', 'b'], "o": ['i', 'p'], "p": ['o'],
                          "q": ['w'], "r": ['t', 'e'], "s": ['d', 'a'], "t": ['r', 'y'],
                          "u": ['y', 'i'], "v": ['c', 'b'], "w": ['e', 'q'], "x": ['z', 'c'], "y": ['t', 'u'],
                          "z": ['x']}
    if len(word) > 1:
        new_word = list(word)
        acceptable_subs = []
        for ind, each_char in enumerate(new_word):
            if each_char in keyboard_char_dict.keys():
                acceptable_subs.append(ind)

        if len(acceptable_subs) == 0:
            return None

        char_ind = random.choice(acceptable_subs)

        first_char = new_word[char_ind]

        new_word[char_ind] = random.choice(keyboard_char_dict[first_char])
        final_new_word = "".join(new_word)
        return final_new_word


def write_data(examples, tgt_file):
    '''

    :param examples:
    :return:
    '''

    json_examples = {"data":{}}

    for example in examples:
        if example.title not in json_examples["data"]:
            json_examples["data"][example.title] = {}

        if example.context_text not in json_examples["data"][example.title]:
            json_examples["data"][example.title][example.context_text] = []

        entry = {"id":example.qas_id,\
                 "question":example.question_text,\
                 "context_text":example.context_text,\
                 "answer_text":example.answer_text,\
                 "start_position":example.start_position, \
                 "end_position": example.end_position,
                 "title":example.title,\
                 "answers":example.answers}

        json_examples["data"][example.title][example.context_text].append(entry)


    question_count = 0

    squad_format = {"data":[]}
    for each_title in json_examples["data"]:
        entry = {"title":each_title,"paragraphs":[]}
        for each_paragraph in json_examples["data"][each_title]:
            paragraph_entry = {"context":each_paragraph, "qas":[]}
            for each_entry in json_examples["data"][each_title][each_paragraph]:
                paragraph_entry["qas"].append(each_entry)
                question_count+=1
            entry["paragraphs"].append(paragraph_entry)
        squad_format["data"].append(entry)


    print(question_count)
    print(len(examples))

    json.dump(squad_format, open(tgt_file, "w"))


def perturb_spelling(examples, replacement_prob=1.0):
    perturbed_examples = []

    for sample in examples:

        sentence = tokenize(sample)

        perturbed_sentence = []
        for word in sentence:


            replacement = np.random.choice([0,1],p=[1.0-replacement_prob, replacement_prob])

            if replacement == 1:
                perturbed_word = perturb_word_kb(word)

                # If there are no characters that can be misspelt by keyboard swap
                if perturbed_word is None:
                    perturbed_word = word
            else:
                perturbed_word = word

            perturbed_sentence.append(perturbed_word)

        try:
            perturbed_examples.append(" ".join(perturbed_sentence))
        except Exception as e:
            import pdb
            pdb.set_trace()

    return perturbed_examples

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

    parser.add_argument("--noise_type", default="kb", type=str)
    parser.add_argument("--data_src", type=str, help="source data file to perturb with synthetic translation noise")
    parser.add_argument("--data_tgt", type=str, help="target path to dump perturbed data")
    parser.add_argument("--replacement_prob", type=float, default=1.0, help="Probability of perturbing a word")
    args = parser.parse_args()

    examples = read_data(args.data_src)
    perturbed_examples = perturb_spelling(examples, replacement_prob=0.25)

    # # Get perturbed data for every squad instance
    # perturbed_dev = []
    # for each_example in dev_examples:
    #     perturbed_question = perturb_spelling([each_example.question_text], replacement_prob= args.replacement_prob)
    #     each_example.question_text = perturbed_question[0]

    # Write perturbed dataset
    write_data(perturbed_examples, args.data_tgt)
