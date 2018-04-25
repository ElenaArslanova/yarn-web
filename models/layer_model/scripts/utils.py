def get_golden(filename, drop_bad_synsets=True, drop_unsure_words=True):
    import re
    with open(filename, 'r', encoding='utf-8') as f:
        raw = f.read()

    raw = raw.strip()

    if drop_bad_synsets:
        raw = re.sub(r'#\d+\n?', '', raw)
    else:
        raw = raw.replace('#', '')

    if drop_unsure_words:
        raw = re.sub(r'\?\w+, |, \?\w+', '', raw)
    else:
        raw = raw.replace('?', '')

    clusters = raw.split('\n\n')
    golden = {}
    for cluster in clusters:
        words, *sIDs = cluster.split('\n')
        words = frozenset(words.split(', '))
        sIDs = set(int(sID) for sID in sIDs if sID)
        golden[words] = sIDs
    return golden