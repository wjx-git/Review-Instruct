actions = ['<respond>', '<think>', '<criticize>', '<raise>']

init_user_input = 'initial user input:'


chairman_instruction = """This is an interview setting, and you, as the chair of the interview panel, are conducting an in-person interview. 
The candidate will strive to answer the questions you pose, and the panel members will evaluate the candidate’s responses based on usefulness, relevance, accuracy, depth, and creativity. Based on these evaluations, you need to pose new questions to deeply assess the candidate. 
Here are your action guidelines:
<think>: Gradually analyze each panel member’s comments. This is hidden from the candidate. Reflect only when necessary, and keep it concise.
<ask>: Summarize these comments and pose a potential follow-up question to deeply assess the candidate’s abilities. If most of the reviewers’ comments are positive, please raise a related field question based on the dialogue topic. If most of the reviewers’ comments suggest that the answers are insufficient or incorrect, please raise targeted questions based on these criticisms. The question should elicit a concise response and avoid excessive specificity or repetition. If no panel comments are provided, do not ask a question!
Strictly follow the action guidelines. Conduct the assessment in English unless otherwise necessary."""

candidate_instruction = """This is an interview setting, and you, as the candidate, are undergoing an in-person interview.
The interviewer will randomly ask questions, and you need to strive to provide the best possible answers. The interviewer will evaluate your responses based on usefulness, relevance, accuracy, depth, and creativity, and will ask new questions based on your answers to deeply assess you.
Here are your action guidelines:
<think>: Gradually think to analyze the question or plan your answer. This is hidden from the interviewer. Reflect only when necessary, and keep it concise.
<respond>: Respond to the user’s input as accurately as possible. Strictly follow the action guide"""

reviewer_instruction = """This is an interview setting, where you are a member of the interview panel conducting a live interview. The candidate will strive to answer the questions, and you will evaluate the candidate’s responses based on aspects such as usefulness, relevance, accuracy, depth, and creativity. 
Below is your action guide:
<think>: Gradually think through to analyze the problem or plan a response. This is hidden from the candidate. Only think when necessary, and keep it concise.
<criticize>: Criticize the inadequacies and flaws in the candidate’s answers.
Strictly follow the action guidelines. Conduct the assessment in English unless otherwise necessary"""

action_prompts = {
    '<respond>': "Action guide: only include <respond>. Use <think> if needed. Finish your whole response within 300 words, including <think>. ENCLOSE EACH ACTION IN ITS RESPECTIVE TAGS!\nOpponent’s Response or Question:",
    '<criticize>': "Action guide: only include <criticize>. Use <think> if needed. Finish your whole response within 300 words, including <think>. ENCLOSE EACH ACTION IN ITS RESPECTIVE TAGS!\nOpponent´s Response or Question:",
    '<raise>': "Action guide: only include <ask>. Use <think> if needed. Finish your whole response within 300 words, including <think>. ENCLOSE EACH ACTION IN ITS RESPECTIVE TAGS!\nComments from members of the committee:",
}

missing_actions_prompts = 'Only generate //ACTIONS_UNDONE//! ENCLOSE THEM IN TAGS!'


class Prompter:
    def __init__(self, lang='en'):
        self.lang = lang
        self.chairman_instruction = chairman_instruction
        self.candidate_instruction = candidate_instruction
        self.reviewer_instruction = reviewer_instruction
        self.init_user_input = init_user_input
        self.missing_actions_prompts = missing_actions_prompts
        
        self.actions = actions
        self.action_prompts = action_prompts
        
        self.word2token = 4/3
        self.word_limit_normal = 300
        self.word_limit_extra_space = 400 #for need_extra_space_cats
        self.judge_word_limit = 300 #for judge verdicts
    
    def get_qgen_prompt(self, domain, num):
        prompt = self.question_generation_instruction.replace('//NUM//', str(num)).replace('//DOMAIN//', domain).replace('//QGEN_COMMAND_DOMAIN//', self.qgen_command_dict[domain]).replace('//QGEN_EXAMPLE_DOMAIN//', self.qgen_example_dict[domain])
        return prompt
    
    def cats_in_language(self, cats):
        return cats
        
    def acts_in_language(self, acts):
        return acts