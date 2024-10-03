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


class Subtask_Agent:
    EXPERT_AGENT_PROMPT = """作为一个对犯罪{aspect}定义清晰的司法专家，请根据下述信息判断{criminals}是否构成{false_charge}罪的{aspect}。
    规则说明:
    {aspect_rule}
    [Note]:{insight}
    [Knowledge]
    {knowledge}
    案件事实:
    {fact}\n\n
    请仔细查看案件和规则，仅基于{aspect}资格的角度来分析，不必涉及其他构成要件的分析。请按照如下要求作答\n
    1.明确{aspect}的构成要件和规则的对应关系，请清楚地表达你的判定逻辑，并给出明确的结论答案：True、False（构成{false_charge}罪的{aspect}回答True，不构成回答False）。回答格式：[判案逻辑]+[答案]
    """

    def __init__(self, facts_list, insight_dict, decompose_strategy_dict, article_list):
        self.facts_list = facts_list
        self.insight_dict = insight_dict
        self.decompose_strategy_dict = decompose_strategy_dict
        self.article_list = article_list
        self.final_result = []
        self.error_li = []
        
    def evaluate_with_ask(self, data_item, flag, apikey, model_name, aspect, knowledge):
        try:
            charge_name = "true_charge" if flag == "positive" else "confusing_charge"
            false_charge = data_item[0][charge_name]
            criminals = data_item[1]['meta']['criminals']
            fact = data_item[1]['fact']
            aspect_rule = self.article_list[false_charge].split("\n")[self.decompose_strategy_dict[aspect][0]]
            insight = self.insight_dict[false_charge][self.decompose_strategy_dict[aspect][1]]
            
            prompt = self.EXPERT_AGENT_PROMPT.format(
                aspect=aspect,
                criminals=criminals,
                false_charge=false_charge,
                aspect_rule=aspect_rule,
                fact=fact,
                insight=insight,
                knowledge=knowledge
            )
            start_time = time.time()
            answer, cb = self.call_gpt(prompt, apikey, model_name)
            elapsed_time = time.time() - start_time 
            return answer, cb, elapsed_time
        except Exception as e:
            logging.error(f"Error in evaluate_with_ask: {e}")
            return False, False, False

