#movies=["wanghuaiyu","xialiuyuan",["qianfengfeng","yeyajin",["shengmingming","tangmei"]]]
def print_list(lists):
    for each_item in lists:
        if(isinstance(each_item,list)):
            print_list(each_item)
        else:
            print(each_item)

