import locale

try:
    result = locale.getdefaultlocale()
    print(f"locale.getdefaultlocale()返回: {result}")
    print(f"返回类型: {type(result)}")
    print(f"返回长度: {len(result)}")
    
    if len(result) == 1:
        print(f"只有一个返回值: {result[0]}")
    else:
        print(f"两个返回值: {result[0]}, {result[1]}")
except Exception as e:
    print(f"错误: {e}")