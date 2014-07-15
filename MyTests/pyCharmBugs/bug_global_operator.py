# pycharm shows, that all 'a' are the same
def f():
  def g():
    global a
    a = 3
  a = 1
  g()
  print(a)
f()