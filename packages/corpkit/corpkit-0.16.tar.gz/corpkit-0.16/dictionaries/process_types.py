#!/usr/bin/python

#   dictionaries: process type wordlists
#   Author: Daniel McDonald

# Author's note: 

# This list of process types, and entire associated method, is very simplistic. 
# It comes from what Mick O'Donnell (genius behind UAM Corpus Tool) sent me.
# Unlike UAM Corpus Tool, there is no disambiguation of senses based on grammatical features. It's best considered a heuristic, at this point.
# These are useful when the Tregex query is already very precise, 
# and you just want to cut down the kinds of /VB.?/.
# In truth, this file represents one of the most obviously evil things I have ever done.

# Also, there is no material process list, because I haven't figured out how to do it yet. Currently, I just use:

# r'/VB.?/ !< %s !< %s !< %s' % (processes.relational, processes.verbal, processes.mental)

# Also, I'm starting to wonder if I should just use list comprehension *after*
# Tregex does its search. Perhaps there could be a list of filters to be passed 
# to interrogator(), like 'relational only', 'usa english', etc.?

def process_types():
    """This function takes lists of regular and irregular process verbs
    and turns them into regexes. These can then be piped into Tregex queries, etc."""
    import collections
    
    irregular_relational_processes = ["become", "becomes", "became", "become", "becoming", "appear", "appears", "feel", "feels", "felt", "feeling", "smell", "smells", "smelled", "smelt", "smelling", "be", "was", "been", "being", "are", "were", "is", "am", "[^a-z]s", "[^a-z]m", "[^a-z]re", "have", "has", "had", "had", "having", "[^a-z]d", "[^a-z]ve"]
    regular_relational_processes = ["sound", "look", "seem", "appear"]
    irregular_verbal_processes = ['certify', 'certifies', 'certified', 'certified', 'certifying', 'deny', 'denies', 'denied', 'denied', 'denying', 'forbid', 'forbids', 'forbade', 'forbidden', 'forbidding', 'foretell', 'foretells', 'foretold', 'foretold', 'foretelling', 'forswear', 'forswears', 'forswore', 'forsworn', 'forswearing', 'imply', 'implies', 'implied', 'implied', 'implying', 'move', 'moves', 'moved', 'moved', 'moving', 'notify', 'notifies', 'notified', 'notified', 'notifying', 'prophesy', 'prophesies', 'prophesied', 'prophesied', 'prophesying', 'reply', 'replies', 'replied', 'replied', 'replying', 'say', 'says', 'said', 'said', 'saying', 'specify', 'specifies', 'specified', 'specified', 'specifying', 'swear', 'swears', 'swore', 'sworn', 'swearing', 'tell', 'tells', 'told', 'told', 'telling', 'write', 'writes', 'wrote', 'written', 'writing']
    regular_verbal_processes = ['accede', 'add', 'admit', 'advise', 'advocate', 'allege', 'announce', 'answer', 'apprise', 'argue', 'ask', 'assert', 'assure', 'attest', 'aver', 'avow', 'bark', 'beg', 'bellow', 'blubber', 'boast', 'brag', 'cable', 'claim', 'comment', 'complain', 'confess', 'confide', 'confirm', 'contend', 'convey', 'counsel', 'declare', 'demand', 'disclaim', 'disclose', 'divulge', 'emphasise', 'emphasize', 'exclaim', 'explain', 'forecast', 'gesture', 'grizzle', 'guarantee', 'hint', 'holler', 'indicate', 'inform', 'insist', 'intimate', 'mention', 'moan', 'mumble', 'murmur', 'mutter', 'note', 'object', 'offer', 'phone', 'pledge', 'preach', 'predicate', 'preordain', 'proclaim', 'profess', 'prohibit', 'promise', 'propose', 'protest', 'reaffirm', 'reassure', 'rejoin', 'remark', 'remind', 'repeat', 'report', 'request', 'require', 'respond', 'retort', 'reveal', 'riposte', 'roar', 'scream', 'shout', 'signal', 'state', 'stipulate', 'telegraph', 'telephone', 'testify', 'threaten', 'vow', 'warn', 'wire', 'reemphasise', 'reemphasize', 'rumor', 'rumour']
    irregular_mental_processes = ['choose', 'chooses', 'chose', 'chosen', 'choosing', 'dream', 'dreams', 'dreamed', 'dreamt', 'dreaming', 'fancy', 'fancies', 'fancied', 'fancying', 'feel', 'feels', 'felt', 'feeling', 'find', 'finds', 'found', 'finding', 'figure', 'figures', 'figured', 'figuring', 'forget', 'forgets', 'forgot', 'forgotten', 'forgetting', 'hear', 'hears', 'heard', 'hearing', 'know', 'justify', 'justifies', 'justified', 'justifying', 'knows', 'knew', 'known', 'knowing', 'learn', 'learns', 'learned', 'learnt', 'learning', 'mean', 'means', 'meant', 'meaning', 'overhear', 'overhears', 'overheard', 'overhearing', 'prove', 'proves', 'proved', 'proven', 'proving', 'read', 'reads', 'see', 'sees', 'saw', 'seen', 'seeing', 'smell', 'smells', 'smelled', 'smelt', 'smelling', 'think', 'thinks', 'thought', 'thinking', 'understand', 'understands', 'understood', 'understanding', 'worry', 'worries', 'worried', 'worrying']
    regular_mental_processes = ['abide', 'abominate', 'accept', 'acknowledge', 'acquiesce', 'adjudge', 'adore', 'affirm', 'agree', 'allow', 'allure', 'anticipate', 'appreciate', 'ascertain', 'aspire', 'assent', 'assume', 'begrudge', 'believe', 'calculate', 'care', 'conceal', 'concede', 'conceive', 'concern', 'conclude', 'concur', 'condone', 'conjecture', 'consent', 'consider', 'contemplate', 'convince', 'crave', 'decide', 'deduce', 'deem', 'delight', 'desire', 'determine', 'detest', 'discern', 'discover', 'dislike', 'doubt', 'dread', 'enjoy', 'envisage', 'estimate', 'excuse', 'expect', 'exult', 'fear', 'foreknow', 'foresee', 'gather', 'grant', 'grasp', 'hate', 'hope', 'hurt', 'hypothesise', 'hypothesize', 'imagine', 'infer', 'inspire', 'intend', 'intuit', 'judge', 'ken', 'lament', 'like', 'loathe', 'love', 'marvel', 'mind', 'miss', 'need', 'neglect', 'notice', 'observe', 'omit', 'opine', 'perceive', 'plan', 'please', 'posit', 'postulate', 'pray', 'preclude', 'prefer', 'presume', 'presuppose', 'pretend', 'provoke', 'realize', 'realise', 'reason', 'recall', 'reckon', 'recognise', 'recognize', 'recollect', 'reflect', 'regret', 'rejoice', 'relish', 'remember', 'resent', 'resolve', 'rue', 'scent', 'scorn', 'sense', 'settle', 'speculate', 'suffer', 'suppose', 'surmise', 'surprise', 'suspect', 'trust', 'visualise', 'visualize', 'want', 'wish', 'wonder', 'yearn', 'rediscover']

    def regex_maker(irregular, regular):
        """makes a regex from the list of words passed to it"""
        suffixes = ['s', 'es', 'ed', 'ing', '']    
        return r'(?i)^((%s)(%s)|(%s))$' % ( '{1,2}|'.join(regular) + '{1,2}', '|'.join(suffixes), '|'.join(irregular))
    
    list_of_regexes = []
    for process_type in [[irregular_relational_processes, regular_relational_processes], [irregular_mental_processes, regular_mental_processes], [irregular_verbal_processes, regular_verbal_processes]]:
        as_regex = regex_maker(process_type[0], process_type[1])
        list_of_regexes.append(as_regex)

        #regex_list = [regex_maker(process_type) for process_type in [relational_processes, mental_processes, verbal_processes]]
        # implement material process as any word not on this list?

    outputnames = collections.namedtuple('processes', ['relational', 'mental', 'verbal'])
    output = outputnames(list_of_regexes[0], list_of_regexes[1], list_of_regexes[2])
    return output

processes = process_types()
