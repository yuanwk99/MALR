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

class AutoPlanner:
    AUTO_PLANNER_PROMPT = """You are currently in the task planning stage. 
    Break the rule and case facts down into multi-dimensional sub-steps.
    [规则说明]
    {rule}
    [案件事实]
    {fact}
    
    - Each action MUST have a unique ID, which is strictly increasing.
    - Ensure the plan maximizes parallelizability.
    - Never explain the actions with comments."""

    PREFIX = """- return a dict list,like {
        "Identify_the_Subject": {
            "ID": 1,
            "sub_steps": [
                "Determine if the subject is an employee of a company, enterprise, or other units."
            ]
        },
        "xx":{},}"""

    SUB_STEP_PROMPT = """
    Count the occurrences of each element in multiple lists, but it's important to note that some elements, although they have different names, may have similar meanings and should be considered the same.
        
    {li}

    Requirements：
    1. Identify similar elements, such as 'Evaluate_the_Object' and 'Evaluate_Object_of_Crime' should be treated as the same.
    2. Generate a new two-dimensional list and modify the original list to include similarly named elements.
    3. There's no need to produce code; just provide the final result.
    
    [Output format]
    only return: new two-dimensional list
    [[xx,xx,xx],[xx,xx,xx]]
    """

    def __init__(self, demo_list, api_keys):
        self.demo_list = demo_list
        self.api_keys = api_keys
        self.plans = []

    def get_demonstration(self, index):
        charge = 'true_charge'
        charge_name = self.demo_list[index][0][charge]
        fact = self.demo_list[index][1]['fact']
        criminals = self.demo_list[index][1]['meta']['criminals'][0]
        return charge_name, fact, criminals

    def plan_generation(self):
        for index in range(0,2):  # Processing just the first item for now
            charge_name, fact, criminals = self.get_demonstration(index)
            rule = article_list[charge_name]  # Assuming article_list is defined elsewhere
            prompt = self.AUTO_PLANNER_PROMPT.format(fact=fact, rule=rule) + self.PREFIX
            content, cb = call_gpt(prompt, apikey=self.api_keys[0], model_name="gpt-4-0125-preview")
            self.plans.append(content)
            # logging.info("*****\n" + content + "\n\n*****\n")

    def process_plans(self):
        term_counts = {}
        sub_steps = []
        for plan in tqdm(self.plans):
            print(plan)
            sub_step = [list(eval(plan.replace("```json", "").replace("```", "").strip()).keys())]
            sub_steps.append(sub_step)
            
            
            
        prompt = self.SUB_STEP_PROMPT.format(li=sub_steps)
        content, _ = call_gpt(p=prompt, apikey=self.api_keys[0], model_name="gpt-4-0125-preview")
        print(content)
        try:
            new_data = eval(content.replace("```json", "").replace("```python", "").replace("```", "").strip())
        except:
            content,_ = call_gpt(p="extract the new list, just return python list format\n"+content, apikey=self.api_keys[0], model_name="gpt-4-0125-preview")
            print(content)
            new_data = eval(content.replace("```json", "").replace("```python", "").replace("```", "").strip())
            print(new_data)
            
            with open('./output/auto-planner/new_data.txt', 'w', encoding='utf-8') as f:
                 for item in new_data:
                        f.write(str(item) + '\n')

        # Count occurrences of each unique term/concept
        for lst in new_data:
            for term in lst:
                term_counts[term] = term_counts.get(term, 0) + 1
        print("term_counts:\n",term_counts)
        return term_counts

    def summarize_terms(self, term_counts):
        threshold = 32 * 0.8
        for term, count in term_counts.items():
            if count >= threshold:
                print(term)

    def execute(self):
        self.plan_generation()
        term_counts = self.process_plans()
        self.summarize_terms(term_counts)
        
def main():
    # Load the training dataset
    demo_list = load_data(path="./dataset/legal/facts-sample-trainset.txt", type_='legal')
    
    # Assume there's a key for OpenAI API
    openai_api_keys = openai_api_key_li  # Assign your API keys accordingly

    auto_planner = AutoPlanner(demo_list, openai_api_keys)
    auto_planner.execute()

if __name__ == "__main__":
    main()