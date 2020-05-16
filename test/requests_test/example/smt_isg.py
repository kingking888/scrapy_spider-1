import ctypes
def bin2dec(string_num):
    return int(string_num, 2)
def shifting( string_num,num_r):
    base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'),ord('A')+6)]
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 2)
        mid.append(base[rem])
    temp = ''.join([str(x) for x in mid[::-1]])
    s1 = temp.zfill(32)
    s2 = s1[num_r:]+"0"*num_r
    s3 = bin2dec(s2)
    return s3
list1 = [0,3773236737,1568080888,1567949264,301240318,1,1,0,3086956040,0,0,0,0,0,0,186,508,90,127,0,0]
list2 = [2,2,4,4,4,1,1,4,4,3,2,2,2,2,2,1,2,1,1,1,1]
list_a = []
for i in range(len(list1)):
    num1 = list1[i]
    num2 = list2[i]
    list_l = []
    for j in range(num2):
        t_num = num1 & 255
        a = ctypes.c_int32(num1).value
        num1 = a >> 8
        list_l.append(t_num)
    list_a.extend(list_l[::-1])
print(list_a)
list_a = [0,
41,
123,
97,
93,
119,
17,
242,
93,
114,
18,
240,
172,
149,
183,
182,
1,
1,
192,
168,
7,
154,
164,
219,
59,
113,
0,
0,
64,
0,
11,
0,
1,
0,
0,
2,
3,
2,
14,
249,
1,
218,
90,
100,
0,
0
]
t = 0
for i in list_a:
    # i = ctypes.c_int32(i)
    i_l = shifting(t,5)
    t = i_l - t + i
    print(t)
