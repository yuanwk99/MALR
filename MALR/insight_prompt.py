Self_Reflector_PROMPT= """你是一个先进的法律推理agent，可以通过自我反思来分析错误回答，思考原因。

通过将规则拆分为4个方面，分别根据[案件事实]和4个方面的[规则说明]回答推理问题的尝试。
你错误地回答了该问题，我需要你根据你错误回答示例，并分析是在哪一个（或多个）方面判断有误。

[案件事实]{fact}

[问题描述]
分别依据主体<subject>,主观方面<mental>,客体<object>,客观方面<conduct>判断{criminals}是否构成{false_charge}罪的主体、主观方面、客体、客观方面？

[错误回答]
{initial_answer}

[真实结果]
{criminals}构成{false_charge}罪,因此不存在某个方面的结果为Fasle

[要求]
回答格式:
Aspect1: <ONLY the option word of the four aspects; not a complete sentence!>
Reason1: <ONLY the reason why Aspect1 you conclude error results in Chinese>
...
Select the error aspect, NOT all aspects are necessary to analyze.
"""

GET_INSIGHT_from_error_success_pair_PROMPT="""你是一个先进的法律推理agent，可以通过自我反思来提升自我。
我将给你一个之前通过给定的[规则说明]和[案件事实]回答推理问题的尝试。
下面是一个法律问题，有一个错误回答，有一个正确回答，请用一句话强调最关键的task-level判断要素，不要出现具体人名。

这是示例:
[规则说明]
{rule}

[案件事实]
{fact}

[相关问题]
{criminals}是否构成{charge}罪的{element}?

[错误回答]
{false_trial}

[正确回答]
{true_trial}

[输出格式]
如果xx，则不符合{charge}罪的{element}要求。
"""

GET_INSIGHT_from_success_exp_PROMPT="""你是一个先进的法律推理agent，可以通过自我反思来提升自我。
下面是根据[案件事实]和[规则说明]回答的问题，并且全部都正确回答。请用一句话强调2个罪名最关键的element判断的要素。

[案件事实]
{fact}

[规则说明1]
{rule1}

[相关问题1]
{criminals}是否构成{true_charge}罪?

[正确回答1]
{answer1}

[规则说明2]
{rule2}

[相关问题2]
{criminals}是否构成{false_charge}罪?

[正确回答2]
{answer2}

[[输出格式]
insight:如果[条件]，则不符合{true_charge}罪的<最关键的element>要求。
<最关键的element>从['主体', '主观方面','客体', '客观方面']选取
要求：生成的非常容易理解、简洁
对比两个罪名的规则，[条件]尽量参照{false_charge}罪罪名的条件生成
"""

INSIGHT_FILTER_PROMPT = """
You are an insight filtering who can filter the insights in the rule-insight knowledge base.
[Insights knowledge base]
{insight_from_knowledge_base}

[Requirement]
1. Check the correctness for insights
2. Filter and remove duplicate insights
3. Don’t change the original expression of any insights
4. Return the same json format as [Insights knowledge base]
"""