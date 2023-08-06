def print_list(mov_list):
            for each_item in mov_list:
                if isinstance(each_item, list):
                    print_list(each_item)
                else:
                        print(each_item)
