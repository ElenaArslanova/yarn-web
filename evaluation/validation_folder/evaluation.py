import numpy as np

def get_mapping_and_clusters():
    '''
    Парсит csv в словари с нужными данными для удобства:
    - mapping = {gID: clusterID}
    - clusters = {clusterID: set(sIDs)}
        
    Здесь 
    gID - id синсета из золотого стандарта
    clusterID - id кластера из предварительной кластеризации YARN
    '''
    with open('mapping.csv') as f:
        mapping = {line.strip().split(';')[0] : int(line.strip().split(';')[1]) for line in f}

    with open('3to9.csv', encoding = 'utf8') as f:
        clusters = {int(line.strip().split(';')[0]) : set(line.strip().split(';')[1].split(',')) for line in f}
    return mapping, clusters

def get_data(file_name):
    '''
    Парсит training\test csv в словарь с нужными данными для удобства:
    pure_synsets = {gID : pure_synset(set of words)}
    '''
    with open(file_name, encoding = 'utf8') as f:
        pure_synsets  = {}
        for line in f:
            gID, _, words = line.strip().split(';')
            words = set(words.split(','))
            pure_synsets[gID] = words
    return pure_synsets

def get_JPRF(ideal, version):
    '''
    Подсчитывает Jaccard, precision, recall, F-score для пары класс - кластер
    '''
    # i - cluster, j - class
    n_ij = len(ideal & version) # Кол-во элементов, вошедших как в кластер, так и в класс
    n_i = len(version)          # Кол-во элементов в кластере
    n_j = len(ideal)            # Кол-во элементов в классе
    P = n_ij/n_i                # Точность   
    R = n_ij/n_j                # Полнота
    J = len(ideal & version) / len(ideal | version)
    try:
        F1 = (2 * P * R) / (P + R)
    except:
        #print(f'P = {P}, R = {R} for ideal {ideal} and version {version}')
        F1 = 0                  # На случай, если вообще нет правильно выбранных элементов
    return J, P, R, F1

def evaluate(results):
    '''
    Принимает коллекцию пар "золотой синсет" - автоматически созданный синсет.
    Возвращает средние Jaccard, precision, recall, F-score для этой коллекции
    '''
    grades = []
    for ideal, version in results:
        scores = get_JPRF(ideal, version)
        grades.append(scores)
    grades = np.array(grades)
    return grades.mean(axis=0)

def get_version(file_name):
    '''
    Считывает версию (автоматически созданные синсеты) в словарь вида
    {gID : set(words)}
    '''
    version = {}
    with open(file_name, encoding = 'utf8') as f:
        for line in f:
            gID, words = line.strip().split(';')
            version[gID] = set(words.split(','))
    return version

def align_version_with_gold(pure_synsets, version):
    '''
    Преобразовывает синсеты из золотого стандарта
    и созданные автоматиески в формат нужный для метода
    evaluate()
    '''
    return tuple((frozenset(pure_synsets[gID]), frozenset(version[gID])) for gID in pure_synsets)

def evaluate_version(file_name):
    '''
    Основной метод. Оценивает вашу версию чистых синсетов.
    Выдаёт средние Jaccard, precision, recall, F-score
    '''
    mapping, clusters = get_mapping_and_clusters()
    pure_synsets = get_data('Test_set.csv')
    version = get_version(file_name)
    return evaluate(align_version_with_gold(pure_synsets, version))

evaluate_version('version.csv')