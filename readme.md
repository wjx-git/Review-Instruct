This is the repo for ACL2025 paper [Review-Instruct: A Review-Driven Multi-Turn Conversations Generation Method for Large Language Models](https://arxiv.org/abs/2505.11010).


## Review-Instruct


<p align="center">
  <img src="assets/ri.png" alt="Review Instruct" />
</p>

Review-Instruct, a novel framework that synthesizes multi-turn conversations through an iterative "Ask-Respond-Review" process involving three agent roles: a Candidate, multiple Reviewers, and a Chairman. 
The framework iteratively refines instructions by incorporating Reviewer feedback, enhancing dialogue diversity and difficulty.

## How to use the repository to run code

Prepare the environment:
1. Set up the environment using: conda env create -f env.yml
2. Activate the environment with: conda activate LLM_Eval
3. Make sure you have the environment variables listed in utils/api_utils.py

Before including any participants, make sure:
1. The participant's calling function is written in the "generate_response" function inside "utils/api_utils.py".


here is an example command:

```bash
python main.py
```


