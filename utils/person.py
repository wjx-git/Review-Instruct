from utils.api_utils import generate_response
import re


class Person:
    def __init__(self, promptor, model_name):

        self.model_name = model_name
        self.promptor = promptor
        self.chat_history = []

    def add_history(self, role, content, action_guide=''):
        if action_guide:
            self.actions = self.promptor.acts_in_language(action_guide)
            action_guide_prompt = self.promptor.action_prompts['_'.join(action_guide)]
            # automatically append to chat history
            self.chat_history.append({"role": role, "content": f"{action_guide_prompt}\n{content}"})
        else:
            self.chat_history.append(
                {"role": role, "content": content}
            )

    def get_response(self, max_tokens):
        '''
        returns: 
            response (dict): {'original': str, 'no_thought': str, 'parsed': [(str, str)]}
        '''
        response = {}
        # generate response
        original_response = generate_response(self, self.chat_history, n=1, max_tokens=max_tokens)
        if original_response == '$ERROR$':
            raise Exception('Error in generating response')
        
        # parse response
        response['parsed'] = self.parse_response(original_response)
        response['no_thought'] = self.no_thought_content(response['parsed'])
        response['original'] = original_response

        # if actions in action guide is not done, try to generate them
        actions_done = [p[0] for p in response['parsed']]
        actions_undone = [a for a in self.actions if a not in actions_done]
        try_count = 0
        

        tmp_chat_history = self.chat_history.copy()
        while actions_undone != [] and try_count < 2:
            print('model: ', self.model_name, 'actions_undone:', actions_undone)
            tmp_chat_history.append({"role": "assistant",  "content": response['original']})

            # generate missing action prompt
            actions_undone = ', '.join(actions_undone)
            missing_action_prompt = self.promptor.missing_actions_prompts.replace('//ACTIONS_UNDONE//', actions_undone)
            tmp_chat_history.append({"role": "user",  "content": missing_action_prompt})
            
            # generate response
            new_response = generate_response(self, tmp_chat_history, n=1, max_tokens=max_tokens)
            
            # parse
            new_response_parsed = self.parse_response(new_response)
            for p in new_response_parsed:
                response['parsed'] = self.append_action_to_parsed_list(response['parsed'], p[0], p[1])

            response['original'] += new_response
            response['no_thought'] = self.no_thought_content(response['parsed'])
            
            # delete tmp history
            tmp_chat_history = tmp_chat_history[:-2]
            
            # update undone actions
            actions_done = [p[0] for p in response['parsed']]
            actions_undone = [a for a in self.actions if a not in actions_done]
            try_count += 1
        return response
    
    def append_action_to_parsed_list(self, parsed, action, content):
        # all actions (except think) should be used only once
        done_actions = [p[0] for p in parsed]
        if action not in done_actions or action == self.promptor.acts_in_language(['<think>'])[0]:
            # add to parsed
            parsed.append((action, content))
        else:
            # locate the last instance of the action
            for j in range(len(parsed)-1, -1, -1):
                if parsed[j][0] == action:
                    # replace it with the latest one
                    parsed[j] = (action, content)
                    break
        return parsed
    
    def reconstruct_response(self, parsed):
        response = ''
        for p in parsed:
            response += f'{p[0]}{p[1]}{p[0].replace("<", "</")}\n'
        return response

    def parse_response(self, response):
        # split response based on its respective tags
        split_actions = self.promptor.actions + [a.replace('<', '</') for a in self.promptor.actions]
        split_tags = '(' + '|'.join(split_actions) + ')'
        splitted = re.split(split_tags, response)
        parsed = []
        skip_next = False
        for i in range(len(splitted)):
            if skip_next:
                skip_next = False
                continue
            s = splitted[i]
            if s != '\n' and (any(c.isalpha() for c in s)): # contains letters
                if s in self.promptor.actions:
                    self.append_action_to_parsed_list(parsed, s, splitted[i+1])
                    skip_next = True
                # if it was not enclosed in tags, regard it as a response
                elif s not in [a.replace('<', '</') for a in self.promptor.actions]:
                    self.append_action_to_parsed_list(parsed, self.promptor.acts_in_language(['<respond>'])[0], s)
        return parsed
    
    def no_thought_content(self, parsed):
        no_thought = ''
        for p in parsed:
            # don't see criticism because it might give away hints, think of criticism as a form of thought
            if p[0] in self.promptor.acts_in_language(['<respond>', '<raise>']):
                no_thought += f'{p[0]}{p[1]}{p[0].replace("<", "</")}\n'
        return no_thought
    
    def reformat_parsed(self, parsed):
        reformatted = ''
        for p in parsed:
            reformatted += f'{p[0]}{p[1]}{p[0].replace("<", "</")}\n'
        return reformatted
    

class Chairman(Person):
    def __init__(self, promptor, model_name):
        super().__init__(promptor, model_name)
        self.chat_history = [{"role": "system", "content":self.promptor.chairman_instruction}]
        self.actions = self.promptor.acts_in_language(['<respond>'])

   
class Candidate(Person):
    def __init__(self, promptor, model_name):
        super().__init__(promptor, model_name)
        self.chat_history = [{"role": "system", "content":self.promptor.candidate_instruction}]
        self.actions = self.promptor.acts_in_language(['<respond>'])


class Reviewer(Person):
    def __init__(self, promptor, model_name):
        super().__init__(promptor, model_name)

        self.chat_history = [{"role": "system", "content":self.promptor.reviewer_instruction},
                            {"role": "user", "content": 'Dear Examiners, I am ready to answer the questions. Please proceed.'},
                            ]
        self.actions = self.promptor.acts_in_language(['<respond>'])
