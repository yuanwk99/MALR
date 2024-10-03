import os
import logging
import time
import pandas as pd
import openai
import requests
import json
from tqdm import tqdm
from utils.dataloader import load_data,load_rule
from utils.model import call_gpt

class LegalExpertAssistant:
    EXPERT_CHECHER_PROMPT = """Please form a key question according to the [insight] and [case fact].
    [Start of Eaxmlpes]
    [case 1]
    [insight]
    如果主体是国家工作人员，则不符合挪用资金罪的主体要求
    [案件事实]
    福建省将乐县人民检察院指控，2014年12月29日，被告人肖某甲利用担任中国农业银行股份有限公司将乐金溪支行客户经理的职务便利...
    [问题]
    肖某甲是否构成挪用资金罪的主体？
    [Your response]
    S1:挪用资金罪的主体的审查：被告人肖某甲是中国农业银行股份有限公司将乐金溪支行客户经理
    S2:主体和insight的关系：如果主体是国家工作人员，则不符合挪用资金罪的主体要求
    S3:因此，形成的关键问题是：中国农业银行股份有限公司将乐金溪支行客户经理是国家工作人员吗？
    [End of Eaxmlpes]
    [Your turn]
    [insight]
    {insight}
    [案件事实]
    {fact}
    [问题]
    该案件是否构成{charge_name}罪的{aspect}？
    [Your response]
    """

    ASK_FARUI_EXPERT_PROMPT = """你是一个法律助手，请根据如下[Context Information]回答关键问题的答案。
    [Context Information]
    {Question}
    请给出该问题明确、简洁的的答案。
    """

    def __init__(self, article_list, insight_dict, decompose_strategy_dict):
        self.article_list = article_list
        self.insight_dict = insight_dict
        self.decompose_strategy_dict = decompose_strategy_dict

    def evaluate_with_ask(self, data_item, flag, apikey, model_name, aspect):
        try:
            charge_name = "true_charge" if flag == "positive" else "confusing_charge"
            false_charge = data_item[0][charge_name]
            criminals = data_item[1]['meta']['criminals']
            fact = data_item[1]['fact']
            aspect_rule = self.article_list[false_charge].split("\n")[self.decompose_strategy_dict[aspect][0]]
            insight = self.insight_dict[false_charge][self.decompose_strategy_dict[aspect][1]]

            question_prompt = self.EXPERT_CHECHER_PROMPT.format(
                aspect=aspect,
                charge_name=false_charge,
                insight=insight,
                fact=fact,
            )
            
            answer, cb, elapsed_time = call_gpt(question_prompt, apikey, model_name)
            return answer, cb, elapsed_time
        
        except Exception as e:
            logging.error(f"Error in evaluate_with_ask: {e}")
            return False, False, False
    
    def call_farui(self, prompt):
        post_body = {
            "model": 'farui-max-0403',
            "input": {
                "messages": [
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': prompt}
                ]
            },
            "parameters": {
                "enable_search": True,
                "top_p": 0.3,
                "repetition_penalty": 1.0
            },
            "stream": False
        }

        r = requests.post(
            url='your_legal_expert_api',
            headers={
                "Content-Type": "application/json",
                "X-DashScope-SSE": "enable",
                "Authorization": "Bearer " + "yourkey"
            },
            data=json.dumps(post_body)
        )

        return eval(r.text)['output']['text']   

    
    def get_answer_to_key_question(self,data_item, flag, apikey, model_name, aspect):
        question,_,_ = evaluate_with_ask(self, data_item, flag, apikey, model_name, aspect)
        answer_prompt = self.ASK_FARUI_EXPERT_PROMPT.format(Question=question)
        return self.call_farui(answer_prompt)

