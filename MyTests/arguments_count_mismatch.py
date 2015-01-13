# Good analizer must just check code, but not execute!
# The lines below is a simple test for this requirement
f = open('123','w')
f.write('bug!')
f.close()


# Test begin
def func(a, b, c, d):
    pass
    
func(1, 2, 3)


