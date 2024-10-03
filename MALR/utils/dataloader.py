import json

def load_data(path,type_):
    """
    path:./dataset/legal/CAIL-2018.txt -->CAIL Confusing
    data sample: [[{'confusing_charge'},{'true_charge'},{"fact":,"meta":{}}]]
    
    type_: ["legal"]
    """
    
    if type_ == "legal":
        # 读取数据集
        with open(path, 'r') as file:
            facts_list = file.readlines()
        facts_list = [eval(fact.strip()) for fact in facts_list]
    
    return facts_list

def load_rule(path, type_):
    if type_ == "legal":
        with open(path) as f:
            article_list = json.load(f)    
        for key in article_list.keys():
            article_list[key] =str(article_list[key]).replace(" ","").replace("{'定义':'","").replace("'}","").replace("','","\n").replace("'","")
            
    return article_list