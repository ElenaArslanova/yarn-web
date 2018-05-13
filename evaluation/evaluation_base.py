import numpy as np

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
        print(f'P = {P}, R = {R} for ideal {ideal} and version {version}')
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
        #print(scores)
        grades.append(scores)
    grades = np.array(grades)
    return grades.mean(axis=0)

# Просто игрушечный пример
results = (({1, 2, 3}, {2, 3}), ({4, 5}, {4, 5, 6, 7}))
evaluate(results)