#!/usr/bin/env python
#-*- coding:utf-8 -*-

import tcf

corpus = tcf.TextCorpus(open('tcf04-karin-wl.xml', 'rb').read())
print('## Corpus:')
print(corpus)
print('## Tokens:')
for token in corpus.tokens:
    print(token, token.lemma, token.tag, token.postag)
    if token.wordsenses:
    	print(token.wordsenses)
    entity_info = []
    if token.reference:
        entity_info.append(token.reference.entity)
        if token.reference.target:
            entity_info.append(token.reference.target)
    if token.entity:
        entity_info.append(token.entity.class_)
    if entity_info:
        print(*entity_info)
print('## Sentences:')
for sentence in corpus.sentences:
    print(' '.join([token.text for token in sentence.tokens]))
print('## Textstructure:')
for span in corpus.textstructure:
    print(span.type, ' '.join([token.text for token in span.tokens]))
for span in [span for span in corpus.textstructure if span.type == 'line']:
    print(' '.join([token.text for token in span.tokens]))
print('## Dependency:')
for parse in corpus.depparsing:
    for dep in parse:
        print('{} --({})-> {}'.format([t.id for t in dep.gov_tokens],
                                       dep.func,
                                       [t.id for t in dep.dep_tokens]))
print('## Dependency Tree')
for parse in corpus.depparsing:
    root = parse.root
    for dep in parse.find_dependents(root):
        print('{} --> {}'.format(root.id, dep.id))