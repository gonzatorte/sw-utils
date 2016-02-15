from sw_utils.deep_dict import DeepDict

s = DeepDict()

s.set([1], 1)
s.set([1,2], 12)
s.set([1,2,3], 123)

assert s.get([1]) == 1
assert s.get([1,2]) == 12
assert s.get([1,2,3]) == 123

assert s.keys() == [[1],[1,2],[1,2,3]]

assert s.keys_where(lambda x: x == 1)[0].data['a'] == 1

assert s.keys_where(lambda x: x == 2)[0].data['a'] == 12
s.set([1,10,2], 'dd')
assert s.keys_where(lambda x: x == 2)[1].data['a'] == 'dd'

assert s.keys_where(lambda x: x == 3)[0].data['a'] == 123


s.set([1,2,3], 'abc')
assert s.get([1,2,3]) == 'abc'

s.set([11,21,31], 112131)
s.set([11], 11)
s.set([11,21,31], None)
assert s.get([11,21,31]) == None
assert s.get([11,21]) == None
assert s.get([11]) == 11

assert s.get([1]) == s[[1]]
assert s.get([1,2]) == s[[1,2]]
assert s.get([5]) == s[[5]]
assert s.get([5]) == s[5]
assert s.get(5) == s[5]

rr = s.serialize()
ss = DeepDict()
ss.deserialize(rr)
assert ss.get(['1']) == s.get([1])

# assert s[[1,2]][[3]] == s[[1]][[2,3]]
