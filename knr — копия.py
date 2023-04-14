import os

file = open('names.txt', 'w', encoding='utf-8')
works = os.listdir()
file.write('\n'.join(works))
for i, w in enumerate(works):
    if '.doc' in w:
        os.rename(w, str(i)+'.'+w.split('.')[-1])


