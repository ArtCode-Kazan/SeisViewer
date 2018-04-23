import string
# https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-valuehttps://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
# https://stackoverflow.com/questions/2059564/python-sort-the-list

a='sdjownfuwncuibviowebvwjc jn u9ejcviwfuwdhwoeifh9w0efi -w9jfwfjfjd'

b=dict()
for char in list(a):
    if char not in list(string.ascii_lowercase):
        continue
    if char not in b:
        b[char]=0
    else:
        b[char]+=1

c=list()
for key, value in b.items():
    temp = [key,value]
    c.append(temp)

c.sort(key=lambda x: x[1],reverse=True)

for char,count in c:
    print('Char: {} Frequency: {}'.format(char,count))

