def seeif_nested(prospected_list):
    for each_lines in prospected_list:
        if not isinstance(each_lines,list):
            print (each_lines)
            
        else:
           seeif_nested(each_lines)



plist=["ram",["sam","jadu",["madu","luchi",["lalala"]]]]

seeif_nested(plist)
    
