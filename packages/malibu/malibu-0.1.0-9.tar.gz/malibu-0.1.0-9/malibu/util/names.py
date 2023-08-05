#!/usr/bin/env python2.7

import random

__adjectives__ = [ "smelly", "firey", "naughty", "sad", "frazzled", "excited", 
        "gross", "chipper", "nasty", "nosey", "pokey", "frustrated", "glum",
        "bouncy", "electric", "immune", "excited", "perfunctory", "likable",
        "fastidious", "adorable", "charming", "pleasant", "crass", "gloomy",
        "faithful", "spectacular", "diminished", "hurtful", "voltaic", 
        "fervent", "ravishing", "riveting", "peculiar", "cross", "smashed",
        "ridiculous", "pontiferous", "offended", "overzealous", "jealous",
        "freaky", "comical", "creepy", "disturbed", "massive", "bigoted",
        "ecstatic", "rowdy", "friendly", "enlightened", "failing" ]

__nouns__ = [ "feynman", "einstein", "roadrunner", "tacocat", "grump", "fish",
        "michael", "bishop", "charlie", "metcalfe", "babbage", "zuckerberg",
        "nicholas", "priest", "doge", "pimp", "drone", "worker", "voltorb",
        "bulbasaur", "king", "bay", "transformers", "johnson", "baby",
        "charmander", "mew", "axel", "wayne", "charles", "jessica", "clarice",
        "doctor", "horton", "ballmer", "jobs", "gates", "failfish" ]

def get_simple_name():

    adj = random.choice(__adjectives__)
    noun = random.choice(__nouns__)

    return '_'.join([adj, noun])
